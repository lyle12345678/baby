"""pages/3_record_list.py — 紀錄列表、搜尋、刪除"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="紀錄列表", page_icon="📋", layout="centered")
st.title("📋 紀錄列表")

try:
    from utils.google_sheet import get_all_records, delete_record
    records = get_all_records()
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

if not records:
    st.info("尚無紀錄。請至「新增紀錄」頁面開始記錄。")
    st.stop()

df = pd.DataFrame(records)

# ── 篩選區 ────────────────────────────────────────────────
with st.expander("🔍 搜尋 / 篩選", expanded=True):
    search = st.text_input("食材關鍵字", placeholder="輸入食材名稱搜尋…")
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("開始日期", value=None)
    with col2:
        date_to   = st.date_input("結束日期", value=None)

filtered = df.copy()
if search:
    filtered = filtered[filtered["食材"].str.contains(search, na=False)]
if date_from:
    filtered = filtered[filtered["日期"] >= date_from.isoformat()]
if date_to:
    filtered = filtered[filtered["日期"] <= date_to.isoformat()]

filtered = filtered.sort_values("日期", ascending=False).reset_index(drop=True)

st.caption(f"顯示 {len(filtered)} / {len(df)} 筆紀錄")
st.divider()

# ── 列表顯示 ──────────────────────────────────────────────
ALERT_KEYWORDS = ["紅疹", "拉肚子", "便秘", "嘔吐", "脹氣"]
MOOD = {1:"😭", 2:"😟", 3:"😐", 4:"😊", 5:"😍"}

def drive_preview_url(url: str) -> str:
    """把 Drive 分享連結轉成可直接顯示的圖片網址。"""
    if not url:
        return ""
    if "/file/d/" in url:
        file_id = url.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
    return url

for idx, row in filtered.iterrows():
    note      = str(row.get("食用後狀況", ""))
    is_alert  = any(k in note for k in ALERT_KEYWORDS)
    pref      = row.get("喜好度", "")
    mood      = MOOD.get(int(pref), "") if str(pref).isdigit() else ""
    food_url  = drive_preview_url(str(row.get("食物照片", "")))
    poop_url  = drive_preview_url(str(row.get("排便照片", "")))

    with st.container(border=True):
        col_info, col_del = st.columns([5, 1])
        with col_info:
            header = f"**{row.get('食材', '-')}**　{mood}"
            if is_alert:
                header += "　⚠️"
            st.markdown(header)
            st.caption(
                f"📅 {row.get('日期', '-')}　"
                f"第 {row.get('天數', '-')} 天　"
                f"份量：{row.get('單次份量', '-')} ml"
            )
            if note:
                st.caption(f"📝 {note}")
        with col_del:
            if st.button("🗑️", key=f"del_{idx}", help="刪除"):
                try:
                    delete_record(idx + 2)
                    st.success("已刪除")
                    st.rerun()
                except Exception as e:
                    st.error(f"刪除失敗：{e}")

        # 照片預覽
        if food_url or poop_url:
            p1, p2 = st.columns(2)
            if food_url:
                with p1:
                    st.caption("🍱 食物照片")
                    st.image(food_url, use_container_width=True)
            if poop_url:
                with p2:
                    st.caption("💩 排便照片")
                    st.image(poop_url, use_container_width=True)
