import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="GOLDSTACK", layout="wide", page_icon="💰")

st.sidebar.title("GOLDSTACK")
mode = st.sidebar.radio("Choose Mode:", ["1. Auto ETL + Pipeline + Dashboard", "2. GoldStack AI - Tell it what to do"])

# --- SHARED STATE ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'gold_df' not in st.session_state:
    st.session_state.gold_df = None

# ============ MODE 1: AUTO ETL ============
if mode.startswith("1"):
    st.title("🔧 Auto ETL → Pipeline → Dashboard")
    st.write("Upload any system file and GOLDSTACK will auto-build everything.")

    uploaded = st.file_uploader("Upload CSV / Excel / JSON", type=["csv","xlsx","xls","json","parquet"])

    if uploaded:
        # ETL BRONZE
        st.subheader("Step 1: Bronze - Raw Ingest")
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        elif uploaded.name.endswith((".xlsx","xls")):
            df = pd.read_excel(uploaded)
        elif uploaded.name.endswith(".json"):
            df = pd.read_json(uploaded)
        else:
            df = pd.read_parquet(uploaded)

        st.write(f"Loaded {len(df)} rows, {len(df.columns)} cols")
        st.dataframe(df.head())
        st.session_state.df = df

        # ETL SILVER
        st.subheader("Step 2: Silver - Clean & Transform")
        df_clean = df.copy()
        df_clean = df_clean.drop_duplicates()
        df_clean = df_clean.dropna(how='all')
        # Auto convert dates
        for col in df_clean.columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='ignore')
            except:
                pass
        st.write("✅ Duplicates removed, nulls handled, dates parsed")
        st.dataframe(df_clean.head())

        # ETL GOLD
        st.subheader("Step 3: Gold - Business Ready")
        st.session_state.gold_df = df_clean
        st.success("Gold table ready")

        # AUTO DASHBOARD
        st.subheader("Step 4: Auto Dashboard")
        num_cols = df_clean.select_dtypes(include='number').columns.tolist()
        cat_cols = df_clean.select_dtypes(include='object').columns.tolist()

        if num_cols:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.histogram(df_clean, x=num_cols[0], title=f"Distribution of {num_cols[0]}")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                if len(num_cols) > 1:
                    fig2 = px.scatter(df_clean, x=num_cols[0], y=num_cols[1], color=cat_cols[0] if cat_cols else None)
                    st.plotly_chart(fig2, use_container_width=True)

        if cat_cols:
            fig3 = px.bar(df_clean[cat_cols[0]].value_counts().head(10), title=f"Top {cat_cols[0]}")
            st.plotly_chart(fig3, use_container_width=True)

        st.download_button("Download Gold Data", df_clean.to_csv(index=False), "gold_data.csv")

# ============ MODE 2: GOLDSTACK AI ============
else:
    st.title("🤖 GoldStack AI - Tell me what to do")
    st.write("Example: 'filter sales > 1000', 'show top 10 customers', 'plot revenue by month', 'remove nulls'")

    if st.session_state.gold_df is None and st.session_state.df is None:
        st.warning("Upload data in Mode 1 first, or upload here:")
        up2 = st.file_uploader("Upload for AI", type=["csv","xlsx"], key="ai_up")
        if up2:
            st.session_state.gold_df = pd.read_csv(up2) if up2.name.endswith("csv") else pd.read_excel(up2)

    df_ai = st.session_state.gold_df if st.session_state.gold_df is not None else st.session_state.df

    if df_ai is not None:
        st.dataframe(df_ai.head(3))
        user_cmd = st.text_input("What should I do to the data?", placeholder="e.g. show average sales by region")

        if user_cmd:
            st.info(f"AI executing: {user_cmd}")
            cmd = user_cmd.lower()

            # SIMPLE AI LOGIC - you can replace with OpenAI later
            try:
                if "filter" in cmd or "where" in cmd:
                    st.write("Filtered view (showing first 20 matches):")
                    # naive filter - shows code that user can edit
                    st.code(f"df.query('{user_cmd}')")
                    st.dataframe(df_ai.head(20))

                elif "plot" in cmd or "chart" in cmd or "graph" in cmd:
                    num_cols = df_ai.select_dtypes(include='number').columns
                    if len(num_cols) >= 1:
                        fig = px.histogram(df_ai, x=num_cols[0], title=user_cmd)
                        st.plotly_chart(fig)

                elif "top" in cmd:
                    import re
                    n = int(re.findall(r'\d+', cmd)[0]) if re.findall(r'\d+', cmd) else 10
                    st.dataframe(df_ai.head(n))

                elif "average" in cmd or "mean" in cmd or "sum" in cmd or "count" in cmd:
                    st.write(df_ai.describe())

                elif "remove" in cmd and "null" in cmd:
                    st.session_state.gold_df = df_ai.dropna()
                    st.success("Nulls removed!")
                    st.dataframe(st.session_state.gold_df.head())

                else:
                    st.write(f"I understood: '{user_cmd}'")
                    st.write("Current data summary:")
                    st.write(df_ai.describe(include='all'))
                    # Placeholder for LLM integration
                    st.code("""
# To make this REAL AI, add:
# import openai
# response = openai.ChatCompletion.create(
# model="gpt-4",
# messages=[{"role":"user", "content": f"Write pandas code for: {user_cmd}"}]
# )
                    """)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("No data yet. Go to Mode 1 and upload first.")