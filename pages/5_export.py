"""pages/5_export.py — 匯出 CSV / Excel"""
import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="匯出資料", page_icon="📥", layout="centered")
st.title("📥 匯出資料")

try:
    from utils.google_sheet import get_all_records
    records = get_all_records()
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

if not records:
    st.info("尚無資料可匯出。")
    st.stop()

df = pd.DataFrame(records)
today = date.today().strftime("%Y%m%d")

st.markdown(f"目前共 **{len(df)}** 筆紀錄，匯出日期：`{date.today().isoformat()}`")
st.divider()

# ── CSV ───────────────────────────────────────────────────
csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="⬇️ 下載 CSV",
    data=csv_bytes,
    file_name=f"baby_food_{today}.csv",
    mime="text/csv",
    use_container_width=True,
)

st.write("")

# ── Excel ─────────────────────────────────────────────────
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="副食品紀錄")
xlsx_bytes = buffer.getvalue()

st.download_button(
    label="⬇️ 下載 Excel",
    data=xlsx_bytes,
    file_name=f"baby_food_{today}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.divider()
st.subheader("資料預覽")
st.dataframe(df, use_container_width=True, hide_index=True)
