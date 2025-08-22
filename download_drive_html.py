import os
import json
import sys
import io
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ------------------------
# 配置服务账号
# ------------------------
service_account_info = os.environ.get("GDRIVE_SERVICE_ACCOUNT")
if not service_account_info:
    print("❌ GDRIVE_SERVICE_ACCOUNT not found")
    sys.exit(1)

service_account_info = json.loads(service_account_info)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# ------------------------
# 文件夹 ID
# ------------------------
FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
if not FOLDER_ID:
    print("❌ GDRIVE_FOLDER_ID not found")
    sys.exit(1)

# ------------------------
# 获取文件列表（HTML, TXT, Google Docs）
# ------------------------
def list_files(folder_id):
    query = f"'{folder_id}' in parents and (" \
            "mimeType='text/html' or " \
            "mimeType='text/plain' or " \
            "mimeType='application/vnd.google-apps.document')" 
    results = service.files().list(
        q=query,
        pageSize=1000,
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

# ------------------------
# 下载 HTML 文件
# ------------------------
def download_html_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    print(f"✅ Downloaded {file_name}")

# ------------------------
# 下载 TXT 文件并生成 HTML
# ------------------------
def download_txt_file(file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    text_content = fh.getvalue().decode('utf-8')
    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{file_name}</title></head><body><pre>{text_content}</pre></body></html>"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ TXT converted to HTML: {file_name}")

# ------------------------
# 导出 Google Docs 为 HTML
# ------------------------
def export_google_doc(file_id, file_name):
    request = service.files().export_media(fileId=file_id, mimeType='text/html')
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    print(f"✅ Exported Google Doc to HTML: {file_name}")

# ------------------------
# 主程序
# ------------------------
if __name__ == "__main__":
    files = list_files(FOLDER_ID)
    print("Found files:", [f['name'] for f in files])
    if not files:
        print("⚠️ No files found")
        sys.exit(0)

    safe_files = []
    for f in files:
        safe_name = f['name'].replace(" ", "-") + ".html"
        if f['mimeType'] == 'text/html':
            download_html_file(f['id'], safe_name)
        elif f['mimeType'] == 'text/plain':
            download_txt_file(f['id'], safe_name)
        else:
            export_google_doc(f['id'], safe_name)
        safe_files.append(safe_name)

    # ------------------------
    # 生成首页累积导航（Site Map）
    # ------------------------
    index_content = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Reading Glasses</title></head><body>\n"
    index_content += "<h1>Reading Glasses</h1>\n<ul>\n"
    for fname in safe_files:
        index_content += f'<li><a href="{fname}">{fname}</a></li>\n'
    index_content += "</ul>\n</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    print("✅ index.html (full site map) generated")

    # ------------------------
    # 每个页面底部随机内部链接（4~6 条）
    # ------------------------
    for fname in safe_files:
        with open(fname, "r", encoding="utf-8") as f:
            content = f.read()
        other_files = [x for x in safe_files if x != fname]
        num_links = min(len(other_files), random.randint(4, 6))
        random_links = random.sample(other_files, num_links)
        links_html = "<footer><ul>\n" + "\n".join([f'<li><a href="{x}">{x}</a></li>' for x in random_links]) + "\n</ul></footer>"
        content += links_html
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print("✅ Bottom random internal links updated (4~6 per page)")
