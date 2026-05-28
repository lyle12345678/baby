"""
utils/google_sheet.py

封裝所有 Google Sheets API 操作。
設定方式：
  1. 於 Streamlit Cloud → Secrets 或 .streamlit/secrets.toml 填入：
       [gcp_service_account]
       type = "service_account"
       project_id = "your-project"
       private_key_id = "..."
       private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
       client_email = "your-sa@your-project.iam.gserviceaccount.com"
       ...

       [sheet]
       name = "baby_food_record"   # Google Sheet 檔名
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ── 欄位定義（順序與 Sheet 欄位一致）────────────────────────
COLUMNS = ["日期", "食材", "天數", "單次份量", "喜好度", "食用後狀況"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource(ttl=0)
def _get_client():
    """建立並快取 gspread client（使用 secrets.toml 中的 service account）。"""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def _get_sheet():
    """取得目標 worksheet（第一個工作表）。"""
    client = _get_client()
    sheet_name = st.secrets.get("sheet", {}).get("name", "baby_food_record")
    spreadsheet = client.open(sheet_name)
    ws = spreadsheet.sheet1

    # 若工作表是空的，自動建立標題列
    if ws.row_count == 0 or not ws.row_values(1):
        ws.append_row(COLUMNS)

    return ws


# ── Public API ────────────────────────────────────────────

def get_all_records() -> list[dict]:
    """讀取所有紀錄，回傳 list[dict]（key = 欄位名稱）。"""
    ws = _get_sheet()
    return ws.get_all_records()


def append_record(
    date_str: str,
    food: str,
    day: int,
    amount: str,
    preference: int | None,
    note: str,
) -> None:
    """新增一筆紀錄至 Google Sheet。"""
    ws = _get_sheet()
    row = [
        date_str,
        food.strip(),
        int(day),
        amount.strip(),
        preference if preference is not None else "",
        note.strip(),
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")


def update_record(row_index: int, data: dict) -> None:
    """更新第 row_index 列（1-based，含標題列故資料從第 2 列起）。
    data 為 {欄位名稱: 值} 的 dict。
    """
    ws = _get_sheet()
    header = ws.row_values(1)
    updates = []
    for col_name, value in data.items():
        if col_name in header:
            col_num = header.index(col_name) + 1  # 1-based
            updates.append({
                "range": gspread.utils.rowcol_to_a1(row_index, col_num),
                "values": [[value]],
            })
    if updates:
        ws.batch_update(updates)


def delete_record(row_index: int) -> None:
    """刪除第 row_index 列（1-based，含標題列）。"""
    ws = _get_sheet()
    ws.delete_rows(row_index)
