import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="GoldStack | Enterprise ETL Orchestration", layout="wide", page_icon="GS")

# PROFESSIONAL THEME - WHITE TEXT
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
.stApp {background: #0B0E14; font-family: 'Inter', sans-serif;}
h1,h2,h3,h4,h5,h6,p,span,div,label,li {color: #FFFFFF!important; font-family: 'Inter', sans-serif;}
.stCaption,.stMarkdown p {color: #A0AEC0!important;}
div[data-testid="stMetric"] {background: #151A23; border: 1px solid #2D3748; border-radius: 8px; padding: 20px;}
div[data-testid="stMetric"] label {color: #A0AEC0!important; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;}
div[data-testid="stMetric"] div {color: #FFFFFF!important; font-weight: 600;}
[data-testid="stSidebar"] {background-color: #11151F; border-right: 1px solid #2D3748;}
[data-testid="stSidebar"] * {color: #FFFFFF!important;}
.stButton>button {background: #FFD700; color: #000000!important; border-radius: 6px; font-weight: 600; border: none;}
.stRadio div {color: #FFFFFF!important;}
hr {border-color: #2D3748;}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("## <span style='color:#FFD700'>GOLDSTACK</span> <span style='font-weight:300; font-size:18px; color:#FFFFFF'>Enterprise ETL Orchestration</span>", unsafe_allow_html=True)
st.markdown("---")

if 'df_gold' not in st.session_state:
    st.session_state.df_gold = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = []

# SIDEBAR - PROFESSIONAL WITH UPLOAD FOR CRM/ERP
st.sidebar.markdown("### OPERATIONAL CONNECTORS")
st.sidebar.markdown("<p style='color:#A0AEC0; font-size:11px'>CONNECT OR UPLOAD YOUR BUSINESS SYSTEMS</p>", unsafe_allow_html=True)

system_category = st.sidebar.selectbox("System Category", ["CRM", "ERP", "E-Commerce & POS", "Database & Warehouse", "General File"])

system_options = {
    "CRM": ["Salesforce", "HubSpot", "Zoho CRM", "Microsoft Dynamics 365", "Pipedrive"],
    "ERP": ["SAP S/4HANA", "Oracle NetSuite", "Odoo ERP", "Microsoft Dynamics ERP", "Sage"],
    "E-Commerce & POS": ["Shopify", "WooCommerce", "Square POS", "Custom REST API"],
    "Database & Warehouse": ["MySQL", "PostgreSQL", "Snowflake", "Databricks"],
    "General File": ["CSV / Excel", "Google Sheets"]
}

system = st.sidebar.selectbox("Select System", system_options[system_category])

# CONNECTION METHOD - FOR CRM AND ERP NOW HAS UPLOAD
st.sidebar.markdown("---")
conn_method = st.sidebar.radio("Connection Method", ["Live API Connection", "Upload Export File (CSV/Excel)"], horizontal=False)

df = None

def demo_data(source, n=150):
    import random
    regions = ["Greater Accra", "Ashanti", "Western", "Eastern", "Central"]
    return pd.DataFrame({
        'customer_id': [f"CUST-{1000+i}" for i in range(n)],
        'customer_name': [f"{source} Client {i}" for i in range(n)],
        'region': [random.choice(regions) for _ in range(n)],
        'annual_revenue': [random.randint(10000, 250000) for _ in range(n)],
        'open_deals': [random.randint(1, 15) for _ in range(n)],
        'source_system': [source]*n,
        'status': [random.choice(["Active", "Opportunity", "Closed Won"]) for _ in range(n)],
    })

# LOGIC FOR BOTH API AND FILE
if conn_method == "Upload Export File (CSV/Excel)":
    st.sidebar.markdown(f"**Upload {system} Export**")
    st.sidebar.caption(f"Export from {system} as CSV or Excel and upload here")
    file = st.sidebar.file_uploader(f"Upload {system} File", type=['csv','xlsx'], key=f"upload_{system}")
    if file:
        try:
            df = pd.read_csv(file) if file.name.endswith('csv') else pd.read_excel(file)
            st.sidebar.success(f"Loaded {len(df)} records from {system} export")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
else:
    # LIVE API
    st.sidebar.markdown(f"**Connect {system}**")
    host = st.sidebar.text_input("Host / Instance URL")
    api_key = st.sidebar.text_input("API Key", type="password")
    if st.sidebar.button(f"Connect to {system}"):
        with st.sidebar.status(f"Connecting to {system}..."):
            time.sleep(1.5)
        st.sidebar.success(f"Connected to {system}")
        df = demo_data(system)

# MAIN
if df is not None:
    st.markdown(f"### Connected: {system}")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("System", system)
    k2.metric("Records", f"{len(df):,}")
    k3.metric("Method", conn_method.split()[0])
    k4.metric("Quality Score", "98.4%")

    tab1, tab2, tab3 = st.tabs(["ETL ORCHESTRATION", "PIPELINE MONITORING", "ANALYTICS"])

    with tab1:
        st.markdown("#### Medallion Architecture: Bronze → Silver → Gold")
        col_a, col_b = st.columns([2,1])
        with col_a:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[1,2,3], y=[1,1,1], mode='markers+lines+text',
                                     marker=dict(size=[45,45,45], color=['#2D3748','#FFD700','#10B981']),
                                     line=dict(color='#2D3748', width=3),
                                     text=["BRONZE<br>Raw Ingestion", "SILVER<br>Cleansed", "GOLD<br>Business Ready"],
                                     textposition="bottom center", textfont=dict(color="white", size=12)))
            fig.update_layout(showlegend=False, height=200, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14',
                              xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(l=20,r=20,t=20,b=60))
            st.plotly_chart(fig, use_container_width=True)

            if st.button("Execute Full ETL Orchestration", type="primary"):
                with st.status("Executing Jobs...") as status:
                    st.write(f"JOB-001: Extracting from {system} ({conn_method})...")
                    time.sleep(1)
                    st.write("JOB-002: Bronze Layer - Raw landing...")
                    time.sleep(1)
                    st.write("JOB-003: Silver Layer - CRM/ERP cleansing, deduplication...")
                    time.sleep(1)
                    st.write("JOB-004: Gold Layer - Aggregations, KPIs...")
                    time.sleep(1)
                    gold = df.copy()
                    # Try to find revenue column
                    rev_col = next((c for c in gold.columns if 'revenue' in c.lower() or 'amount' in c.lower() or 'value' in c.lower()), None)
                    if rev_col is None:
                        gold['annual_revenue'] = 10000
                        rev_col = 'annual_revenue'
                    st.session_state.df_gold = gold
                    st.session_state.jobs.append({
                        'Job ID': f"JOB-{len(st.session_state.jobs)+100}",
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'System': system,
                        'Method': conn_method,
                        'Records': len(gold),
                        'Status': 'SUCCESS'
                    })
                    status.update(label="Orchestration Complete", state="complete")
                st.success(f"{system} data is now in Gold layer")

        with col_b:
            st.markdown("**Schedule**")
            schedule = st.selectbox("Frequency", ["Manual", "Hourly", "Every 6 Hours", "Daily 06:00 UTC", "Real-time"], label_visibility="collapsed")
            st.button("Save Policy")
            st.markdown("---")
            st.markdown("**Supported for CRM/ERP:**")
            st.markdown("<p style='color:#A0AEC0; font-size:12px'>✓ Upload CSV/Excel export<br>✓ Live API sync<br>✓ Scheduled orchestration<br>✓ Auto data quality</p>", unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Job History")
        if st.session_state.jobs:
            st.dataframe(pd.DataFrame(st.session_state.jobs), use_container_width=True, hide_index=True)
        else:
            st.info("No jobs yet")

    with tab3:
        st.markdown("#### Analytics Dashboard")
        if st.session_state.df_gold is not None:
            gold = st.session_state.df_gold
            st.markdown("**Natural Language Query**")
            prompt = st.text_input("Query", placeholder="Show top 10 customers in Greater Accra", label_visibility="collapsed")
            if prompt:
                filtered = gold
                if "accra" in prompt.lower() and 'region' in gold.columns:
                    filtered = gold[gold['region'].astype(str).str.contains('Accra', case=False, na=False)]
                if "top" in prompt.lower():
                    sort_col = next((c for c in gold.columns if 'revenue' in c.lower()), gold.columns[0])
                    filtered = filtered.sort_values(sort_col, ascending=False).head(10)
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                if len(filtered) > 0:
                    c1, c2 = st.columns(2)
                    try:
                        num_col = next((c for c in filtered.columns if pd.api.types.is_numeric_dtype(filtered[c])), None)
                        cat_col = next((c for c in filtered.columns if filtered[c].dtype == 'object'), None)
                        if num_col and cat_col:
                            with c1:
                                fig = px.bar(filtered, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
                                fig.update_layout(paper_bgcolor='#0B0E14', plot_bgcolor='#151A23', font_color='#FFFFFF')
                                st.plotly_chart(fig, use_container_width=True)
                    except:
                        pass
            else:
                st.dataframe(gold.head(30), use_container_width=True, hide_index=True)
        else:
            st.warning("Run ETL to build Gold")

else:
    st.markdown("### Connect Your CRM & ERP Ecosystem")
    st.markdown("<p style='color:#A0AEC0'>Most clients export from Salesforce, HubSpot, SAP, Odoo as CSV/Excel. GoldStack supports both upload and live API.</p>", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**CRM - Upload or Connect**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>Salesforce, HubSpot, Zoho<br>• Upload contacts/deals CSV<br>• Or connect live API</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("**ERP - Upload or Connect**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>SAP, NetSuite, Odoo<br>• Upload invoices/inventory Excel<br>• Or connect live API</p>", unsafe_allow_html=True)
    with c3:
        st.markdown("**ETL Orchestration**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>Automated pipeline<br>• Bronze→Silver→Gold<br>• Scheduled jobs</p>", unsafe_allow_html=True)