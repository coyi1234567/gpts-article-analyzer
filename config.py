import os

class Config:
    """应用配置类"""
    
    # Flask应用配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))

    # 网页抓取配置
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    
    # 图片缓存配置
    IMAGE_CACHE_DAYS = 7  # 图片缓存7天
    IMAGE_CACHE_MAX_AGE = 604800  # 7天 = 604800秒
    
    # 代理URL配置
    PROXY_BASE_URL = os.getenv('PROXY_BASE_URL', 'https://gpts-article-analyzer-z6axascum-coyis-projects.vercel.app')

