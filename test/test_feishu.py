import requests

APP_ID = "cli_a97b0e12ec391bc4"
APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"
FOLDER_TOKEN = "Fa3BfRjRolhjyQdG5k4c72pSn8j"
APP_TOKEN = "ANlPblTwhaVlausMjpucnb3an7M"
TABLE_ID = "tblew6g53b1wWWNK"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    print(f"Token请求状态码: {response.status_code}")
    print(f"Token响应: {response.text}")
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result["tenant_access_token"]
    return None

def test_drive_api(token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={FOLDER_TOKEN}&page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nDrive API请求状态码: {response.status_code}")
    print(f"Drive API响应: {response.text}")

def test_bitable_api(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nBitable API请求状态码: {response.status_code}")
    print(f"Bitable API响应: {response.text}")

def test_folder_info(token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/folders/{FOLDER_TOKEN}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nFolder Info请求状态码: {response.status_code}")
    print(f"Folder Info响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"\n获取到Token: {token[:20]}...")
        test_drive_api(token)
        test_bitable_api(token)
        test_folder_info(token)