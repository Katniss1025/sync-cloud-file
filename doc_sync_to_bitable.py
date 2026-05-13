from unicodedata import category
import lark_oapi as lark
import logging
import requests
import os
from typing import Dict, List, Tuple
from lark_oapi.api.bitable.v1 import *

os.environ['NO_PROXY'] = 'open.feishu.cn'
os.environ['no_proxy'] = 'open.feishu.cn'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 允许的分类列表
ALLOWED_CATEGORIES = ['论文发表', '热点分析', '每日动态', '月刊', '星座基础数据库', '应用专刊', '年报', '半月刊', '专题研究', '咨询报告']

# 需要跳过的文件夹
SKIP_FOLDERS = ['每日动态']


class FeishuDocSync:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.client = self._build_client()
        self.tenant_access_token = None
        self.token_expire_time = 0

    def _build_client(self) -> lark.Client:
        return lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .build()

    def _get_session(self):
        session = requests.Session()
        session.trust_env = False
        return session

    def _get_tenant_access_token(self) -> str:
        import time
        current_time = time.time()
        if self.tenant_access_token and current_time < self.token_expire_time:
            return self.tenant_access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        
        try:
            session = self._get_session()
            response = session.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.tenant_access_token = result["tenant_access_token"]
                self.token_expire_time = current_time + result["expire"] - 60
                logger.info("获取tenant_access_token成功")
                return self.tenant_access_token
            else:
                logger.error(f"获取token失败: {result.get('msg')}")
                raise Exception(f"获取token失败: {result.get('msg')}")
        except Exception as e:
            logger.error(f"获取tenant_access_token异常: {str(e)}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        token = self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

    def list_folder_files(self, folder_token: str, parent_name: str = "", grandparent_name: str = "", category: str = "") -> List[Dict]:
        """
        递归获取文件夹中的所有文件
        :param folder_token: 当前文件夹token
        :param parent_name: 父文件夹名称（用于作为完成时间）
        :param grandparent_name: 祖父文件夹名称（用于作为分类）
        :param category: 当前分类
        """
        files = []
        try:
            url = f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={folder_token}&page_size=100"
            headers = self._get_headers()
            session = self._get_session()
            
            while url:
                response = session.get(url, headers=headers)
                
                if response.status_code == 403:
                    result = response.json()
                    logger.error(f"权限错误: code={result.get('code')}, msg={result.get('msg')}")
                    logger.error("请尝试将文件夹设置为'组织内可见'或联系管理员授权应用访问")
                    return []
                
                response.raise_for_status()
                result = response.json()
                
                if result.get("code") != 0:
                    logger.error(f"获取文件列表失败: {result.get('msg')}")
                    break
                
                folder_files = result.get("data", {}).get("files", [])
                if not folder_files:
                    logger.info(f"文件夹 {folder_token} 为空")
                    break
                
                for item in folder_files:
                    file_type = item.get("type")
                    file_name = item.get("name")
                    file_token = item.get("token")
                    file_url = item.get("url", "")
                    
                    # 跳过需要忽略的文件夹
                    if file_type == "folder" and file_name in SKIP_FOLDERS:
                        logger.info(f"跳过文件夹: {file_name}")
                        continue
                    
                    if file_type == "folder":
                        # 更新层级：当前文件夹变为父文件夹，原父文件夹变为祖父文件夹
                        new_category = grandparent_name if grandparent_name else file_name
                        if new_category in ALLOWED_CATEGORIES:
                            cat = new_category
                        else:
                            cat = category if category else new_category
                        sub_folder_files = self.list_folder_files(file_token, file_name, parent_name, cat)
                        files.extend(sub_folder_files)
                    elif file_type != "bitable":
                        if not file_url:
                            file_url = self._get_file_share_url(file_token)
                        
                        # 确定分类和完成时间
                        final_category = category if category else grandparent_name
                        completion_time = parent_name  # 最终文件夹名称作为完成时间
                        
                        # 如果分类不在允许列表中，记录警告
                        if final_category and final_category not in ALLOWED_CATEGORIES:
                            logger.warning(f"文件 {file_name} 的分类 '{final_category}' 不在允许列表中")
                        
                        files.append({
                            "file_name": file_name,
                            "file_url": file_url,
                            "category": final_category,
                            "completion_time": completion_time,
                            "file_token": file_token
                        })
                
                url = None
                    
        except Exception as e:
            logger.error(f"获取文件夹文件列表异常: {str(e)}")
        
        return files

    def _get_file_share_url(self, file_token: str) -> str:
        try:
            url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/shared_link"
            headers = self._get_headers()
            session = self._get_session()
            response = session.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data", {}).get("url", "")
            
            logger.warning(f"获取文件分享链接失败，使用默认链接")
            return f"https://www.feishu.cn/file/{file_token}"
        except Exception as e:
            logger.error(f"获取文件分享链接异常: {str(e)}")
            return f"https://www.feishu.cn/file/{file_token}"

    def get_bitable_records(self, app_token: str, table_id: str) -> List[Dict]:
        records = []
        try:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=500"
            headers = self._get_headers()
            session = self._get_session()
            
            response = session.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                records = result.get("data", {}).get("items", [])
            else:
                logger.error(f"获取多维表格记录失败: {result.get('msg')}")
                    
        except Exception as e:
            logger.error(f"获取多维表格记录异常: {str(e)}")
        
        return records

    def create_bitable_record(self, app_token: str, table_id: str, fields: Dict) -> bool:
        try:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            headers = self._get_headers()
            session = self._get_session()
            payload = {"fields": fields}
            
            response = session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logger.info(f"创建记录成功: {fields.get('成果名称')}")
                return True
            else:
                logger.error(f"创建记录失败: {result.get('msg')}")
                return False
        except Exception as e:
            logger.error(f"创建记录异常: {str(e)}")
            return False

    def update_bitable_record(self, app_token: str, table_id: str, record_id: str, fields: Dict) -> bool:
        try:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
            headers = self._get_headers()
            session = self._get_session()
            payload = {"fields": fields}
            
            response = session.put(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logger.info(f"更新记录成功: {record_id}")
                return True
            else:
                logger.error(f"更新记录失败: {result.get('msg')}")
                return False
        except Exception as e:
            logger.error(f"更新记录异常: {str(e)}")
            return False

    def sync_files_to_bitable(self, folder_token: str, app_token: str, table_id: str) -> Tuple[int, int]:
        logger.info("开始同步文件到多维表格...")
        
        folder_files = self.list_folder_files(folder_token)
        logger.info(f"获取到 {len(folder_files)} 个文件")
        
        existing_records = self.get_bitable_records(app_token, table_id)
        existing_names = {}
        for record in existing_records:
            fields = record.get("fields", {})
            if isinstance(fields, dict) and "成果名称" in fields:
                existing_names[fields["成果名称"]] = record.get("record_id")
        
        created_count = 0
        updated_count = 0
        
        for file_info in folder_files:
            file_name = file_info["file_name"]
            
            fields = {
                "成果名称": file_name,
                "链接": file_info["file_url"],
                "分类": file_info["category"] if file_info["category"] else "",
                "完成时间": file_info["completion_time"] if file_info["completion_time"] else ""
            }
            
            if file_name in existing_names:
                record_id = existing_names[file_name]
                if self.update_bitable_record(app_token, table_id, record_id, fields):
                    updated_count += 1
            else:
                if self.create_bitable_record(app_token, table_id, fields):
                    created_count += 1
        
        logger.info(f"同步完成: 新增 {created_count} 条记录, 更新 {updated_count} 条记录")
        return created_count, updated_count


# 添加定时任务支持
try:
    import schedule
    import time
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False


def run_periodically(interval_minutes: int = 60):
    """
    定期运行同步任务
    :param interval_minutes: 同步间隔（分钟），默认每小时同步一次
    """
    if not HAS_SCHEDULE:
        logger.error("请先安装 schedule 库: pip install schedule")
        return
    
    logger.info(f"定时同步任务已启动，每 {interval_minutes} 分钟同步一次")
    
    def job():
        try:
            logger.info("===== 开始定时同步 =====")
            APP_ID = "cli_a97b0e12ec391bc4"
            APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"
            
            FOLDER_TOKEN = "Fa3BfRjRolhjyQdG5k4c72pSn8j"
            APP_TOKEN = "ANlPblTwhaVlausMjpucnb3an7M"
            TABLE_ID = "tblew6g53b1wWWNK"
            
            if not all([APP_ID, APP_SECRET, FOLDER_TOKEN, APP_TOKEN, TABLE_ID]):
                logger.error("请先配置所有必要的参数")
                return
            
            sync = FeishuDocSync(APP_ID, APP_SECRET)
            created, updated = sync.sync_files_to_bitable(FOLDER_TOKEN, APP_TOKEN, TABLE_ID)
            logger.info(f"定时同步完成: 新增 {created} 条, 更新 {updated} 条")
        except Exception as e:
            logger.error(f"定时同步失败: {str(e)}")
    
    # 立即执行一次
    job()
    
    # 设置定时任务
    schedule.every(interval_minutes).minutes.do(job)
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='飞书云文档同步到多维表格')
    parser.add_argument('--periodic', action='store_true', help='启用定时同步模式')
    parser.add_argument('--interval', type=int, default=60, help='同步间隔（分钟），默认60分钟')
    
    args = parser.parse_args()
    
    if args.periodic:
        # 定时同步模式
        run_periodically(args.interval)
    else:
        # 单次同步模式（原有逻辑）
        APP_ID = "cli_a97b0e12ec391bc4"
        APP_SECRET = "LymTUuZJggkeetChyTfaOc8nOkgC5XEN"
        
        FOLDER_TOKEN = "Fa3BfRjRolhjyQdG5k4c72pSn8j"
        APP_TOKEN = "ANlPblTwhaVlausMjpucnb3an7M"
        TABLE_ID = "tblew6g53b1wWWNK"
        
        if not all([APP_ID, APP_SECRET, FOLDER_TOKEN, APP_TOKEN, TABLE_ID]):
            logger.error("请先配置所有必要的参数")
            return
        
        sync = FeishuDocSync(APP_ID, APP_SECRET)
        
        try:
            created, updated = sync.sync_files_to_bitable(FOLDER_TOKEN, APP_TOKEN, TABLE_ID)
            print(f"\n同步结果:")
            print(f"  新增记录: {created} 条")
            print(f"  更新记录: {updated} 条")
        except Exception as e:
            logger.error(f"同步失败: {str(e)}")


if __name__ == "__main__":
    main()
