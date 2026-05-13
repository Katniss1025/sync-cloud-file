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

def test_read_bitable(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records?page_size=10"
    headers = {"Authorization": f"Bearer {token}"}
    
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers)
    
    print(f"读取多维表格状态码: {response.status_code}")
    print(f"读取多维表格响应: {response.text}")

def test_create_bitable(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "records": [{
            "fields": {
                "成果名称": "测试文件",
                "链接": "https://test.com",
                "分类": "测试分类"
            }
        }]
    }
    
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, headers=headers, json=payload)
    
    print(f"\n创建记录状态码: {response.status_code}")
    print(f"创建记录响应: {response.text}")

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"获取到Token: {token[:20]}...")
        test_read_bitable(token)
        test_create_bitable(token)