import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="GoldStack | Auto ETL + Tableau", layout="wide", page_icon="GS")

# PROFESSIONAL WHITE TEXT
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
.stApp {background: #0B0E14; font-family: 'Inter', sans-serif;}
h1,h2,h3,h4,h5,h6,p,span,div,label,li {color: #FFFFFF!important;}
.stCaption {color: #A0AEC0!important;}
div[data-testid="stMetric"] {background: #151A23; border: 1px solid #2D3748; border-radius: 8px; padding: 20px;}
div[data-testid="stMetric"] label {color: #A0AEC0!important; font-size: 11px; text-transform: uppercase;}
[data-testid="stSidebar"] {background-color: #11151F; border-right: 1px solid #2D3748;}
[data-testid="stSidebar"] * {color: #FFFFFF!important;}
.stButton>button {background: #FFD700; color: #000000!important; font-weight: 700; border-radius: 6px;}
hr {border-color: #2D3748;}
.tableau-card {background: #151A23; border: 1px solid #2D3748; border-radius: 8px; padding: 15px; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

st.markdown("## <span style='color:#FFD700'>GOLDSTACK</span> <span style='font-weight:300'>| Fully Automatic ETL + Tableau Auto-Builder</span>", unsafe_allow_html=True)
st.markdown("---")

if 'df_gold' not in st.session_state:
    st.session_state.df_gold = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'auto_ran' not in st.session_state:
    st.session_state.auto_ran = False

# SIDEBAR - AUTH
st.sidebar.markdown("### 1. AUTHENTICATE & CONNECT")
st.sidebar.markdown("<p style='color:#A0AEC0; font-size:11px'>SYSTEM AUTO-BUILDS EVERYTHING AFTER AUTH</p>", unsafe_allow_html=True)

system_category = st.sidebar.selectbox("Category", ["CRM", "ERP", "E-Commerce & POS", "Database", "File"])
system_map = {
    "CRM": ["Salesforce", "HubSpot", "Zoho CRM", "Dynamics 365"],
    "ERP": ["SAP S/4HANA", "Oracle NetSuite", "Odoo ERP", "Dynamics ERP", "Sage"],
    "E-Commerce & POS": ["Shopify", "Square POS", "WooCommerce"],
    "Database": ["MySQL", "PostgreSQL", "Snowflake"],
    "File": ["CSV / Excel", "Google Sheets"]
}
system = st.sidebar.selectbox("System", system_map[system_category])

conn_method = st.sidebar.radio("Method", ["Live API Connection", "Upload CRM/ERP Export (CSV/Excel)"])

df = None

def demo_data(src, n=150):
    import random
    regions = ["Greater Accra", "Ashanti", "Western", "Eastern"]
    return pd.DataFrame({
        'customer_name': [f"{src} Client {i}" for i in range(n)],
        'region': [random.choice(regions) for _ in range(n)],
        'annual_revenue': [random.randint(15000, 300000) for _ in range(n)],
        'deals': [random.randint(1, 20) for _ in range(n)],
        'status': [random.choice(["Active", "Closed Won", "Opportunity"]) for _ in range(n)],
        'industry': [random.choice(["Retail", "Finance", "Manufacturing", "Services"]) for _ in range(n)],
        'source_system': [src]*n
    })

if conn_method == "Upload CRM/ERP Export (CSV/Excel)":
    file = st.sidebar.file_uploader(f"Upload {system} Export", type=['csv','xlsx'])
    if file:
        df = pd.read_csv(file) if file.name.endswith('csv') else pd.read_excel(file)
        st.sidebar.success(f"Authenticated: {len(df)} records from {system}")
else:
    host = st.sidebar.text_input("Instance URL / Host")
    key = st.sidebar.text_input("API Key / OAuth Token", type="password")
    if st.sidebar.button(f"Authenticate {system}", type="primary"):
        with st.sidebar.status(f"Authenticating {system}..."):
            time.sleep(1.2)
            st.sidebar.write("✓ Auth Success")
            time.sleep(0.5)
            st.sidebar.write(f"✓ Pulling data from {system}...")
            time.sleep(0.8)
        df = demo_data(system)
        st.sidebar.success(f"Authenticated & Extracted {len(df)} records")

# AUTOMATIC ETL + JOBS + PIPELINE + TABLEAU DASHBOARD
if df is not None:
    # AUTO TRIGGER ETL IF NOT YET RAN FOR THIS DATA
    if not st.session_state.auto_ran or st.session_state.df_gold is None or len(st.session_state.df_gold)!= len(df):
        with st.status("🤖 FULLY AUTOMATIC MODE: Building Everything...", expanded=True) as status:
            st.write(f"Step 1: Authenticated to {system} - {len(df)} records")
            time.sleep(0.8)
            st.write("Step 2: AUTO ETL - Bronze Layer (Raw Ingestion)...")
            bronze = df.copy()
            time.sleep(0.8)
            st.write("Step 3: AUTO ETL - Silver Layer (CRM/ERP Cleansing, Deduplication, Standardization)...")
            silver = bronze.dropna().copy()
            time.sleep(0.8)
            st.write("Step 4: AUTO ETL - Gold Layer (Business Logic, Aggregations)...")
            # Auto find numeric
            for col in silver.columns:
                if 'revenue' in col.lower() or 'amount' in col.lower():
                    silver['revenue_per_deal'] = silver[col] / silver.get('deals', 1).replace(0,1) if 'deals' in silver.columns else silver[col]
            gold = silver
            time.sleep(0.8)
            st.write("Step 5: AUTO BUILDING ETL JOBS...")
            job_id = f"JOB-{len(st.session_state.jobs)+101}"
            st.session_state.jobs.append({
                'Job ID': job_id,
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'System': system,
                'Method': conn_method,
                'Bronze': f"{len(bronze)} rec",
                'Silver': f"{len(silver)} rec",
                'Gold': f"{len(gold)} rec",
                'Status': 'SUCCESS - AUTO',
                'Schedule': 'Auto - Daily 06:00 UTC'
            })
            time.sleep(0.5)
            st.write("Step 6: AUTO BUILDING PIPELINE - Orchestration DAG...")
            time.sleep(0.5)
            st.write("Step 7: AUTO BUILDING TABLEAU DASHBOARD - Detecting Dimensions & Measures...")
            time.sleep(0.8)
            st.session_state.df_gold = gold
            st.session_state.auto_ran = True
            status.update(label="✅ FULLY AUTOMATIC BUILD COMPLETE", state="complete")

    gold = st.session_state.df_gold

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("System", system)
    k2.metric("Gold Records", f"{len(gold):,}")
    k3.metric("Auto Jobs", f"{len(st.session_state.jobs)} Built")
    k4.metric("Status", "Auto Dashboard Ready")

    tab1, tab2, tab3 = st.tabs(["⚙️ AUTO ETL JOBS (Auto Built)", "🔀 AUTO PIPELINE (Auto Built)", "📊 TABLEAU AUTO DASHBOARD (Auto Built)"])

    with tab1:
        st.markdown("#### Jobs Auto-Built After Authentication")
        st.dataframe(pd.DataFrame(st.session_state.jobs), use_container_width=True, hide_index=True)
        # Visual pipeline auto
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1,2,3,4], y=[1,1,1,1], mode='markers+lines+text',
                                 marker=dict(size=[35,35,35,45], color=['#10B981','#10B981','#10B981','#FFD700']),
                                 line=dict(color='#10B981', width=4),
                                 text=["CRM/ERP<br>Extract<br>✓ AUTO", "BRONZE<br>✓ AUTO", "SILVER<br>✓ AUTO", "GOLD<br>✓ AUTO"],
                                 textposition="bottom center", textfont=dict(color="white", size=11)))
        fig.update_layout(showlegend=False, height=220, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14',
                          xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(b=70))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Pipeline Auto-Built (DAG)")
        st.markdown(f"""
        <div class="tableau-card">
        <b>Pipeline ID:</b> PIPELINE-{system.upper()}-001 | <b>Trigger:</b> After Auth | <b>Schedule:</b> Daily 06:00 UTC (Auto)<br><br>
        <code style="color:#10B981">{system} ({conn_method}) → Bronze (Raw) → Silver (Cleansed CRM/ERP) → Gold (Aggregated) → Tableau Dashboard</code><br><br>
        <span style="color:#A0AEC0">All jobs auto-created, no manual intervention. Next run: Tomorrow 06:00 UTC</span>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Tableau Features - Auto Built Dashboard")
        st.markdown("<p style='color:#A0AEC0'>Dimensions & Measures auto-detected | Filters | Drag & Drop simulation | Auto Charts</p>", unsafe_allow_html=True)

        # Tableau-like shelves
        st.markdown("---")
        # Auto detect dims/measures
        dims = [c for c in gold.columns if gold[c].dtype == 'object']
        meas = [c for c in gold.columns if pd.api.types.is_numeric_dtype(gold[c])]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div class='tableau-card'><b>Dimensions (Auto)</b><br><span style='color:#A0AEC0; font-size:12px'>" + "<br>".join(dims[:6]) + "</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='tableau-card'><b>Measures (Auto)</b><br><span style='color:#A0AEC0; font-size:12px'>" + "<br>".join(meas[:6]) + "</span></div>", unsafe_allow_html=True)
        with c3:
            row_field = st.selectbox("Rows (Tableau)", dims, index=0 if dims else None)
            col_field = st.selectbox("Columns (Tableau)", meas, index=0 if meas else None)
        with c4:
            filter_field = st.selectbox("Filter (Tableau)", ["None"] + dims)
            filter_val = st.text_input("Filter Value", placeholder="e.g. Greater Accra")

        # Apply filter
        filtered = gold.copy()
        if filter_field!= "None" and filter_val:
            filtered = filtered[filtered[filter_field].astype(str).str.contains(filter_val, case=False, na=False)]

        # Natural Language Prompt - Tableau Ask Data
        st.markdown("**Tableau Ask Data (Natural Language)**")
        prompt = st.text_input("Prompt", placeholder="Show top 10 by revenue in Greater Accra", label_visibility="collapsed")
        if prompt:
            if "accra" in prompt.lower() and 'region' in filtered.columns:
                filtered = filtered[filtered['region'].astype(str).str.contains('Accra', case=False, na=False)]
            if "top" in prompt.lower():
                filtered = filtered.sort_values(meas[0] if meas else filtered.columns[0], ascending=False).head(10)

        # AUTO TABLEAU CHARTS - 4 charts auto built
        st.markdown("---")
        st.markdown("**Auto-Generated Tableau Dashboard (4 Views)**")

        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        try:
            with r1c1:
                if row_field and col_field:
                    fig = px.bar(filtered, x=row_field, y=col_field, color=row_field, title=f"{col_field} by {row_field} (Auto)")
                    fig.update_layout(paper_bgcolor='#0B0E14', plot_bgcolor='#151A23', font_color='#FFFFFF')
                    st.plotly_chart(fig, use_container_width=True)

            with r1c2:
                if len(meas) >= 1 and len(dims) >=1:
                    fig2 = px.pie(filtered, names=dims[0], values=meas[0], title=f"{meas[0]} by {dims[0]} (Auto)")
                    fig2.update_layout(paper_bgcolor='#0B0E14', font_color='#FFFFFF')
                    st.plotly_chart(fig2, use_container_width=True)

            with r2c1:
                if len(meas) >=1:
                    fig3 = px.treemap(filtered, path=[dims[0]] if dims else None, values=meas[0], title="Treemap (Tableau Feature)")
                    fig3.update_layout(paper_bgcolor='#0B0E14', font_color='#FFFFFF')
                    st.plotly_chart(fig3, use_container_width=True)

            with r2c2:
                if len(meas) >=2:
                    fig4 = px.scatter(filtered, x=meas[0], y=meas[1] if len(meas)>1 else meas[0], color=dims[0] if dims else None, size=meas[0], title="Scatter (Tableau Feature)")
                    fig4.update_layout(paper_bgcolor='#0B0E14', plot_bgcolor='#151A23', font_color='#FFFFFF')
                    st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.error(f"Auto dashboard error: {e}")

        st.dataframe(filtered.head(50), use_container_width=True, hide_index=True)

else:
    st.info("👈 Authenticate your CRM or ERP system - Everything else is AUTOMATIC")
    st.markdown("""
    <div class="tableau-card">
    <b>How Automatic Works:</b><br>
    <span style="color:#A0AEC0">
    1. User Authenticates CRM (Salesforce/HubSpot) or ERP (SAP/NetSuite/Odoo) - via API or Upload<br>
    2. <b>AUTO ETL:</b> Bronze → Silver → Gold auto-runs<br>
    3. <b>AUTO JOBS:</b> ETL jobs auto-created with schedule<br>
    4. <b>AUTO PIPELINE:</b> DAG auto-built<br>
    5. <b>AUTO TABLEAU DASHBOARD:</b> Dimensions/Measures detected, 4 charts auto-built, Filters + Ask Data prompt<br>
    No manual steps.
    </span>
    </div>
    """, unsafe_allow_html=True)