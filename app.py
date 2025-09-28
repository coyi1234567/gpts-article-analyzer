from flask import Flask, request, jsonify
from flask_cors import CORS
from web_scraper import WebScraper
from config import Config
import logging
import requests

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
        
        # 为GPTs准备数据，包含代理图片URL
        import base64
        from urllib.parse import quote
        
        processed_images = []
        for i, img in enumerate(article_data['images']):
            # 生成代理URL
            encoded_url = base64.b64encode(quote(img['absolute_url'], safe='').encode()).decode()
            proxy_url = f"https://gpts-article-analyzer.vercel.app/image/{encoded_url}"
            
            processed_images.append({
                'original_url': img['absolute_url'],
                'proxy_url': proxy_url,
                'alt': img['alt'],
                'title': img['title'],
                'index': i + 1,
                'description': f"图片{i+1}" + (f" - {img['alt']}" if img['alt'] else "")
            })
        
        result = {
            'success': True,
            'data': {
                'title': article_data['title'],
                'content': article_data['content'],
                'author': article_data['author'],
                'publish_time': article_data['publish_time'],
                'summary': article_data['summary'],
                'images': processed_images,
                'tags': article_data['tags']
            }
        }
        
        logger.info(f"文章内容提取完成: {article_data['title']}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"提取文章内容失败: {str(e)}")
        return jsonify({'success': False, 'error': f'提取失败: {str(e)}'})

@app.route('/image/<path:encoded_url>')
def proxy_image(encoded_url):
    """图片代理接口，用于绕过防盗链，支持7天缓存过期"""
    try:
        import base64
        from urllib.parse import unquote
        from datetime import datetime, timedelta
        
        # 解码URL
        image_url = base64.b64decode(encoded_url.encode()).decode()
        image_url = unquote(image_url)
        
        logger.info(f"代理图片请求: {image_url}")
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }
        
        # 获取图片
        response = requests.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 计算缓存过期时间
        expires_date = datetime.utcnow() + timedelta(days=Config.IMAGE_CACHE_DAYS)
        expires_str = expires_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 返回图片，设置缓存
        from flask import Response
        return Response(
            response.content,
            mimetype=response.headers.get('content-type', 'image/jpeg'),
            headers={
                'Cache-Control': f'public, max-age={Config.IMAGE_CACHE_MAX_AGE}',
                'Expires': expires_str,
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        logger.error(f"图片代理失败: {str(e)}")
        return jsonify({'error': f'图片代理失败: {str(e)}'}), 500


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
