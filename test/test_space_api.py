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

def test_space_list(token):
    url = "https://open.feishu.cn/open-apis/space/v1/spaces"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Space List请求状态码: {response.status_code}")
    print(f"Space List响应: {response.text}")

def test_space_folder(token, folder_token):
    url = f"https://open.feishu.cn/open-apis/space/v1/folders/{folder_token}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nSpace Folder请求状态码: {response.status_code}")
    print(f"Space Folder响应: {response.text}")

def test_space_nodes(token, folder_token):
    url = f"https://open.feishu.cn/open-apis/space/v1/folders/{folder_token}/nodes"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nSpace Nodes请求状态码: {response.status_code}")
    print(f"Space Nodes响应: {response.text}")

def test_search(token):
    url = "https://open.feishu.cn/open-apis/drive/search/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": "", "page_size": 10}
    response = requests.post(url, headers=headers, json=payload)
    print(f"\nSearch V1请求状态码: {response.status_code}")
    print(f"Search V1响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_space_list(token)
        test_space_folder(token, "Fa3BfRjRolhjyQdG5k4c72pSn8j")
        test_space_nodes(token, "Fa3BfRjRolhjyQdG5k4c72pSn8j")
        test_search(token)