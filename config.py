import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # OpenAI API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # 应用配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    
    # 图片处理配置
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 5242880))  # 5MB
    SUPPORTED_IMAGE_FORMATS = os.getenv('SUPPORTED_IMAGE_FORMATS', 'jpg,jpeg,png,gif,webp').split(',')
    
    # 网页抓取配置
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    
    # GPTs配置
    GPT_MODEL = "gpt-4o"  # 使用最新的GPT-4o模型
    GPT_VISION_MODEL = "gpt-4o"  # 使用GPT-4o进行图片分析
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7

