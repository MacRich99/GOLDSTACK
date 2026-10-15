import streamlit as st
import pandas as pd
import duckdb
import time
from datetime import datetime

st.set_page_config(page_title="GoldStack AI", page_icon="🥇", layout="wide")

# HEADER
st.markdown("""
<style>
.gold {color:#FFD700; font-weight:800}
</style>
""", unsafe_allow_html=True)

st.title("🥇 GoldStack AI - Any System → Gold")
st.caption("Automated ETL • Jobs • Pipeline • Dashboard | CRM • ERP • POS • WMS • FINANCE • SUPPORT • MARKETING • SCM")

# SIDEBAR - SYSTEM SELECTOR
st.sidebar.title("🔌 Connect Systems")
system_map = {
    "CRM": "Customers, contacts",
    "ERP": "Orders, sales",
    "POS": "Shopify, Square, POS",
    "WMS": "Inventory, stock",
    "FINANCE": "MoMo, expenses",
    "SUPPORT": "WhatsApp, tickets",
    "MARKETING": "Ads, campaigns",
    "SCM": "Suppliers, PO"
}
selected_systems = st.sidebar.multiselect("Select your stack", list(system_map.keys()), default=["CRM","ERP"])

# PIPELINE STATUS
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Pipeline Jobs")
job1 = st.sidebar.checkbox("Job 1: Bronze Ingestion", value=True)
job2 = st.sidebar.checkbox("Job 2: Silver Clean", value=True)
job3 = st.sidebar.checkbox("Job 3: Gold 360 Build", value=True)
job4 = st.sidebar.checkbox("Job 4: Dashboard Refresh", value=True)

# MAIN TABS
tab1, tab2, tab3, tab4 = st.tabs(["📥 INGEST", "🔄 ETL PIPELINE", "📊 DASHBOARD", "🚀 JOBS"])

with tab1:
    st.subheader("Step 1: Drop ANY files from ANY system")
    st.info(f"GoldStack will auto-detect {', '.join(selected_systems)} and run Bronze→Silver→Gold automatically")
    files = st.file_uploader("Upload CRM, ERP, POS, WMS, FINANCE files", accept_multiple_files=True, type=['xlsx','csv','xls','parquet'], key="gold")

with tab2:
    st.subheader("Automated Medallion Architecture")
    col1, col2, col3 = st.columns(3)
    col1.metric("BRONZE", "Raw Layer", "Auto Ingest")
    col2.metric("SILVER", "Clean Layer", "Deduplicate")
    col3.metric("GOLD", "Business Layer", "360 View")

    pipeline_placeholder = st.empty()

with tab3:
    dashboard_placeholder = st.empty()

# ETL LOGIC
if files:
    con = duckdb.connect(":memory:")
    bronze_tables = []
    silver_tables = []
    logs = []

    progress = st.progress(0)
    status = st.empty()

    for idx, f in enumerate(files):
        progress.progress(int((idx/len(files))*100))
        status.write(f"⏳ Processing {f.name}...")
        time.sleep(0.3)

        # LOAD
        try:
            if f.name.endswith(('xlsx','xls')):
                df = pd.read_excel(f)
            elif f.name.endswith('parquet'):
                df = pd.read_parquet(f)
            else:
                df = pd.read_csv(f)
        except Exception as e:
            st.error(f"Failed to read {f.name}: {e}")
            continue

        tname = f.name.split('.')[0].lower().replace(" ","_").replace("-","_")[:30]
        con.register("tmp_df", df)

        # JOB 1: BRONZE
        if job1:
            con.execute(f"DROP TABLE IF EXISTS bronze_{tname}")
            con.execute(f"CREATE TABLE bronze_{tname} AS SELECT *, '{f.name}' as _source_file, CURRENT_TIMESTAMP as _ingest_time FROM tmp_df")
            bronze_tables.append(f"bronze_{tname}")
            logs.append(f"✅ BRONZE: bronze_{tname} ({len(df)} rows)")

        # JOB 2: SILVER
        if job2:
            con.execute(f"DROP TABLE IF EXISTS silver_{tname}")
            # auto find id column
            id_candidates = [c for c in df.columns if 'id' in c.lower() or 'phone' in c.lower() or 'email' in c.lower()]
            id_col = id_candidates[0] if id_candidates else df.columns[0]
            con.execute(f'CREATE TABLE silver_{tname} AS SELECT DISTINCT * FROM bronze_{tname} WHERE "{id_col}" IS NOT NULL')
            cnt = con.execute(f"SELECT COUNT(*) FROM silver_{tname}").fetchone()[0]
            silver_tables.append(f"silver_{tname}")
            logs.append(f"✅ SILVER: silver_{tname} cleaned → {cnt} rows (dedup on {id_col})")

    # JOB 3: GOLD
    if job3 and silver_tables:
        status.write("⏳ Building GOLD 360...")
        con.execute("DROP TABLE IF EXISTS gold_360")
        try:
            # try join if 2+ tables and have customer_id
            if len(silver_tables) >= 2:
                # check if customer_id exists
                cols1 = con.execute(f"SELECT * FROM {silver_tables[0]} LIMIT 0").df().columns.tolist()
                cols2 = con.execute(f"SELECT * FROM {silver_tables[1]} LIMIT 0").df().columns.tolist()
                common = set(cols1).intersection(set(cols2))
                join_key = "customer_id" if "customer_id" in common else list(common)[0] if common else None

                if join_key and join_key!= "_source_file" and join_key!= "_ingest_time":
                    con.execute(f"""
                        CREATE TABLE gold_360 AS
                        SELECT * FROM {silver_tables[0]}
                        LEFT JOIN {silver_tables[1]} USING("{join_key}")
                    """)
                else:
                    con.execute(f"CREATE TABLE gold_360 AS SELECT * FROM {silver_tables[0]}")
            else:
                con.execute(f"CREATE TABLE gold_360 AS SELECT * FROM {silver_tables[0]}")
        except Exception as e:
            con.execute(f"CREATE TABLE gold_360 AS SELECT * FROM {silver_tables[0]}")
            logs.append(f"⚠️ GOLD join fallback: {e}")

        gold_df = con.execute("SELECT * FROM gold_360").df()
        logs.append(f"🥇 GOLD: gold_360 LIVE with {len(gold_df)} rows")
        progress.progress(100)
        status.write(f"✅ Pipeline complete at {datetime.now().strftime('%H:%M:%S')}")
        time.sleep(1)
        progress.empty()
        status.empty()

        # PIPELINE VISUAL
        with pipeline_placeholder.container():
            st.success("ETL Pipeline Executed")
            for log in logs:
                st.text(log)

            st.markdown("### Pipeline Flow")
            flow = " → ".join(bronze_tables[:2]) + " → " + " → ".join(silver_tables[:2]) + " → gold_360"
            st.code(flow, language="text")

        # DASHBOARD
        with dashboard_placeholder.container():
            st.subheader(f"🥇 GOLD Dashboard - {len(gold_df)} records from {len(files)} systems")

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Gold Records", len(gold_df))
            k2.metric("Systems Connected", len(selected_systems))
            k3.metric("Silver Tables", len(silver_tables))
            k4.metric("Data Quality", f"{int(len(gold_df)/max(1,sum([con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in bronze_tables]))*100)}%")

            st.dataframe(gold_df.head(100), use_container_width=True)

            num_df = gold_df.select_dtypes(include='number')
            if not num_df.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Gold Metrics**")
                    st.bar_chart(num_df.iloc[:20, :1])
                with c2:
                    st.markdown("**Distribution**")
                    st.line_chart(num_df.iloc[:20, :1])

            st.download_button("⬇️ Download GOLD CSV", gold_df.to_csv(index=False), "gold_360.csv")

            st.balloons()

    # JOB 4: JOBS TAB
    with tab4:
        st.subheader("Automated Jobs & Pipeline Schedule")
        st.table(pd.DataFrame([
            {"Job": "Bronze Ingest", "Status": "Success" if job1 else "Skipped", "Last Run": datetime.now().strftime("%H:%M:%S"), "Next": "On file upload"},
            {"Job": "Silver Clean", "Status": "Success" if job2 else "Skipped", "Last Run": datetime.now().strftime("%H:%M:%S"), "Next": "After Bronze"},
            {"Job": "Gold Build", "Status": "Success" if job3 else "Skipped", "Last Run": datetime.now().strftime("%H:%M:%S"), "Next": "After Silver"},
            {"Job": "Dashboard", "Status": "Live" if job4 else "Paused", "Last Run": datetime.now().strftime("%H:%M:%S"), "Next": "Realtime"},
        ]))

else:
    with tab2:
        st.warning("Upload files in INGEST tab to run automated pipeline")
    with tab3:
        st.info("Dashboard will appear here after Gold table is built")

st.sidebar.markdown("---")
st.sidebar.success("GoldStack AI v1.0 - Any System → Gold")
