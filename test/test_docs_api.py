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

def test_docs_list(token):
    url = "https://open.feishu.cn/open-apis/docs/v1/documents"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 10}
    response = requests.get(url, headers=headers, params=params)
    print(f"Docs列表请求状态码: {response.status_code}")
    print(f"Docs列表响应: {response.text[:500]}...")

def test_docs_search(token):
    url = "https://open.feishu.cn/open-apis/docs/api/search"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"keyword": "", "page_size": 10}
    response = requests.post(url, headers=headers, json=payload)
    print(f"\nDocs搜索请求状态码: {response.status_code}")
    print(f"Docs搜索响应: {response.text[:500]}...")

def test_folder_direct(token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token=Fa3BfRjRolhjyQdG5k4c72pSn8j&page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\n文件夹直接访问请求状态码: {response.status_code}")
    print(f"文件夹直接访问响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_docs_list(token)
        test_docs_search(token)
        test_folder_direct(token)