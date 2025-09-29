"""
🍪 Chrome Cookie 自动提取器
自动从Chrome浏览器中提取知乎登录Cookie
"""

import os
import sqlite3
import json
import base64
import shutil
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ChromeCookieExtractor:
    """Chrome Cookie提取器"""
    
    def __init__(self):
        self.chrome_paths = self._get_chrome_paths()
    
    def _get_chrome_paths(self):
        """获取Chrome Cookie数据库路径"""
        paths = []
        
        # macOS路径
        if os.name == 'posix':
            home = Path.home()
            chrome_paths = [
                home / "Library/Application Support/Google/Chrome/Default/Cookies",
                home / "Library/Application Support/Google/Chrome/Profile 1/Cookies",
                home / "Library/Application Support/Google/Chrome/Default/Network/Cookies",
            ]
            paths.extend([str(p) for p in chrome_paths if p.exists()])
        
        # Windows路径
        elif os.name == 'nt':
            appdata = os.environ.get('APPDATA', '')
            localappdata = os.environ.get('LOCALAPPDATA', '')
            chrome_paths = [
                os.path.join(localappdata, "Google/Chrome/User Data/Default/Cookies"),
                os.path.join(localappdata, "Google/Chrome/User Data/Profile 1/Cookies"),
                os.path.join(appdata, "Google/Chrome/User Data/Default/Cookies"),
            ]
            paths.extend([p for p in chrome_paths if os.path.exists(p)])
        
        # Linux路径
        else:
            home = Path.home()
            chrome_paths = [
                home / ".config/google-chrome/Default/Cookies",
                home / ".config/google-chrome/Profile 1/Cookies",
                home / ".config/chromium/Default/Cookies",
            ]
            paths.extend([str(p) for p in chrome_paths if p.exists()])
        
        return paths
    
    def _copy_cookies_db(self, source_path):
        """复制Cookie数据库到临时文件"""
        try:
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, "cookies.db")
            shutil.copy2(source_path, temp_path)
            return temp_path
        except Exception as e:
            logger.warning(f"复制Cookie数据库失败: {e}")
            return None
    
    def _decrypt_cookie_value(self, encrypted_value, key=None):
        """解密Cookie值"""
        try:
            if not encrypted_value:
                return ""
            
            # 如果已经是字符串，直接返回
            if isinstance(encrypted_value, str):
                return encrypted_value
            
            # 如果是字节，尝试解码
            if isinstance(encrypted_value, bytes):
                # 对于Chrome的加密Cookie，我们尝试直接解码
                try:
                    # 尝试UTF-8解码
                    decoded = encrypted_value.decode('utf-8')
                    return decoded
                except UnicodeDecodeError:
                    # 如果UTF-8失败，返回base64编码
                    import base64
                    return base64.b64encode(encrypted_value).decode('ascii')
            
            return str(encrypted_value)
        except Exception as e:
            logger.warning(f"解密Cookie失败: {e}")
            return str(encrypted_value) if encrypted_value else ""
    
    def extract_zhihu_cookies(self):
        """提取知乎Cookie"""
        cookies = {}
        
        for chrome_path in self.chrome_paths:
            try:
                logger.info(f"尝试从 {chrome_path} 提取Cookie")
                
                # 复制数据库到临时文件
                temp_path = self._copy_cookies_db(chrome_path)
                if not temp_path:
                    continue
                
                # 连接数据库
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                
                # 查询知乎Cookie
                cursor.execute("""
                    SELECT name, value, encrypted_value, host_key, path, expires_utc, is_secure, is_httponly
                    FROM cookies 
                    WHERE host_key LIKE '%zhihu.com%'
                    ORDER BY name
                """)
                
                rows = cursor.fetchall()
                
                for row in rows:
                    name, value, encrypted_value, host_key, path, expires_utc, is_secure, is_httponly = row
                    
                    # 优先使用明文值，如果没有则使用加密值
                    cookie_value = value if value else encrypted_value
                    
                    # 解密Cookie值
                    decrypted_value = self._decrypt_cookie_value(cookie_value)
                    
                    # 只保存重要的Cookie
                    if name in ['d_c0', 'z_c0', '_zap', 'q_c1', 'tgw_l7_route', '__zse_ck', 
                               'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49', 
                               'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49']:
                        cookies[name] = decrypted_value
                        logger.info(f"找到Cookie: {name} = {decrypted_value[:20]}...")
                
                conn.close()
                
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                    os.rmdir(os.path.dirname(temp_path))
                except:
                    pass
                
                if cookies:
                    logger.info(f"成功提取到 {len(cookies)} 个知乎Cookie")
                    return cookies
                    
            except Exception as e:
                logger.warning(f"从 {chrome_path} 提取Cookie失败: {e}")
                continue
        
        logger.warning("未能从Chrome中提取到知乎Cookie")
        return {}
    
    def save_cookies_to_config(self, cookies):
        """将Cookie保存到配置文件"""
        if not cookies:
            logger.warning("没有Cookie可保存")
            return False
        
        try:
            config_path = "config.py"
            
            # 读取现有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建Cookie字典字符串
            cookie_dict = "{\n"
            for name, value in cookies.items():
                # 转义特殊字符
                escaped_value = str(value).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                cookie_dict += f"        '{name}': '{escaped_value}',\n"
            cookie_dict += "    }"
            
            # 替换配置
            import re
            pattern = r'ZHIHU_REAL_COOKIES = \{[^}]*\}'
            replacement = f'ZHIHU_REAL_COOKIES = {cookie_dict}'
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"成功保存 {len(cookies)} 个Cookie到配置文件")
            return True
            
        except Exception as e:
            logger.error(f"保存Cookie到配置文件失败: {e}")
            return False

def main():
    """主函数"""
    print("🍪 开始自动提取Chrome中的知乎Cookie...")
    
    extractor = ChromeCookieExtractor()
    
    # 提取Cookie
    cookies = extractor.extract_zhihu_cookies()
    
    if cookies:
        print(f"✅ 成功提取到 {len(cookies)} 个知乎Cookie:")
        for name, value in cookies.items():
            print(f"   {name}: {value[:30]}...")
        
        # 保存到配置文件
        if extractor.save_cookies_to_config(cookies):
            print("✅ Cookie已保存到config.py文件")
            print("🚀 现在可以重启服务并测试知乎抓取了！")
        else:
            print("❌ 保存Cookie到配置文件失败")
    else:
        print("❌ 未能提取到知乎Cookie")
        print("💡 请确保：")
        print("   1. Chrome浏览器已登录知乎")
        print("   2. 浏览器没有运行（关闭Chrome后重试）")
        print("   3. 有足够的文件访问权限")

if __name__ == "__main__":
    main()
