import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="GoldStack - Tableau Edition", page_icon="⬢", layout="wide")

# GOLD BLACK WHITE THEME
st.markdown("""
<style>
.stApp {background:#0A0A0A; color:#FFFFFF}
[data-testid="stSidebar"] {background:#000000; border-right:1px solid #222}
.kpi {
 background: linear-gradient(135deg, #111 0%, #1A1A1A 100%);
 border:1px solid #222;
 border-left:4px solid #D4AF37;
 border-radius:10px; padding:16px;
}
.kpi-label {color:#888; font-size:10px; letter-spacing:1.5px; text-transform:uppercase}
.kpi-value {color:#FFF; font-size:28px; font-weight:800}
.kpi-delta {color:#D4AF37; font-size:12px}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### <span style='color:#D4AF37'>⬢</span> GoldStack AI", unsafe_allow_html=True)
    st.caption("TABLEAU EDITION")
    st.divider()
    st.markdown("**DATA SOURCE**")
    files = st.file_uploader("Drop CRM/ERP/POS files", type=['csv','xlsx','xls'], accept_multiple_files=True)
    st.divider()
    if st.button("↻ Refresh Gold"):
        st.rerun()
    st.markdown('<span style="color:#D4AF37">● LIVE</span> goldstack-prod', unsafe_allow_html=True)