# utils/data_loader.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import streamlit as st

def get_gsheet_data():
    scope = ["https://spreadsheets.google.com/feeds ", "https://www.googleapis.com/auth/drive "]
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

def save_gsheet_data(sheet, df):
    sheet.clear()
    sheet.update([list(map(str, df.columns))] + df.astype(str).values.tolist())
