import streamlit as st
from datetime import date
import sys, os
sys.path.append(os.path.dirname(__file__))

home_page    = st.Page("pages/1_home.py",        title="🏠 首頁",    default=True)
add_page     = st.Page("pages/2_add_record.py",  title="➕ 新增紀錄")
list_page    = st.Page("pages/3_record_list.py", title="📋 紀錄列表")
analysis_page= st.Page("pages/4_analysis.py",    title="📊 喜好分析")
alerts_page  = st.Page("pages/5_alerts.py",      title="⚠️ 異常反應")
export_page  = st.Page("pages/6_export.py",      title="📥 匯出資料")

pg = st.navigation([home_page, add_page, list_page, analysis_page, alerts_page, export_page])
st.set_page_config(page_title="寶寶副食品紀錄", page_icon="🍼", layout="centered")
pg.run()
