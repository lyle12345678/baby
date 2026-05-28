"""pages/1_add_record.py — 新增副食品紀錄"""
import streamlit as st
from datetime import date
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="新增紀錄", page_icon="➕", layout="centered")

st.title("➕ 新增副食品紀錄")

with st.form("add_record_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        record_date = st.date_input("📅 日期 *", value=date.today())
    with col2:
        day_num = st.number_input("🔢 第幾天嘗試 *", min_value=1, max_value=365, value=1, step=1)

    food_name = st.text_input("🥕 食材名稱 *", placeholder="例如：紅蘿蔔泥")
    amount    = st.text_input("🥄 單次份量 *", placeholder="例如：15ml 或 2 湯匙")

    preference = st.slider(
        "⭐ 寶寶喜好度（1 ～ 5）",
        min_value=1, max_value=5, value=3,
        help="1 = 非常排斥，5 = 非常喜歡",
    )
    stars_preview = "⭐" * preference + "☆" * (5 - preference)
    st.caption(f"目前喜好度：{stars_preview}")

    note = st.text_area(
        "📝 食用後狀況（選填）",
        placeholder="例如：排便正常、無紅疹、略有脹氣……",
        height=100,
    )

    submitted = st.form_submit_button("💾 儲存紀錄", use_container_width=True, type="primary")

if submitted:
    # 驗證必填
    if not food_name.strip():
        st.error("請填寫食材名稱！")
        st.stop()
    if not amount.strip():
        st.error("請填寫單次份量！")
        st.stop()

    try:
        from utils.google_sheet import append_record
        append_record(
            date_str   = record_date.isoformat(),
            food       = food_name,
            day        = int(day_num),
            amount     = amount,
            preference = preference,
            note       = note,
        )
        st.success(f"✅ 已儲存「{food_name}」的第 {day_num} 天紀錄！")
        st.balloons()
    except Exception as e:
        st.error(f"儲存失敗：{e}")
        st.info("請確認 secrets.toml 設定與 Google Sheet 共用權限。")
