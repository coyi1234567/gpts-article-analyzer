import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
from typing import Dict, List, Optional, Tuple
from config import Config
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """网页内容抓取器，支持图文内容提取"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.timeout = Config.TIMEOUT
    
    def scrape_article(self, url: str) -> Dict:
        """
        抓取文章内容，包括文字和图片
        
        Args:
            url: 文章链接
            
        Returns:
            包含文章信息的字典
        """
        try:
            logger.info(f"开始抓取文章: {url}")
            
            # 发送请求
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取文章信息
            article_info = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'images': self._extract_images(soup, url),
                'author': self._extract_author(soup),
                'publish_time': self._extract_publish_time(soup),
                'summary': self._extract_summary(soup),
                'tags': self._extract_tags(soup),
                'raw_html': str(soup)
            }
            
            logger.info(f"文章抓取完成: {article_info['title']}")
            return article_info
            
        except Exception as e:
            logger.error(f"抓取文章失败: {url}, 错误: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'title': '',
                'content': '',
                'images': [],
                'author': '',
                'publish_time': '',
                'summary': '',
                'tags': []
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        # 尝试多种标题选择器
        title_selectors = [
            'h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            'title',
            '[class*="title"]',
            '[id*="title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                return title_elem.get_text(strip=True)
        
        return soup.title.get_text(strip=True) if soup.title else ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章正文内容"""
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # 尝试多种内容选择器
        content_selectors = [
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'article',
            '.article-body',
            '.post-body',
            '[class*="content"]',
            '[id*="content"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 清理内容
                content = self._clean_text(content_elem.get_text())
                if len(content) > 100:  # 确保内容足够长
                    return content
        
        # 如果没有找到特定容器，尝试从body中提取
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return ""
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """提取文章中的图片"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            img_info = {
                'src': '',
                'alt': '',
                'title': '',
                'width': '',
                'height': '',
                'absolute_url': ''
            }
            
            # 获取图片属性
            img_info['src'] = img.get('src', '')
            img_info['alt'] = img.get('alt', '')
            img_info['title'] = img.get('title', '')
            img_info['width'] = img.get('width', '')
            img_info['height'] = img.get('height', '')
            
            # 转换为绝对URL
            if img_info['src']:
                img_info['absolute_url'] = urljoin(base_url, img_info['src'])
                
                # 过滤掉小图标和装饰性图片
                if self._is_valid_content_image(img_info):
                    images.append(img_info)
        
        return images
    
    def _is_valid_content_image(self, img_info: Dict) -> bool:
        """判断是否为有效的内容图片"""
        src = img_info['src'].lower()
        alt = img_info['alt'].lower()
        
        # 过滤掉常见的非内容图片
        exclude_patterns = [
            'logo', 'icon', 'avatar', 'button', 'banner', 'ad', 'advertisement',
            'sponsor', 'sponsored', 'sidebar', 'header', 'footer', 'nav',
            'social', 'share', 'comment', 'like', 'follow'
        ]
        
        for pattern in exclude_patterns:
            if pattern in src or pattern in alt:
                return False
        
        # 过滤掉太小的图片（可能是装饰性图片）
        try:
            width = int(img_info['width']) if img_info['width'] else 0
            height = int(img_info['height']) if img_info['height'] else 0
            if width > 0 and height > 0 and (width < 100 or height < 100):
                return False
        except:
            pass
        
        return True
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者信息"""
        author_selectors = [
            '.author',
            '.byline',
            '.writer',
            '[class*="author"]',
            '[class*="byline"]',
            'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            if selector.startswith('meta'):
                author_elem = soup.select_one(selector)
                if author_elem:
                    return author_elem.get('content', '')
            else:
                author_elem = soup.select_one(selector)
                if author_elem:
                    return author_elem.get_text(strip=True)
        
        return ""
    
    def _extract_publish_time(self, soup: BeautifulSoup) -> str:
        """提取发布时间"""
        time_selectors = [
            '.publish-time',
            '.post-time',
            '.date',
            'time',
            '[class*="time"]',
            '[class*="date"]',
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]'
        ]
        
        for selector in time_selectors:
            if selector.startswith('meta'):
                time_elem = soup.select_one(selector)
                if time_elem:
                    return time_elem.get('content', '')
            else:
                time_elem = soup.select_one(selector)
                if time_elem:
                    return time_elem.get_text(strip=True)
        
        return ""
    
    def _extract_summary(self, soup: BeautifulSoup) -> str:
        """提取文章摘要"""
        summary_selectors = [
            '.summary',
            '.excerpt',
            '.description',
            'meta[name="description"]',
            'meta[property="og:description"]'
        ]
        
        for selector in summary_selectors:
            if selector.startswith('meta'):
                summary_elem = soup.select_one(selector)
                if summary_elem:
                    return summary_elem.get('content', '')
            else:
                summary_elem = soup.select_one(selector)
                if summary_elem:
                    return summary_elem.get_text(strip=True)
        
        return ""
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """提取文章标签"""
        tags = []
        
        # 尝试多种标签选择器
        tag_selectors = [
            '.tags a',
            '.tag',
            '.category',
            '.keywords',
            'meta[name="keywords"]'
        ]
        
        for selector in tag_selectors:
            if selector.startswith('meta'):
                tag_elem = soup.select_one(selector)
                if tag_elem:
                    keywords = tag_elem.get('content', '')
                    if keywords:
                        tags.extend([tag.strip() for tag in keywords.split(',')])
            else:
                tag_elems = soup.select(selector)
                for tag_elem in tag_elems:
                    tag_text = tag_elem.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
        
        return list(set(tags))  # 去重
    
    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）【】""''""''，。！？；：]', '', text)
        return text.strip()
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """下载图片内容"""
        try:
            response = self.session.get(image_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 检查图片大小
            if len(response.content) > Config.MAX_IMAGE_SIZE:
                logger.warning(f"图片过大，跳过: {image_url}")
                return None
            
            return response.content
        except Exception as e:
            logger.error(f"下载图片失败: {image_url}, 错误: {str(e)}")
            return None

# 测试函数
if __name__ == "__main__":
    scraper = WebScraper()
    
    # 测试微信文章
    test_url = "https://mp.weixin.qq.com/s/example"
    result = scraper.scrape_article(test_url)
    
    print("文章标题:", result['title'])
    print("文章内容长度:", len(result['content']))
    print("图片数量:", len(result['images']))
    print("作者:", result['author'])
    print("发布时间:", result['publish_time'])

