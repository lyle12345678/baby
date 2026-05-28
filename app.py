import streamlit as st
from datetime import date, datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))

# ── 頁面設定 ──────────────────────────────────────────────
st.set_page_config(
    page_title="寶寶副食品紀錄",
    page_icon="🍼",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── 全域 CSS ──────────────────────────────────────────────
st.markdown("""
<style>
/* 手機優先：加大按鈕、字體 */
[data-testid="stButton"] button {
    width: 100%;
    padding: 0.6rem 1rem;
    font-size: 1rem;
    border-radius: 10px;
}
[data-testid="stSidebar"] {
    min-width: 220px;
}
h1 { font-size: 1.5rem !important; }
h2 { font-size: 1.2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── 工具函式 ──────────────────────────────────────────────
def load_sheet():
    """從 Google Sheets 讀取所有紀錄，回傳 list[dict]。
    若尚未設定憑證，回傳空清單（讓首頁仍可渲染）。
    """
    try:
        from utils.google_sheet import get_all_records
        return get_all_records()
    except Exception:
        return []


# ── 首頁內容 ──────────────────────────────────────────────
st.title("🍼 寶寶副食品紀錄")

records = load_sheet()
today_str = date.today().strftime("%Y/%m/%d")

# 今日紀錄提示
today_records = [r for r in records if r.get("日期", "").startswith(date.today().strftime("%Y"))]
# 更精確比對
today_records = [r for r in records if r.get("日期", "") == date.today().isoformat()]

if today_records:
    st.success(f"✅ 今天已紀錄 **{len(today_records)}** 筆副食品")
else:
    st.warning(f"📝 今天（{today_str}）還沒有紀錄，記得記錄哦！")

st.divider()

# ── 最近紀錄（最新 5 筆）─────────────────────────────────
st.subheader("📋 最近紀錄")

if records:
    recent = records[-5:][::-1]          # 取最後 5 筆，新的在前
    for r in recent:
        pref = r.get("喜好度", "")
        stars = "⭐" * int(pref) if str(pref).isdigit() else ""
        note  = r.get("食用後狀況", "")
        note_display = f" ｜ {note[:20]}{'…' if len(note) > 20 else ''}" if note else ""

        st.markdown(
            f"**{r.get('食材', '-')}**　"
            f"{r.get('日期', '-')}　"
            f"第 {r.get('天數', '-')} 天　"
            f"{r.get('單次份量', '-')}　"
            f"{stars}{note_display}"
        )
else:
    st.info("尚無紀錄，請至「新增紀錄」頁面開始記錄。")

st.divider()

# ── 快速新增按鈕 ──────────────────────────────────────────
st.info("👈 請使用左側選單切換頁面")


# ── 側邊欄選單說明 ────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍼 寶寶副食品")
    st.markdown("""
- 🏠 首頁
- ➕ 新增紀錄
- 📋 紀錄列表
- 📊 喜好分析
- ⚠️ 異常反應
- 📥 匯出資料
    """)
    st.divider()
    st.caption("資料儲存於 Google Sheets")
    st.caption(f"今日：{today_str}")
    if records:
        st.caption(f"共 {len(records)} 筆紀錄")
