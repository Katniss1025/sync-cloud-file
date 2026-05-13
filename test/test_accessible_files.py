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

def test_accessible_files(token):
    url = "https://open.feishu.cn/open-apis/drive/v1/files?page_size=50"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"可访问文件列表请求状态码: {response.status_code}")
    result = response.json()
    
    if result.get("code") == 0:
        files = result.get("data", {}).get("files", [])
        print(f"\n应用可访问的文件/文件夹: {len(files)} 个")
        for i, file in enumerate(files[:10], 1):
            print(f"{i}. 名称: {file.get('name')}, 类型: {file.get('type')}, Token: {file.get('token')[:20]}...")
        
        if len(files) == 0:
            print("\n⚠️ 应用当前没有可访问的任何文件/文件夹")
            print("请检查：")
            print("1. 文件夹是否设置为'组织内可见'")
            print("2. 是否需要管理员授权应用访问特定文件夹")
    else:
        print(f"请求失败: {result.get('msg')}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_accessible_files(token)