from flask import Flask, request, jsonify
from flask_cors import CORS
from web_scraper import WebScraper
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 初始化网页抓取器
scraper = WebScraper()

@app.route('/')
def index():
    """主页"""
    return """
    <h1>🤖 智能文章解读器 - GPTs版本</h1>
    <p>专门为GPTs设计的文章内容提取服务</p>
    <p>API端点: /extract</p>
    <p>使用方法: POST /extract {"url": "文章链接"}</p>
    """

@app.route('/extract', methods=['POST'])
def extract_article():
    """提取文章内容供GPTs分析"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': '请提供文章链接'})
        
        logger.info(f"开始提取文章内容: {url}")
        
        # 抓取文章内容
        article_data = scraper.scrape_article(url)
        
        if 'error' in article_data:
            return jsonify({'success': False, 'error': f'抓取文章失败: {article_data["error"]}'})
        
        # 为GPTs准备数据
        result = {
            'success': True,
            'data': {
                'title': article_data['title'],
                'content': article_data['content'],
                'author': article_data['author'],
                'publish_time': article_data['publish_time'],
                'summary': article_data['summary'],
                'images': [
                    {
                        'url': img['absolute_url'],
                        'alt': img['alt'],
                        'title': img['title']
                    }
                    for img in article_data['images']
                ],
                'tags': article_data['tags']
            }
        }
        
        logger.info(f"文章内容提取完成: {article_data['title']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"提取文章内容失败: {str(e)}")
        return jsonify({'success': False, 'error': f'提取失败: {str(e)}'})

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy', 'message': 'GPTs文章提取器运行正常'})

if __name__ == '__main__':
    logger.info("启动GPTs文章提取器...")
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
