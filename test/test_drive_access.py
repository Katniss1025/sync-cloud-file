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

def test_my_drive(token):
    url = "https://open.feishu.cn/open-apis/drive/v1/my_drive/root/children"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"My Drive请求状态码: {response.status_code}")
    print(f"My Drive响应: {response.text[:500]}...")

def test_wiki_spaces(token):
    url = "https://open.feishu.cn/open-apis/wiki/v2/spaces"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"\nWiki Spaces请求状态码: {response.status_code}")
    print(f"Wiki Spaces响应: {response.text[:500]}...")

def test_search_all(token):
    url = "https://open.feishu.cn/open-apis/drive/search/v2/files/search"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": "", "page_size": 10}
    response = requests.post(url, headers=headers, json=payload)
    print(f"\nSearch请求状态码: {response.status_code}")
    print(f"Search响应: {response.text[:500]}...")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_my_drive(token)
        test_wiki_spaces(token)
        test_search_all(token)