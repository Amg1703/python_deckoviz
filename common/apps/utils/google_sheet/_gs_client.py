import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime 
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleSheet:
    def __init__(self,sheet_name):
        if not sheet_name:
            raise ValueError("Sheet name is required.")
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_file(
            os.getenv("GS_CREDENTIALS"),
            scopes=self.scope
        )
        self.client = gspread.authorize(creds)
        self.sheet = self._get_or_create_sheet(sheet_name)
    
    def _get_or_create_sheet(self, sheet_name):
        try:
            return self.client.open(sheet_name).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = self.client.create(sheet_name)
            spreadsheet.share('vmscare747@gmail.com', perm_type='user', role='writer')
            return spreadsheet.sheet1

    def append_to_google_sheet(self,name,email):
        try:
            self.sheet.append_row([name,email,datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            print(self.sheet.url)
        except Exception as e:
            print(f"Error appending to Google Sheet: {e}")
