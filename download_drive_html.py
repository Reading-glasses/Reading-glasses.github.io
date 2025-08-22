import os
import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# 从环境变量中读取 Service Account JSON（Base64 或 JSON 字符串）
service_account_info = os.getenv("GDRIVE_SERVICE_ACCOUNT")

if not service_account_info:
    print("❌ 没有找到环境变量 GDRIVE_SERVICE_ACCOUNT，请检查 GitHub Secrets 是否配置正确。")
    sys.exit(1)

try:
    # 解析 JSON
    service_account_info = json.loads(service_account_info)
except json.JSONDecodeError:
    print("❌ GDRIVE_SERVICE_ACCOUNT 格式错误，无法解析 JSON。")
    sys.exit(1)

# 初始化 Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

def download_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"⬇️ Download {file_name}: {int(status.progress() * 100)}%")
    print(f"✅ Download finished: {file_name}")

if __name__ == "__main__":
    # 用文件ID和文件名测试
    FILE_ID = os.getenv("GDRIVE_FILE_ID")  # GitHub Actions 里也可以设置
    FILE_NAME = os.getenv("GDRIVE_FILE_NAME", "downloaded.html")

    if not FILE_ID:
        print("❌ 缺少环境变量 GDRIVE_FILE_ID")
        sys.exit(1)

    download_file(FILE_ID, FILE_NAME)
