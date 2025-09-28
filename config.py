"""
⚙️ 应用配置
超级阅读研究助手的配置文件
"""

import os


class Config:
    """应用配置类"""
    
    # Flask应用配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    
    # 网页抓取配置
    USER_AGENT = os.getenv('USER_AGENT', 
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    )
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    
    # 图片缓存配置
    IMAGE_CACHE_DAYS = 7  # 图片缓存7天
    IMAGE_CACHE_MAX_AGE = 604800  # 7天 = 604800秒
    
    # 代理URL配置
    PROXY_BASE_URL = os.getenv('PROXY_BASE_URL', 'https://gpts-article-analyzer.vercel.app')
    
    # 性能配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_config_dict(cls):
        """获取配置字典"""
        return {
            'FLASK_ENV': cls.FLASK_ENV,
            'FLASK_DEBUG': cls.FLASK_DEBUG,
            'PORT': cls.PORT,
            'TIMEOUT': cls.TIMEOUT,
            'IMAGE_CACHE_DAYS': cls.IMAGE_CACHE_DAYS,
            'PROXY_BASE_URL': cls.PROXY_BASE_URL,
            'LOG_LEVEL': cls.LOG_LEVEL
        }