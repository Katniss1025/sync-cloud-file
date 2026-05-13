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

def test_drive_files_with_parent(token, folder_token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/files?parent_token={folder_token}&page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Drive Files with parent_token请求状态码: {response.status_code}")
    print(f"Drive Files with parent_token响应: {response.text}")

def test_drive_v1_root(token):
    url = "https://open.feishu.cn/open-apis/drive/v1/files?page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nDrive Files Root请求状态码: {response.status_code}")
    print(f"Drive Files Root响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_drive_files_with_parent(token, "Fa3BfRjRolhjyQdG5k4c72pSn8j")
        test_drive_v1_root(token)