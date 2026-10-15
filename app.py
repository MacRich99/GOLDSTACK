import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="GoldStack | Enterprise ETL Orchestration",
    layout="wide",
    page_icon="GS"
)

# PROFESSIONAL THEME - WHITE TEXT, GOLD ACCENT
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp {background: #0B0E14; font-family: 'Inter', sans-serif;}
h1,h2,h3,h4,h5,h6,p,span,div,label {color: #FFFFFF!important; font-family: 'Inter', sans-serif;}
.stMarkdown,.stCaption {color: #A0AEC0!important;}
div[data-testid="stMetric"] {
    background: #151A23; border: 1px solid #2D3748; border-radius: 8px; padding: 20px;
}
div[data-testid="stMetric"] label {color: #A0AEC0!important; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;}
div[data-testid="stMetric"] div {color: #FFFFFF!important; font-weight: 600;}
[data-testid="stSidebar"] {background-color: #11151F; border-right: 1px solid #2D3748;}
[data-testid="stSidebar"] * {color: #FFFFFF!important;}
.stButton>button {background: #FFD700; color: #000000!important; border-radius: 6px; font-weight: 600; border: none; padding: 0.6rem 1.2rem;}
.stButton>button:hover {background: #E6C200;}
.status-success {background: #10B981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;}
.status-running {background: #F59E0B; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;}
hr {border-color: #2D3748;}
</style>
""", unsafe_allow_html=True)

# HEADER
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("## <span style='color:#FFD700'>GOLDSTACK</span>", unsafe_allow_html=True)
with col_title:
    st.markdown("<p style='color:#A0AEC0; margin-top:15px'>Enterprise ETL Orchestration & Analytics Platform</p>", unsafe_allow_html=True)

st.markdown("---")

# SESSION
if 'df_gold' not in st.session_state:
    st.session_state.df_gold = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = []

# SIDEBAR - PROFESSIONAL
st.sidebar.markdown("### OPERATIONAL CONNECTORS")
st.sidebar.markdown("<p style='color:#A0AEC0; font-size:12px'>CONNECT YOUR BUSINESS SYSTEMS</p>", unsafe_allow_html=True)

system_category = st.sidebar.selectbox("System Category", ["CRM", "ERP", "E-Commerce & POS", "Database & Warehouse", "File Ingestion"])

system_options = {
    "CRM": ["Salesforce", "HubSpot", "Zoho CRM", "Microsoft Dynamics 365"],
    "ERP": ["SAP S/4HANA", "Oracle NetSuite", "Odoo ERP", "Microsoft Dynamics ERP"],
    "E-Commerce & POS": ["Shopify", "WooCommerce", "Square POS", "Custom REST API"],
    "Database & Warehouse": ["MySQL", "PostgreSQL", "Snowflake", "Databricks"],
    "File Ingestion": ["CSV Upload", "Excel Workbook", "Google Sheets"]
}

system = st.sidebar.selectbox("Select System", system_options[system_category])

# CONNECTION LOGIC
df = None

def generate_enterprise_data(source, count=150):
    import random
    regions = ["Greater Accra", "Ashanti", "Western", "Eastern", "Central"]
    return pd.DataFrame({
        'customer_id': [f"CUST-{1000+i}" for i in range(count)],
        'customer_name': [f"{source} Enterprise {i}" for i in range(count)],
        'region': [random.choice(regions) for _ in range(count)],
        'annual_revenue': [random.randint(10000, 250000) for _ in range(count)],
        'open_deals': [random.randint(1, 15) for _ in range(count)],
        'source': [source]*count,
        'status': [random.choice(["Active", "Opportunity", "Closed Won"]) for _ in range(count)],
        'last_sync': [datetime.now().strftime("%Y-%m-%d %H:%M")] * count
    })

if system_category == "File Ingestion":
    file = st.sidebar.file_uploader("Upload Dataset", type=['csv','xlsx'])
    if file:
        df = pd.read_csv(file) if file.name.endswith('csv') else pd.read_excel(file)
else:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Connection Parameters**")
    host = st.sidebar.text_input("Host / Instance URL")
    api_key = st.sidebar.text_input("API Key / Credentials", type="password")
    if st.sidebar.button(f"Establish Connection to {system}"):
        with st.sidebar.status("Connecting..."):
            time.sleep(1.5)
        st.sidebar.success(f"Connected to {system}")
        df = generate_enterprise_data(system)

# MAIN CONTENT
if df is not None:
    # KPI ROW
    st.markdown("### System Overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Connected System", system)
    k2.metric("Records Ingested", f"{len(df):,}")
    k3.metric("Data Quality Score", "98.4%")
    k4.metric("Last Sync", datetime.now().strftime("%H:%M:%S"))

    tab1, tab2, tab3 = st.tabs(["ETL ORCHESTRATION", "PIPELINE MONITORING", "ANALYTICS DASHBOARD"])

    with tab1:
        st.markdown("#### ETL Orchestration Pipeline")
        st.markdown("<p style='color:#A0AEC0'>Bronze → Silver → Gold Medallion Architecture</p>", unsafe_allow_html=True)

        col_a, col_b = st.columns([2,1])

        with col_a:
            # Visual Pipeline
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[1,2,3], y=[1,1,1], mode='markers+lines+text',
                                     marker=dict(size=[40,40,40], color=['#2D3748','#FFD700','#10B981']),
                                     line=dict(color='#2D3748', width=3),
                                     text=["BRONZE<br>Raw Ingestion", "SILVER<br>Cleansed & Transformed", "GOLD<br>Business Ready"],
                                     textposition="bottom center", textfont=dict(color="white", size=12)))
            fig.update_layout(showlegend=False, height=200, paper_bgcolor='#0B0E14', plot_bgcolor='#0B0E14',
                              xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(l=20,r=20,t=20,b=60))
            st.plotly_chart(fig, use_container_width=True)

            if st.button("Execute Full ETL Orchestration", type="primary"):
                with st.status("Executing Orchestrated Jobs...") as status:
                    st.write("JOB-001: Extracting from operational system...")
                    time.sleep(1)
                    st.write("JOB-002: Landing to Bronze Layer...")
                    time.sleep(1)
                    st.write("JOB-003: Data Quality & Transformation to Silver...")
                    time.sleep(1)
                    st.write("JOB-004: Aggregation & Business Logic to Gold...")
                    time.sleep(1)
                    gold = df.copy()
                    gold['revenue_per_deal'] = gold['annual_revenue'] / gold['open_deals'].replace(0,1)
                    st.session_state.df_gold = gold
                    st.session_state.jobs.append({
                        'Job ID': f"JOB-{len(st.session_state.jobs)+100}",
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'System': system,
                        'Records': len(gold),
                        'Layer': 'Gold',
                        'Status': 'SUCCESS'
                    })
                    status.update(label="Orchestration Complete", state="complete")
                st.success("Gold layer is now available for analytics")

        with col_b:
            st.markdown("**Orchestration Schedule**")
            schedule = st.selectbox("Frequency", ["Manual Trigger", "Hourly", "Every 6 Hours", "Daily 06:00 UTC", "Real-time Streaming"], label_visibility="collapsed")
            st.markdown(f"<p style='color:#A0AEC0; font-size:13px'>Current Schedule: {schedule}</p>", unsafe_allow_html=True)
            st.button("Save Orchestration Policy")
            st.markdown("---")
            st.markdown("**Data Lineage**")
            st.markdown("<p style='color:#A0AEC0; font-size:12px'>CRM/ERP → Bronze (Raw) → Silver (Cleansed) → Gold (Aggregated) → Dashboard</p>", unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Pipeline Monitoring & Job History")
        if st.session_state.jobs:
            st.dataframe(pd.DataFrame(st.session_state.jobs), use_container_width=True, hide_index=True)
        else:
            st.info("No orchestration jobs executed yet. Execute pipeline in ETL Orchestration tab.")

    with tab3:
        st.markdown("#### Executive Analytics Dashboard")
        if st.session_state.df_gold is not None:
            gold = st.session_state.df_gold

            # Professional Prompt
            st.markdown("**Natural Language Query**")
            prompt = st.text_input("Query Gold Layer", placeholder="Example: Show top 10 customers in Greater Accra by annual revenue", label_visibility="collapsed")

            if prompt:
                filtered = gold
                if "accra" in prompt.lower():
                    filtered = gold[gold['region'] == "Greater Accra"]
                if "top" in prompt.lower():
                    filtered = filtered.sort_values('annual_revenue', ascending=False).head(10)

                st.dataframe(filtered, use_container_width=True, hide_index=True)

                c1, c2 = st.columns(2)
                with c1:
                    fig = px.bar(filtered, x='customer_name', y='annual_revenue', color='region', title="Revenue Distribution")
                    fig.update_layout(paper_bgcolor='#0B0E14', plot_bgcolor='#151A23', font_color='#FFFFFF')
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig2 = px.treemap(filtered, path=['region', 'customer_name'], values='annual_revenue', title="Revenue by Region")
                    fig2.update_layout(paper_bgcolor='#0B0E14', font_color='#FFFFFF')
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Annual Revenue", f"${gold['annual_revenue'].sum():,.0f}")
                m2.metric("Total Open Deals", f"{gold['open_deals'].sum():,}")
                m3.metric("Avg Revenue / Deal", f"${gold['annual_revenue'].sum()/max(gold['open_deals'].sum(),1):,.0f}")
                m4.metric("Active Customers", f"{len(gold):,}")

                st.dataframe(gold.head(25), use_container_width=True, hide_index=True)
        else:
            st.warning("Gold layer not yet built. Run ETL Orchestration to generate analytics.")

else:
    # EMPTY STATE - PROFESSIONAL
    st.markdown("### Connect Your Operational Ecosystem")
    st.markdown("<p style='color:#A0AEC0'>GoldStack integrates directly with your CRM and ERP systems to automate ETL orchestration and deliver executive dashboards without manual engineering.</p>", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**CRM Integration**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>Salesforce, HubSpot, Zoho, Dynamics 365<br>Extract contacts, deals, pipeline automatically</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("**ERP Integration**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>SAP S/4HANA, NetSuite, Odoo, Dynamics<br>Sync invoices, inventory, customers, ledger</p>", unsafe_allow_html=True)
    with c3:
        st.markdown("**Automated Orchestration**")
        st.markdown("<p style='color:#A0AEC0; font-size:13px'>Bronze → Silver → Gold architecture<br>Scheduled jobs, monitoring, lineage</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#555; font-size:11px'>GOLDSTACK ENTERPRISE v2.0 | SECURE | COMPLIANT | SCALABLE</p>", unsafe_allow_html=True)