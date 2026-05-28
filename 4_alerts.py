"""pages/4_alerts.py — 異常反應紀錄"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="異常反應", page_icon="⚠️", layout="centered")
st.title("⚠️ 異常反應紀錄")

ALERT_KEYWORDS = ["紅疹", "拉肚子", "便秘", "嘔吐", "脹氣"]

try:
    from utils.google_sheet import get_all_records
    records = get_all_records()
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

if not records:
    st.info("尚無任何紀錄。")
    st.stop()

df = pd.DataFrame(records)
df["_is_alert"] = df["食用後狀況"].apply(
    lambda x: any(k in str(x) for k in ALERT_KEYWORDS)
)
alerts = df[df["_is_alert"]].sort_values("日期", ascending=False).reset_index(drop=True)

if alerts.empty:
    st.success("🎉 目前沒有任何異常反應紀錄，寶寶很健康！")
    st.stop()

st.error(f"共偵測到 **{len(alerts)}** 筆異常反應紀錄")
st.caption(f"關鍵字：{' / '.join(ALERT_KEYWORDS)}")
st.divider()

for _, row in alerts.iterrows():
    note = str(row.get("食用後狀況", ""))
    matched = [k for k in ALERT_KEYWORDS if k in note]

    with st.container(border=True):
        st.markdown(f"### ⚠️ {row.get('食材', '-')}")
        st.caption(f"📅 {row.get('日期', '-')}　第 {row.get('天數', '-')} 天　份量：{row.get('單次份量', '-')}")
        cols = st.columns(len(matched)) if matched else [st]
        for c, kw in zip(cols, matched):
            c.error(kw)
        if note:
            st.info(f"📝 {note}")
