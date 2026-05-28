import streamlit as st
from datetime import date
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.title("🍼 寶寶副食品紀錄")

def load_sheet():
    try:
        from utils.google_sheet import get_all_records
        return get_all_records()
    except Exception:
        return []

records   = load_sheet()
today_str = date.today().strftime("%Y/%m/%d")
today_records = [r for r in records if r.get("日期","") == date.today().isoformat()]

if today_records:
    st.success(f"✅ 今天已紀錄 **{len(today_records)}** 筆副食品")
else:
    st.warning(f"📝 今天（{today_str}）還沒有紀錄，記得記錄哦！")

st.divider()
st.subheader("📋 最近紀錄")

MOOD = {1:"😭", 2:"😟", 3:"😐", 4:"😊", 5:"😍"}

if records:
    for r in records[-5:][::-1]:
        pref  = r.get("喜好度", "")
        mood  = MOOD.get(int(pref), "") if str(pref).isdigit() else ""
        note  = str(r.get("食用後狀況", ""))
        note_display = f" ｜ {note[:20]}{'…' if len(note)>20 else ''}" if note else ""
        amount = r.get("單次份量", "-")
        st.markdown(
            f"**{r.get('食材','-')}**　{r.get('日期','-')}　"
            f"第 {r.get('天數','-')} 天　{amount} ml　"
            f"{mood}{note_display}"
        )
else:
    st.info("尚無紀錄，請至「新增紀錄」頁面開始記錄。")

if records:
    st.divider()
    st.caption(f"資料儲存於 Google Sheets｜共 {len(records)} 筆紀錄｜今日：{today_str}")
