"""pages/3_analysis.py — 喜好分析圖表"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="喜好分析", page_icon="📊", layout="centered")
st.title("📊 喜好分析")

try:
    from utils.google_sheet import get_all_records
    records = get_all_records()
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

if not records:
    st.info("尚無資料可分析。")
    st.stop()

df = pd.DataFrame(records)
df["喜好度"] = pd.to_numeric(df["喜好度"], errors="coerce")
df["天數"]   = pd.to_numeric(df["天數"],   errors="coerce")

# ── 統計數字 ──────────────────────────────────────────────
total_records  = len(df)
unique_foods   = df["食材"].nunique()
avg_pref       = df["喜好度"].mean()
alert_kw       = ["紅疹", "拉肚子", "便秘", "嘔吐", "脹氣"]
alert_count    = df["食用後狀況"].apply(
    lambda x: any(k in str(x) for k in alert_kw)
).sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("總紀錄筆數",  f"{total_records} 筆")
col2.metric("嘗試食材種數", f"{unique_foods} 種")
col3.metric("平均喜好度",  f"{avg_pref:.1f} / 5" if pd.notna(avg_pref) else "－")
col4.metric("異常反應次數", f"{int(alert_count)} 次")

st.divider()

# ── 平均喜好度長條圖 ──────────────────────────────────────
st.subheader("食材平均喜好度")
avg_by_food = (
    df.dropna(subset=["喜好度"])
    .groupby("食材")["喜好度"]
    .mean()
    .reset_index()
    .rename(columns={"喜好度": "平均喜好度"})
    .sort_values("平均喜好度", ascending=False)
)

if not avg_by_food.empty:
    fig = px.bar(
        avg_by_food,
        x="食材", y="平均喜好度",
        color="平均喜好度",
        color_continuous_scale=["#F4C0D1", "#D4537E", "#72243E"],
        range_y=[0, 5],
        text_auto=".1f",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="", yaxis_title="平均喜好度",
        margin=dict(t=20, b=0),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 排名統計 ──────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("🥇 Top 5 喜愛食材")
    top5 = avg_by_food.head(5).reset_index(drop=True)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, row in top5.iterrows():
        st.markdown(f"{medals[i]} **{row['食材']}** — {row['平均喜好度']:.1f} ⭐")

with col_r:
    st.subheader("🍽️ 最常食用食材")
    most_used = (
        df.groupby("食材").size()
        .reset_index(name="次數")
        .sort_values("次數", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    for i, row in most_used.iterrows():
        st.markdown(f"**{row['食材']}** — {row['次數']} 次")

st.divider()
st.subheader("❌ 最低接受度食材")
bottom3 = avg_by_food.tail(3).iloc[::-1].reset_index(drop=True)
for _, row in bottom3.iterrows():
    st.markdown(f"**{row['食材']}** — {row['平均喜好度']:.1f} ⭐")
