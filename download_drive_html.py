from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
import os

# 配置
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service-account.json'
FOLDER_ID = '1pNmeFFfs2Ti-Yw8gG6K_imVzNk1OzCTo'  # 替换成你的文件夹ID

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# 获取文件夹中文档
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name, mimeType)"
).execute()

files = results.get('files', [])

for f in files:
    if f['mimeType'] == 'application/vnd.google-apps.document':
        export_url = f"https://www.googleapis.com/drive/v3/files/{f['id']}/export?mimeType=text/html"
        headers = {"Authorization": f"Bearer {creds.token}"}
        r = requests.get(export_url, headers=headers)
        filename = f"{f['name'].replace(' ', '-')}.html"  # 空格替换为 -
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(r.text)
        print(f"Saved {filename}")
