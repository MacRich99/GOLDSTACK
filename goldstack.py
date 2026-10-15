import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="GoldStack - Auto", page_icon="⬢", layout="wide")

st.markdown("""
<style>
.stApp {background:#0A0A0A; color:#FFF}
[data-testid="stSidebar"] {background:#000; border-right:1px solid #222}
.prompt-box {background:#111; border:1px solid #D4AF37; border-radius:12px; padding:20px; margin-bottom:20px}
.kpi {background: linear-gradient(135deg,#111 0%,#1A1A1A 100%); border:1px solid #222; border-left:4px solid #D4AF37; border-radius:10px; padding:16px}
.kpi-label {color:#888; font-size:10px; letter-spacing:1.5px; text-transform:uppercase}
.kpi-value {color:#FFF; font-size:26px; font-weight:800}
.source {background:#D4AF37; color:#000; font-size:9px; padding:2px 8px; border-radius:20px; font-weight:800}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### <span style='color:#D4AF37'>⬢</span> GoldStack AUTO", unsafe_allow_html=True)
    st.caption("Prompt → Databricks Search → Tableau Auto")
    files = st.file_uploader("Upload CRM/ERP/POS", type=['csv','xlsx'], accept_multiple_files=True)
    st.divider()
    st.markdown("**Databricks (Search Only)**")
    DB_HOST = st.text_input("Host", placeholder="adb-xxx.azuredatabricks.net")
    DB_TOKEN = st.text_input("Token", type="password")
    DB_WARE = st.text_input("Warehouse ID")

# STATE
if 'gold_df' not in st.session_state:
    st.session_state.gold_df = pd.DataFrame()
if 'prompt_result' not in st.session_state:
    st.session_state.prompt_result = ""

if files:
    dfs=[]
    for f in files:
        try:
            df = pd.read_excel(f) if f.name.endswith('x') else pd.read_csv(f)
            dfs.append(df)
        except: pass
    if dfs:
        try:
            g = pd.concat(dfs, axis=1)
            g = g.loc[:,~g.columns.duplicated()]
        except:
            g = dfs[0]
        st.session_state.gold_df = g.drop_duplicates()

df = st.session_state.gold_df
if df.empty:
    df = pd.DataFrame({
        'customer_id':[f"AW00{i}" for i in range(11170,11178)],
        'customer_name':["Mason Roberts","Jose Flores","Nathan Johnson","Emma Smith","Liam Brown","Olivia Davis","Noah Miller","Ava Wilson"],
        'region':["Accra","Kumasi","Accra","Takoradi","Accra","Kumasi","Takoradi","Accra"],
        'revenue':[11176,11177,11178,14500,9800,12300,15600,11200],
        'orders':[5,2,8,4,6,3,9,2],
    })
    st.session_state.gold_df = df

# SAFE DATABRICKS SEARCH (READ ONLY)
def search_databricks(query, host, token, ware):
    if not host or not token or not ware:
        return None, "Demo Mode - Add Databricks creds for live search"
    blocked = ["DROP","DELETE","UPDATE","TRUNCATE","ALTER","CREATE","INSERT"]
    if any(b in query.upper() for b in blocked):
        return None, "BLOCKED - Only SEARCH allowed"
    # NL to SEARCH SQL
    q = query.lower()
    if "select" in q:
        sql = query
    elif "top" in q:
        sql = "SELECT * FROM workspace.gold.customers ORDER BY revenue DESC LIMIT 5"
    elif "accra" in q:
        sql = "SELECT * FROM workspace.gold.customers WHERE region ILIKE '%Accra%'"
    elif "revenue" in q and "region" in q:
        sql = "SELECT region, SUM(revenue) as total FROM workspace.gold.customers GROUP BY region"
    else:
        sql = "SELECT * FROM workspace.gold.customers LIMIT 20"

    try:
        url = f"https://{host}/api/2.0/sql/statements"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"statement": sql, "warehouse_id": ware, "wait_timeout":"10s"}
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        j = r.json()
        if 'result' in j and 'data_array' in j['result']:
            cols = [c['name'] for c in j['manifest']['schema']['columns']]
            return pd.DataFrame(j['result']['data_array'], columns=cols), sql
        return None, sql
    except Exception as e:
        return None, str(e)

# ========== STEP 1: PROMPT (SEARCH) ==========
st.markdown("## <span style='color:#D4AF37'>✦</span> Step 1: Prompt → Search GoldStack", unsafe_allow_html=True)

st.markdown('<div class="prompt-box">', unsafe_allow_html=True)
col1, col2 = st.columns([5,1])
with col1:
    prompt = st.text_input("Ask", placeholder="e.g. Show top 5 customers in Accra + build dashboard", label_visibility="collapsed")
with col2:
    go_btn = st.button("SEARCH & BUILD", type="primary", use_container_width=True)

q1,q2,q3,q4 = st.columns(4)
with q1:
    if st.button("Top 5 + Dashboard", use_container_width=True):
        prompt="Top 5 customers"; go_btn=True
with q2:
    if st.button("Accra + Dashboard", use_container_width=True):
        prompt="Customers in Accra"; go_btn=True
with q3:
    if st.button("Revenue by Region", use_container_width=True):
        prompt="Revenue by region"; go_btn=True
with q4:
    if st.button("Full Gold Dashboard", use_container_width=True):
        prompt="Full dashboard"; go_btn=True

st.markdown('</div>', unsafe_allow_html=True)

# Auto run prompt
filtered_df = st.session_state.gold_df
if go_btn and prompt:
    with st.spinner("Searching Databricks Gold Layer..."):
        result, sql = search_databricks(prompt, DB_HOST, DB_TOKEN, DB_WARE)
        st.markdown(f'<span class="source">DATABRICKS SEARCH</span> <code>{sql}</code>', unsafe_allow_html=True)
        if isinstance(result, pd.DataFrame) and not result.empty:
            filtered_df = result
            st.success(f"Found {len(result)} records from Databricks Gold - Auto-building Tableau dashboard below ↓")
            st.session_state.prompt_result = prompt
        else:
            # Local search
            q = prompt.lower()
            if "accra" in q:
                filtered_df = df[df['region'].astype(str).str.contains('Accra', case=False, na=False)]
            elif "top" in q:
                num = df.select_dtypes(include='number').columns[0]
                filtered_df = df.nlargest(5, num)
            st.info(f"Demo search: {len(filtered_df)} records for '{prompt}' - Building dashboard ↓")
            st.session_state.prompt_result = prompt

# ========== STEP 2: TABLEAU DASHBOARD (AUTO) ==========
st.markdown(f"## <span style='color:#D4AF37'>⬢</span> Step 2: Tableau Dashboard - Auto for '{st.session_state.prompt_result or 'All Gold'}'", unsafe_allow_html=True)

if not filtered_df.empty:
    num_col = filtered_df.select_dtypes(include='number').columns[0]

    # KPI
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Total Revenue</div><div class="kpi-value">${filtered_df[num_col].sum():,.0f}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Customers</div><div class="kpi-value">{len(filtered_df)}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Avg Value</div><div class="kpi-value">${filtered_df[num_col].mean():,.0f}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Source</div><div class="kpi-value" style="font-size:14px">Databricks Gold</div></div>', unsafe_allow_html=True)

    # Charts auto
    c1,c2 = st.columns([2,1])
    with c1:
        fig = px.bar(filtered_df.head(20), x=filtered_df.columns[1], y=num_col, color=num_col, color_continuous_scale=['#111','#D4AF37'], title=f"Auto Chart: {st.session_state.prompt_result}")
        fig.update_layout(paper_bgcolor='#111', plot_bgcolor='#111', font_color='#FFF', coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        group_col = 'region' if 'region' in filtered_df.columns else filtered_df.columns[1]
        fig2 = px.pie(filtered_df, names=group_col, values=num_col, hole=0.6, color_discrete_sequence=['#D4AF37','#FFF','#444'])
        fig2.update_layout(paper_bgcolor='#111', font_color='#FFF', title=f"Split by {group_col}")
        st.plotly_chart(fig2, use_container_width=True)

    # Gold Table
    st.markdown("### Gold Table (Prompt Result)")
    st.dataframe(filtered_df, use_container_width=True, height=350)
    st.download_button("⬇️ Export Gold CSV", filtered_df.to_csv(index=False), "GoldStack_Gold.csv", use_container_width=True)

st.divider()
st.caption("GoldStack AUTO • Prompt → Databricks Search (Read Only) → Tableau Auto • Gold #D4AF37")
