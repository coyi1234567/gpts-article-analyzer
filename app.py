"""
🤖 超级阅读研究助手 - GPTs版本
世界一流的智能文章解读器

功能特点：
- 多平台文章抓取（微信、小红书、微博等）
- 图文结合智能分析
- 图片代理服务（解决防盗链问题）
- 7天图片缓存机制
- 结构化分析框架
"""

import base64
import logging
from datetime import datetime, timedelta
from urllib.parse import quote, unquote

import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from config import Config
from web_scraper import WebScraper

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 初始化网页抓取器
scraper = WebScraper()


@app.route('/')
def index():
    """主页 - 展示API信息"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>超级阅读研究助手</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            .header { text-align: center; margin-bottom: 30px; }
            .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .api-info { background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .status { color: #4caf50; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 超级阅读研究助手</h1>
            <p class="status">✅ 服务运行正常</p>
        </div>
        
        <div class="feature">
            <h3>🎯 核心功能</h3>
            <ul>
                <li>多平台文章抓取（微信、小红书、微博等）</li>
                <li>图文结合智能分析</li>
                <li>图片代理服务（解决防盗链问题）</li>
                <li>7天图片缓存机制</li>
                <li>结构化分析框架</li>
            </ul>
        </div>
        
        <div class="api-info">
            <h3>📡 API接口</h3>
            <p><strong>文章提取：</strong> POST /extract</p>
            <p><strong>图片代理：</strong> GET /image/{encoded_url}</p>
            <p><strong>健康检查：</strong> GET /health</p>
        </div>
        
        <div class="feature">
            <h3>🚀 使用方法</h3>
            <pre>curl -X POST /extract -H "Content-Type: application/json" -d '{"url": "文章链接"}'</pre>
        </div>
    </body>
    </html>
    """


@app.route('/extract', methods=['POST'])
def extract_article():
    """
    提取文章内容供GPTs分析
    
    Request Body:
        {
            "url": "文章链接"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "title": "文章标题",
                "content": "文章内容",
                "author": "作者",
                "publish_time": "发布时间",
                "summary": "文章摘要",
                "images": [...],
                "tags": [...]
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({'success': False, 'error': '请提供文章链接'}), 400
        
        logger.info(f"开始提取文章内容: {url}")
        
        # 抓取文章内容
        article_data = scraper.scrape_article(url)
        
        if 'error' in article_data:
            logger.error(f"抓取失败: {article_data['error']}")
            return jsonify({'success': False, 'error': f'抓取文章失败: {article_data["error"]}'}), 500
        
        # 为GPTs准备数据，包含代理图片URL
        processed_images = []
        for i, img in enumerate(article_data['images']):
            # 生成代理URL
            encoded_url = base64.b64encode(quote(img['absolute_url'], safe='').encode()).decode()
            proxy_url = f"{Config.PROXY_BASE_URL}/image/{encoded_url}"
            
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
        
        logger.info(f"文章内容提取完成: {article_data['title']} (图片数量: {len(processed_images)})")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"提取文章内容失败: {str(e)}")
        return jsonify({'success': False, 'error': f'提取失败: {str(e)}'}), 500


@app.route('/image/<path:encoded_url>')
def proxy_image(encoded_url):
    """
    图片代理接口，用于绕过防盗链，支持7天缓存过期
    
    Args:
        encoded_url: Base64编码的图片URL
    
    Returns:
        图片内容或错误信息
    """
    try:
        # 解码URL
        image_url = base64.b64decode(encoded_url.encode()).decode()
        image_url = unquote(image_url)
        
        logger.info(f"代理图片请求: {image_url}")
        
        # 对于微信图片，使用多种代理服务
        if 'mmbiz.qpic.cn' in image_url or 'mmecoa.qpic.cn' in image_url:
            # 尝试多种代理服务
            proxy_services = [
                f"https://images.weserv.nl/?url={quote(image_url, safe='')}",
                f"https://pic1.xuehuaimg.com/proxy/{quote(image_url, safe='')}",
                f"https://img.nga.178.com/attachments/mon_202409/29/{quote(image_url, safe='')}"
            ]
            
            response = None
            for proxy_url in proxy_services:
                try:
                    logger.info(f"尝试代理服务: {proxy_url}")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                    }
                    
                    response = requests.get(proxy_url, headers=headers, timeout=Config.TIMEOUT, stream=True)
                    response.raise_for_status()
                    logger.info(f"代理服务成功: {proxy_url}")
                    break
                except Exception as e:
                    logger.warning(f"代理服务失败: {proxy_url}, 错误: {str(e)}")
                    continue
            
            if response is None:
                raise Exception("所有代理服务都失败了")
            
            # 计算缓存过期时间
            expires_date = datetime.utcnow() + timedelta(days=Config.IMAGE_CACHE_DAYS)
            expires_str = expires_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # 返回图片，设置缓存
            return Response(
                response.content,
                mimetype=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    'Cache-Control': f'public, max-age={Config.IMAGE_CACHE_MAX_AGE}',
                    'Expires': expires_str,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
        
        # 对于其他图片，使用原有逻辑
        else:
            # 设置请求头，模拟浏览器访问
            headers = {
                'User-Agent': Config.USER_AGENT,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            # 根据图片来源设置合适的Referer
            if 'csdn.net' in image_url:
                headers['Referer'] = 'https://blog.csdn.net/'
            elif 'weixin.qq.com' in image_url:
                headers['Referer'] = 'https://mp.weixin.qq.com/'
            else:
                headers['Referer'] = 'https://www.google.com/'
            
            # 获取图片
            response = requests.get(image_url, headers=headers, timeout=Config.TIMEOUT, stream=True)
            response.raise_for_status()
            
            # 计算缓存过期时间
            expires_date = datetime.utcnow() + timedelta(days=Config.IMAGE_CACHE_DAYS)
            expires_str = expires_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # 返回图片，设置缓存
            return Response(
                response.content,
                mimetype=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    'Cache-Control': f'public, max-age={Config.IMAGE_CACHE_MAX_AGE}',
                    'Expires': expires_str,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
        
    except requests.exceptions.Timeout:
        logger.error(f"图片请求超时: {image_url}")
        return jsonify({'error': '图片请求超时'}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"图片请求失败: {image_url}, 错误: {str(e)}")
        return jsonify({'error': f'图片请求失败: {str(e)}'}), 502
    except Exception as e:
        logger.error(f"图片代理失败: {str(e)}")
        return jsonify({'error': f'图片代理失败: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态信息
    """
    return jsonify({
        'status': 'healthy',
        'message': '超级阅读研究助手运行正常',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': '接口不存在'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify({'error': '请求方法不允许'}), 405


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(error)}")
    return jsonify({'error': '内部服务器错误'}), 500


if __name__ == '__main__':
    logger.info("🚀 启动超级阅读研究助手...")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )