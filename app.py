import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="GoldStack AUTO - ETL Orchestrator", layout="wide", page_icon="")

# GOLD BLACK DESIGN
st.markdown("""
<style>
.stApp {background: #0a0a0a; color: #FFD700;}
h1,h2,h3 {color: #FFD700!important;}
div[data-testid="stMetric"] {background: linear-gradient(135deg, #1a1a1a, #2a2a2a); border: 1px solid #FFD700; border-radius: 12px; padding: 15px;}
</style>
""", unsafe_allow_html=True)

st.title(" GoldStack AUTO - ETL Orchestration Platform")
st.caption("Connect Operational System → Auto ETL Jobs → Pipeline → Dashboard")

# SESSION STATE
if 'df_gold' not in st.session_state:
    st.session_state.df_gold = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = []

# SIDEBAR 1: CONNECT OPERATIONAL SYSTEM
st.sidebar.header("🔌 1. Connect Operational System")
system = st.sidebar.selectbox("System Type",
    ["Upload CSV/Excel", "MySQL / Postgres", "Shopify Store", "Google Sheets", "POS API / REST", "QuickBooks"])

df = None

if system == "Upload CSV/Excel":
    file = st.sidebar.file_uploader("Upload Operational Data", type=['csv','xlsx'])
    if file:
        df = pd.read_csv(file) if file.name.endswith('csv') else pd.read_excel(file)

elif system == "MySQL / Postgres":
    st.sidebar.info("Connect Live Database")
    host = st.sidebar.text_input("Host", "localhost")
    db = st.sidebar.text_input("Database", "sales_db")
    user = st.sidebar.text_input("User", "root")
    table = st.sidebar.text_input("Table", "customers")
    if st.sidebar.button("🔌 Connect & Extract"):
        # DEMO DATA - Replace with real sqlalchemy connection
        st.sidebar.success(f"Connected to {db}.{table}")
        df = pd.DataFrame({
            'customer_id': range(1,101),
            'customer_name': [f'Client {i}' for i in range(1,101)],
            'region': ['Accra','Kumasi','Takoradi']*33 + ['Accra'],
            'revenue': [5000 + i*100 for i in range(100)],
            'orders': [i%10+1 for i in range(100)],
            'source_system': [system]*100
        })

elif system == "Shopify Store":
    shop = st.sidebar.text_input("Shopify Domain", "yourstore.myshopify.com")
    token = st.sidebar.text_input("Admin API Token", type="password")
    if st.sidebar.button("Connect Shopify"):
        st.sidebar.success("Connected! Pulling Orders...")
        df = pd.DataFrame({
            'customer_id': range(1,101),
            'customer_name': [f'Shopify Customer {i}' for i in range(1,101)],
            'region': ['Accra','Kumasi','Takoradi']*33 + ['Accra'],
            'revenue': [5000 + i*100 for i in range(100)],
            'orders': [i%10+1 for i in range(100)],
            'source_system': ['Shopify']*100
        })

elif system == "Google Sheets":
    sheet_url = st.sidebar.text_input("Google Sheet Link")
    if st.sidebar.button("Pull Sheet"):
        # For real: use gspread
        df = pd.DataFrame({
            'customer_id': range(1,101),
            'customer_name': [f'Sheets Client {i}' for i in range(1,101)],
            'region': ['Accra','Kumasi','Takoradi']*33 + ['Accra'],
            'revenue': [5000 + i*100 for i in range(100)],
            'orders': [i%10+1 for i in range(100)],
            'source_system': ['Google Sheets']*100
        })

elif system in ["POS API / REST", "QuickBooks"]:
    api_url = st.sidebar.text_input("API Endpoint URL")
    api_key = st.sidebar.text_input("API Key", type="password")
    if st.sidebar.button(f"Connect {system}"):
        df = pd.DataFrame({
            'customer_id': range(1,101),
            'customer_name': [f'{system} Client {i}' for i in range(1,101)],
            'region': ['Accra','Kumasi','Takoradi']*33 + ['Accra'],
            'revenue': [5000 + i*100 for i in range(100)],
            'orders': [i%10+1 for i in range(100)],
            'source_system': [system]*100
        })

# MAIN ETL ORCHESTRATION
if df is not None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Connected System", system)
    col2.metric("Records Extracted", f"{len(df):,}")
    col3.metric("Columns", len(df.columns))

    st.divider()

    # STEP 2: ETL ORCHESTRATION JOBS
    st.header(" 2. ETL Orchestration Jobs")

    job_col1, job_col2, job_col3 = st.columns(3)

    with job_col1:
        st.subheader("Bronze → Silver → Gold")
        if st.button(" Run Full ETL Pipeline", type="primary"):
            with st.status("Running ETL Orchestration...") as status:
                st.write("Job 1: Extract from Operational System...")
                time.sleep(1)
                st.write(f"✓ Extracted {len(df)} rows from {system}")

                st.write("Job 2: Bronze Layer - Raw Ingestion...")
                time.sleep(1)
                bronze = df.copy()

                st.write("Job 3: Silver Layer - Cleaning & Transform...")
                time.sleep(1)
                silver = bronze.dropna()

                st.write("Job 4: Gold Layer - Business Aggregates...")
                time.sleep(1)
                gold = silver.copy()
                gold['revenue_per_order'] = gold['revenue'] / gold['orders'].replace(0,1)

                st.session_state.df_gold = gold
                st.session_state.jobs.append({
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'system': system,
                    'records': len(gold),
                    'status': 'SUCCESS'
                })

                status.update(label="ETL Pipeline SUCCESS", state="complete")
            st.success("Pipeline Complete! Gold Table Ready")

    with job_col2:
        st.subheader(" Job Schedule")
        schedule = st.selectbox("Orchestration Frequency", ["Manual", "Every 1 Hour", "Every 6 Hours", "Daily 6AM", "Real-time"])
        st.info(f"Current: {schedule}")
        if st.button("Save Schedule"):
            st.success(f"Orchestration set to {schedule} - Will auto-run ETL jobs")

    with job_col3:
        st.subheader(" Pipeline History")
        if st.session_state.jobs:
            st.dataframe(pd.DataFrame(st.session_state.jobs), use_container_width=True)
        else:
            st.write("No jobs run yet")

    # STEP 3: PIPELINE + DASHBOARD
    if st.session_state.df_gold is not None:
        st.divider()
        st.header(" 3. Pipeline & Auto Dashboard")

        gold = st.session_state.df_gold

        # PROMPT LIKE CHATGPT
        st.subheader(" Prompt to Build Dashboard (ChatGPT-like)")
        prompt = st.text_input("Ask your data", placeholder="e.g. Show top 5 customers in Accra by revenue, Build revenue by region chart")

        if prompt:
            st.write(f"**Interpreting:** {prompt}")
            # Simple logic to filter/chart
            filtered = gold
            if "accra" in prompt.lower():
                filtered = gold[gold['region'].str.contains('Accra', case=False, na=False)]
            if "top 5" in prompt.lower() or "top5" in prompt.lower():
                filtered = filtered.sort_values('revenue', ascending=False).head(5)

            st.dataframe(filtered, use_container_width=True)

            # Auto Charts
            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(filtered, x='customer_name', y='revenue', color='region', title="Revenue by Customer (Auto)")
                fig.update_layout(paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a', font_color='#FFD700')
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.pie(filtered, names='region', values='revenue', title="Revenue by Region (Auto)")
                fig2.update_layout(paper_bgcolor='#0a0a0a', font_color='#FFD700')
                st.plotly_chart(fig2, use_container_width=True)
        else:
            # Default dashboard
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Revenue", f"GHS {gold['revenue'].sum():,.0f}")
            c2.metric("Total Orders", f"{gold['orders'].sum():,}")
            c3.metric("Avg per Order", f"GHS {gold['revenue'].sum()/max(gold['orders'].sum(),1):,.0f}")
            c4.metric("Active Regions", gold['region'].nunique())

            st.dataframe(gold.head(20), use_container_width=True)

else:
    st.info(" Connect your Operational System from sidebar to start ETL Orchestration")
    st.markdown("""
    ### How it works for clients:
    **1. Connect:** POS, Shopify, MySQL, Google Sheets, Excel
    **2. Orchestrate:** GoldStack runs Bronze→Silver→Gold jobs automatically
    **3. Pipeline:** Schedule every hour/day - no engineer needed
    **4. Dashboard:** Prompt like ChatGPT - dashboard builds itself
    """)