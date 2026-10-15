import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="GoldStack AI - Prompt Brain", page_icon="✦", layout="wide")

st.markdown("""
<style>
.stApp {background:#0A0A0A; color:#FFF}
[data-testid="stSidebar"] {background:#000}
.prompt-main {background:#111; border:1px solid #222; border-left:4px solid #D4AF37; border-radius:12px; padding:20px}
.search-card {background:#000; border:1px solid #1A1A1A; border-radius:8px; padding:12px; margin:8px 0}
.source-tag {background:#D4AF37; color:#000; font-size:10px; padding:2px 8px; border-radius:20px; font-weight:800}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### <span style='color:#D4AF37'>✦</span> GoldStack Brain", unsafe_allow_html=True)
    st.caption("Prompt → Databricks + Google + Gold")
    st.divider()
    st.markdown("**1. Gold Data**")
    files = st.file_uploader("Upload CRM/ERP/POS", type=['csv','xlsx','xls'], accept_multiple_files=True, label_visibility="collapsed")

    st.divider()
    st.markdown("**2. Databricks Connection (Optional)**")
    db_host = st.text_input("Host", placeholder="adb-xxx.azuredatabricks.net")
    db_token = st.text_input("PAT Token", type="password")
    db_warehouse = st.text_input("Warehouse ID", placeholder="abc123")

    st.divider()
    st.markdown("**3. AI Key (Optional)**")
    openai_key = st.text_input("OpenAI / Groq Key", type="password", help="Leave empty for offline mode")

# SESSION GOLD
if 'gold_df' not in st.session_state:
    st.session_state.gold_df = pd.DataFrame()

if files:
    dfs=[]
    for f in files:
        try:
            df = pd.read_excel(f) if f.name.endswith(('xlsx','xls')) else pd.read_csv(f)
            dfs.append(df)
        except: pass
    if dfs:
        try:
            gold = pd.concat(dfs, axis=1)
            gold = gold.loc[:,~gold.columns.duplicated()]
        except:
            gold = dfs[0]
        st.session_state.gold_df = gold.drop_duplicates()

df = st.session_state.gold_df

# FUNCTIONS
def search_web(query):
    """Search DuckDuckGo + Wikipedia - No API key needed"""
    results=[]
    try:
        # DuckDuckGo Instant Answer
        r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json", timeout=5)
        data = r.json()
        if data.get('AbstractText'):
            results.append({"source":"DuckDuckGo", "title":data.get('Heading'), "text":data.get('AbstractText'), "url":data.get('AbstractURL')})
        for topic in data.get('RelatedTopics', [])[:3]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({"source":"Web", "title":topic.get('Text','')[:60], "text":topic.get('Text',''), "url":topic.get('FirstURL','')})
    except: pass

    try:
        # Wikipedia search
        r = requests.get(f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=2&format=json", timeout=5)
        data = r.json()
        for i in range(len(data[1])):
            results.append({"source":"Wikipedia", "title":data[1][i], "text":data[2][i], "url":data[3][i]})
    except: pass
    return results[:5]

def query_databricks(sql, host, token, warehouse):
    """Query Databricks SQL Warehouse"""
    if not host or not token or not warehouse:
        return None, "No Databricks credentials"
    try:
        url = f"https://{host}/api/2.0/sql/statements"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"statement": sql, "warehouse_id": warehouse, "wait_timeout": "10s"}
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        return r.json(), None
    except Exception as e:
        return None, str(e)

def query_gold_data(question, data_df):
    """Query local Gold Data with AI logic"""
    if data_df.empty:
        return "No Gold data uploaded yet.", pd.DataFrame()

    q = question.lower()
    num_col = data_df.select_dtypes(include='number').columns[0] if len(data_df.select_dtypes(include='number').columns)>0 else data_df.columns[0]
    obj_col = data_df.select_dtypes(include='object').columns[0] if len(data_df.select_dtypes(include='object').columns)>0 else data_df.columns[0]
    region_col = next((c for c in data_df.columns if 'region' in c.lower() or 'city' in c.lower()), obj_col)

    answer=""
    result=data_df.copy()

    if "top" in q:
        n=5
        for w in q.split():
            if w.isdigit(): n=int(w)
        result = data_df.nlargest(n, num_col)
        answer = f"Top {n} by {num_col}: ${result[num_col].sum():,.0f} total. " + ", ".join([f"{row[obj_col]}" for _,row in result.iterrows()])

    elif "accra" in q or "kumasi" in q or "region" in q:
        city = "Accra" if "accra" in q else "Kumasi" if "kumasi" in q else None
        if city:
            result = data_df[data_df[region_col].astype(str).str.contains(city, case=False, na=False)]
            answer = f"Found {len(result)} records in {city}, total ${result[num_col].sum():,.0f} revenue."
        else:
            result = data_df.groupby(region_col)[num_col].sum().reset_index()
            answer = f"Revenue by {region_col} calculated."

    elif "churn" in q or "duplicate" in q or "quality" in q or "invalid" in q:
        dups = data_df.duplicated().sum()
        nulls = data_df.isnull().sum().sum()
        answer = f"GOLD QUALITY: {len(data_df)} records, {dups} duplicates, {nulls} nulls. Quality Score: {100-dups/len(data_df)*100:.1f}%"

    elif "revenue" in q or "average" in q or "sum" in q:
        answer = f"Total Revenue: ${data_df[num_col].sum():,.0f}, Average: ${data_df[num_col].mean():,.0f}, Max: ${data_df[num_col].max():,.0f} from {len(data_df)} customers."

    else:
        answer = f"I analyzed {len(data_df)} Gold records. Columns: {', '.join(data_df.columns)}. Try: 'Top 5', 'Revenue by region', 'Accra customers', 'Quality check'."
        result = data_df.head(10)

    return answer, result

def ask_llm(question, context, api_key):
    """Call OpenAI / Groq if key provided"""
    if not api_key:
        return None
    try:
        # Try Groq / OpenAI compatible
        url = "https://api.groq.com/openai/v1/chat/completions" if "gsk_" in api_key else "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"}
        payload = {
            "model": "llama3-70b-8192" if "gsk_" in api_key else "gpt-4o-mini",
            "messages": [
                {"role":"system", "content": f"You are GoldStack AI. You have Gold data: {context}. Answer business questions. Be concise, gold/black theme expert."},
                {"role":"user", "content": question}
            ],
            "max_tokens": 400
        }
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"LLM Error: {e}"

# MAIN UI
st.markdown("## <span style='color:#D4AF37'>✦</span> GoldStack Prompt Brain", unsafe_allow_html=True)
st.caption("One prompt → Searches Gold Data + Databricks + Google + Wikipedia and builds answer")

st.markdown('<div class="prompt-main">', unsafe_allow_html=True)
col_in, col_btn = st.columns([5,1])
with col_in:
    user_q = st.text_input("Ask GoldStack", placeholder="e.g. Show me top 5 customers in Accra and explain churn trends + search best CRM practices", label_visibility="collapsed", key="main_q")
with col_btn:
    ask_btn = st.button("ASK GOLD", type="primary", use_container_width=True)

# Quick prompts
c1,c2,c3,c4 = st.columns(4)
quick = ""
with c1:
    if st.button("Top 5 + Market Trends", use_container_width=True): quick="Top 5 customers and search market trends for CRM"
with c2:
    if st.button("Accra Revenue + Search", use_container_width=True): quick="Revenue in Accra and search Ghana business trends"
with c3:
    if st.button("Quality + Best Practices", use_container_width=True): quick="Quality issues and search data quality best practices"
with c4:
    if st.button("Databricks Query: Gold", use_container_width=True): quick="SELECT * FROM gold.customers LIMIT 10"

if quick:
    user_q = quick
    ask_btn = True

st.markdown('</div>', unsafe_allow_html=True)

if ask_btn and user_q:
    st.divider()
    with st.spinner("✦ GoldStack is searching Gold + Databricks + Web..."):

        # 1. GOLD DATA
        st.markdown("### 1️⃣ Gold Data (Your CRM/ERP/POS)")
        gold_answer, gold_result = query_gold_data(user_q, df)
        st.success(f"**GoldStack AI:** {gold_answer}")
        if not gold_result.empty:
            st.dataframe(gold_result, use_container_width=True, height=250)

        # 2. DATABRICKS
        if "select" in user_q.lower() or "from" in user_q.lower():
            st.markdown("### 2️⃣ Databricks Lakehouse")
            if db_host and db_token and db_warehouse:
                res, err = query_databricks(user_q, db_host, db_token, db_warehouse)
                if err:
                    st.warning(f"Databricks: {err}")
                else:
                    st.json(res)
            else:
                st.warning("Add Databricks Host + Token + Warehouse in sidebar to run SQL live. Query detected: SQL")
                st.code(user_q, language="sql")
        else:
            st.markdown("### 2️⃣ Databricks (Auto)")
            if db_host:
                # auto query gold table
                sql = f"SELECT * FROM gold.customers LIMIT 5"
                res, err = query_databricks(sql, db_host, db_token, db_warehouse)
                if res:
                    st.write("Live Databricks result:")
                    st.json(res)

        # 3. WEB SEARCH
        st.markdown("### 3️⃣ Web Search (Google/DuckDuckGo/Wikipedia)")
        web_results = search_web(user_q)
        if web_results:
            for r in web_results:
                st.markdown(f'<div class="search-card"><span class="source-tag">{r["source"]}</span> <b>{r["title"]}</b><br><span style="color:#888; font-size:13px">{r["text"][:200]}...</span><br><a href="{r["url"]}" style="color:#D4AF37; font-size:12px">{r["url"]}</a></div>', unsafe_allow_html=True)
        else:
            st.caption("No web results")

        # 4. LLM FINAL BUILD
        st.markdown("### 4️⃣ Final Answer - Built from All Sources")
        context = f"Gold data has {len(df)} rows, columns {list(df.columns)[:5] if not df.empty else []}. Gold answer: {gold_answer}"
        if openai_key:
            llm_ans = ask_llm(user_q, context, openai_key)
            if llm_ans:
                st.markdown(f'<div style="background:#000; border:1px solid #D4AF37; border-radius:8px; padding:16px">{llm_ans}</div>', unsafe_allow_html=True)
        else:
            # Offline build
            final = f"""
            **Question:** {user_q}

            **Built from 3 sources:**
                        1. **Gold Data:** {gold_answer}
                        2. **Databricks:** {"Connected" if db_host else "Add credentials in sidebar to query live Lakehouse"}
                        3. **Web:** Found {len(web_results)} articles about '{user_q}'

            **Action:** Use Gold Table above, export to Power BI. Add OpenAI key in sidebar for GPT-4 synthesis.
            """
            st.info(final)

st.divider()
st.caption("GoldStack Prompt Brain • Searches Gold + Databricks SQL + Web and builds answer")