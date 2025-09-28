from flask import Flask, request, jsonify
from flask_cors import CORS
from web_scraper import WebScraper
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
        
        # 为GPTs准备数据，包含代理图片URL和智能过滤
        import base64
        from urllib.parse import quote
        
        # 获取用户指定的过滤类型
        filter_type = data.get('filter_type', 'all')  # all, content_only, cover_only, custom
        
        processed_images = []
        for i, img in enumerate(article_data['images']):
            # 生成代理URL
            encoded_url = base64.b64encode(quote(img['absolute_url'], safe='').encode()).decode()
            proxy_url = f"https://gpts-article-analyzer.vercel.app/image/{encoded_url}"
            
            # 根据过滤类型决定是否包含此图片
            should_include = True
            
            if filter_type == 'content_only':
                # 只保留内容图片，过滤装饰图片
                should_include = self._is_content_image(img, i)
            elif filter_type == 'cover_only':
                # 只保留封面图片
                should_include = 'cover' in img['alt'].lower() or 'cover' in img.get('title', '').lower()
            elif filter_type == 'custom':
                # 自定义过滤，基于用户提示词
                custom_filter = data.get('custom_filter', '')
                should_include = self._matches_custom_filter(img, custom_filter)
            
            if should_include:
                processed_images.append({
                    'original_url': img['absolute_url'],
                    'proxy_url': proxy_url,
                    'alt': img['alt'],
                    'title': img['title'],
                    'index': len(processed_images) + 1,
                    'filter_reason': self._get_filter_reason(img, filter_type)
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
    """图片代理接口，用于绕过防盗链"""
    try:
        import base64
        from urllib.parse import unquote
        
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
        
        # 返回图片
        from flask import Response
        return Response(
            response.content,
            mimetype=response.headers.get('content-type', 'image/jpeg'),
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        logger.error(f"图片代理失败: {str(e)}")
        return jsonify({'error': f'图片代理失败: {str(e)}'}), 500

    def _is_content_image(self, img: dict, index: int) -> bool:
        """判断是否为内容图片"""
        # 封面图片总是保留
        if 'cover' in img['alt'].lower() or 'cover' in img.get('title', '').lower():
            return True
        
        # 过滤掉太小的图片
        try:
            width = int(img.get('width', 0)) if img.get('width') else 0
            height = int(img.get('height', 0)) if img.get('height') else 0
            if width > 0 and height > 0 and (width < 150 or height < 150):
                return False
        except:
            pass
        
        # 过滤掉正方形小图（可能是头像）
        try:
            width = int(img.get('width', 0)) if img.get('width') else 0
            height = int(img.get('height', 0)) if img.get('height') else 0
            if width > 0 and height > 0:
                if abs(width - height) < 20 and width < 200:
                    return False
        except:
            pass
        
        # 对于微信文章，前几张图片通常是内容图片
        if index < 5:  # 前5张图片通常是内容图片
            return True
        
        return True
    
    def _matches_custom_filter(self, img: dict, custom_filter: str) -> bool:
        """基于自定义提示词过滤图片"""
        if not custom_filter:
            return True
        
        # 将提示词转换为关键词列表
        keywords = [kw.strip().lower() for kw in custom_filter.split(',')]
        
        # 检查图片属性是否匹配关键词
        img_text = f"{img['alt']} {img.get('title', '')} {img['src']}".lower()
        
        for keyword in keywords:
            if keyword in img_text:
                return True
        
        return False
    
    def _get_filter_reason(self, img: dict, filter_type: str) -> str:
        """获取过滤原因说明"""
        if filter_type == 'content_only':
            if 'cover' in img['alt'].lower():
                return "封面图片"
            else:
                return "内容配图"
        elif filter_type == 'cover_only':
            return "封面图片"
        elif filter_type == 'custom':
            return "自定义过滤"
        else:
            return "全部保留"

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
