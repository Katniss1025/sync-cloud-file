import requests

APP_ID = "cli_a97b0e12ec391bc4"
APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result["tenant_access_token"]
    return None

def test_explorer(token):
    url = "https://open.feishu.cn/open-apis/drive/explorer/v1/files/list"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"limit": 10}
    response = requests.post(url, headers=headers, json=payload)
    print(f"Explorer请求状态码: {response.status_code}")
    print(f"Explorer响应: {response.text}")

def test_get_folder_info(token, folder_token):
    url = f"https://open.feishu.cn/open-apis/drive/v2/files/{folder_token}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nFolder Info V2请求状态码: {response.status_code}")
    print(f"Folder Info V2响应: {response.text}")

def test_drive_files_v2(token, folder_token):
    url = f"https://open.feishu.cn/open-apis/drive/v2/files?folder_token={folder_token}&page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nDrive Files V2请求状态码: {response.status_code}")
    print(f"Drive Files V2响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_explorer(token)
        test_get_folder_info(token, "Fa3BfRjRolhjyQdG5k4c72pSn8j")
        test_drive_files_v2(token, "Fa3BfRjRolhjyQdG5k4c72pSn8j")