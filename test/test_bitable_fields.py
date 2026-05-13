import requests
import os

os.environ['NO_PROXY'] = 'open.feishu.cn'
os.environ['no_proxy'] = 'open.feishu.cn'

APP_ID = "cli_a97b0e12ec391bc4"
APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"
APP_TOKEN = "ANlPblTwhaVlausMjpucnb3an7M"
TABLE_ID = "tblew6g53b1wWWNK"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result["tenant_access_token"]
    return None

def get_table_fields(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers)
    
    print(f"获取字段状态码: {response.status_code}")
    print(f"获取字段响应: {response.text}")

def test_create_simple(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "fields": {
            "成果名称": "测试文件"
        }
    }
    
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, headers=headers, json=payload)
    
    print(f"\n创建简单记录状态码: {response.status_code}")
    print(f"创建简单记录响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        get_table_fields(token)
        test_create_simple(token)