import requests

APP_ID = "cli_a97b0e12ec391bc4"
APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"
FOLDER_TOKEN = "Fa3BfRjRolhjyQdG5k4c72pSn8j"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result["tenant_access_token"]
    return None

def check_folder_permission(token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/files/{FOLDER_TOKEN}/permission/members"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"文件夹权限查询状态码: {response.status_code}")
    print(f"文件夹权限查询响应: {response.text}")

def list_all_drives(token):
    url = "https://open.feishu.cn/open-apis/drive/v1/drives"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nDrive列表请求状态码: {response.status_code}")
    print(f"Drive列表响应: {response.text}")

def get_drive_info(token, drive_id=""):
    if drive_id:
        url = f"https://open.feishu.cn/open-apis/drive/v1/drives/{drive_id}"
    else:
        url = "https://open.feishu.cn/open-apis/drive/v1/drives/me"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nDrive信息请求状态码: {response.status_code}")
    print(f"Drive信息响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        check_folder_permission(token)
        list_all_drives(token)
        get_drive_info(token)