"""utils/google_sheet.py"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

COLUMNS = ["日期", "食材", "天數", "單次份量", "喜好度", "食用後狀況", "食物照片", "排便照片"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource(ttl=0)
def _get_credentials():
    return Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )


def _get_sheet():
    creds = _get_credentials()
    client = gspread.authorize(creds)
    sheet_name = st.secrets.get("sheet", {}).get("name", "baby_food_record")
    ws = client.open(sheet_name).sheet1
    if ws.row_count == 0 or not ws.row_values(1):
        ws.append_row(COLUMNS)
    return ws


def _upload_to_drive(file_bytes: bytes, filename: str, mime_type: str) -> str:
    """上傳檔案到 Google Drive，回傳公開瀏覽連結。"""
    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)

    folder_id = st.secrets.get("sheet", {}).get("drive_folder_id", None)
    metadata = {"name": filename}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type)
    file = service.files().create(
        body=metadata,
        media_body=media,
        fields="id",
    ).execute()

    file_id = file.get("id")

    # 設定公開讀取權限
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"


def get_all_records() -> list[dict]:
    return _get_sheet().get_all_records()


def append_record(
    date_str: str,
    food: str,
    day: int,
    amount,
    preference: int | None,
    note: str,
    food_photo_url: str = "",
    poop_photo_url: str = "",
) -> None:
    ws = _get_sheet()
    row = [
        date_str,
        food.strip(),
        int(day),
        amount,
        preference if preference is not None else "",
        note.strip(),
        food_photo_url,
        poop_photo_url,
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")


def upload_photo(uploaded_file, prefix: str) -> str:
    """接收 st.file_uploader 的物件，上傳並回傳連結。"""
    if uploaded_file is None:
        return ""
    filename = f"{prefix}_{uploaded_file.name}"
    return _upload_to_drive(
        file_bytes=uploaded_file.read(),
        filename=filename,
        mime_type=uploaded_file.type,
    )


def update_record(row_index: int, data: dict) -> None:
    ws = _get_sheet()
    header = ws.row_values(1)
    updates = []
    for col_name, value in data.items():
        if col_name in header:
            col_num = header.index(col_name) + 1
            updates.append({
                "range": gspread.utils.rowcol_to_a1(row_index, col_num),
                "values": [[value]],
            })
    if updates:
        ws.batch_update(updates)


def delete_record(row_index: int) -> None:
    _get_sheet().delete_rows(row_index)
