"""
🌐 网页内容抓取器
支持多平台文章内容提取，包括文字和图片

支持平台：
- 微信公众平台
- 小红书
- 知乎
- 微博
- 今日头条
- 其他主流平台
"""

import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import Config

# 设置日志
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
        
        # 平台特定的选择器配置
        self.platform_selectors = {
            'wechat': {
                'title': ['h1', '.rich_media_title', '#activity-name'],
                'content': ['#js_content', '.rich_media_content'],
                'author': ['.rich_media_meta_text', '.profile_nickname'],
                'time': ['.rich_media_meta_text', '#publish_time']
            },
            'zhihu': {
                'title': ['h1', '.QuestionHeader-title'],
                'content': ['.RichContent', '.AnswerItem'],
                'author': ['.AuthorInfo-name', '.UserLink-link'],
                'time': ['.ContentItem-time']
            },
            'weibo': {
                'title': ['h1', '.WB_text'],
                'content': ['.WB_text', '.WB_detail'],
                'author': ['.WB_info', '.WB_name'],
                'time': ['.WB_from', '.WB_time']
            },
            'xiaohongshu': {
                'title': ['.title', '.note-title'],
                'content': ['.content', '.note-content'],
                'author': ['.author', '.user-name'],
                'time': ['.time', '.publish-time']
            }
        }
    
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
            
            # 识别平台
            platform = self._identify_platform(url)
            
            # 提取文章信息
            article_info = {
                'url': url,
                'platform': platform,
                'title': self._extract_title(soup, platform),
                'content': self._extract_content(soup, platform),
                'images': self._extract_images(soup, url),
                'author': self._extract_author(soup, platform),
                'publish_time': self._extract_publish_time(soup, platform),
                'summary': self._extract_summary(soup),
                'tags': self._extract_tags(soup),
                'word_count': 0,  # 将在内容提取后计算
                'image_count': 0  # 将在图片提取后计算
            }
            
            # 计算统计信息
            article_info['word_count'] = len(article_info['content'])
            article_info['image_count'] = len(article_info['images'])
            
            logger.info(f"文章抓取完成: {article_info['title']} (字数: {article_info['word_count']}, 图片: {article_info['image_count']})")
            return article_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {url}, 错误: {str(e)}")
            return self._create_error_response(url, f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"抓取文章失败: {url}, 错误: {str(e)}")
            return self._create_error_response(url, str(e))
    
    def _identify_platform(self, url: str) -> str:
        """识别文章平台"""
        domain = urlparse(url).netloc.lower()
        
        if 'mp.weixin.qq.com' in domain:
            return 'wechat'
        elif 'zhihu.com' in domain:
            return 'zhihu'
        elif 'weibo.com' in domain:
            return 'weibo'
        elif 'xiaohongshu.com' in domain:
            return 'xiaohongshu'
        elif 'toutiao.com' in domain:
            return 'toutiao'
        else:
            return 'other'
    
    def _extract_title(self, soup: BeautifulSoup, platform: str) -> str:
        """提取文章标题"""
        # 尝试平台特定选择器
        if platform in self.platform_selectors:
            for selector in self.platform_selectors[platform]['title']:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    return title_elem.get_text(strip=True)
        
        # 通用选择器
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
                title = title_elem.get_text(strip=True)
                # 过滤掉网站名称
                if ' - ' in title:
                    title = title.split(' - ')[0]
                return title
        
        return soup.title.get_text(strip=True) if soup.title else ""
    
    def _extract_content(self, soup: BeautifulSoup, platform: str) -> str:
        """提取文章正文内容"""
        # 移除不需要的元素
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ad']):
            element.decompose()
        
        # 尝试平台特定选择器
        if platform in self.platform_selectors:
            for selector in self.platform_selectors[platform]['content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = self._clean_text(content_elem.get_text())
                    if len(content) > 100:  # 确保内容足够长
                        return content
        
        # 通用内容选择器
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
        
        # 1. 查找所有img标签
        img_tags = soup.find_all('img')
        
        # 2. 查找微信文章特有的图片元素
        wechat_imgs = soup.find_all(['img', 'div'], attrs={'data-src': True})
        
        # 3. 查找背景图片
        bg_imgs = soup.find_all(attrs={'style': re.compile(r'background-image')})
        
        # 合并所有图片元素
        all_img_elements = list(img_tags) + list(wechat_imgs) + list(bg_imgs)
        
        for img in all_img_elements:
            img_info = {
                'src': '',
                'alt': '',
                'title': '',
                'width': '',
                'height': '',
                'absolute_url': '',
                'type': 'img_tag'
            }
            
            # 获取图片属性
            if img.name == 'img':
                img_info['src'] = img.get('src', '') or img.get('data-src', '') or img.get('data-original', '')
                img_info['alt'] = img.get('alt', '')
                img_info['title'] = img.get('title', '')
                img_info['width'] = img.get('width', '')
                img_info['height'] = img.get('height', '')
                img_info['type'] = 'img_tag'
            else:
                # 处理其他元素
                img_info['src'] = img.get('data-src', '') or img.get('data-original', '')
                img_info['alt'] = img.get('alt', '')
                img_info['title'] = img.get('title', '')
                img_info['type'] = 'data_src'
                
                # 处理背景图片
                style = img.get('style', '')
                if 'background-image' in style:
                    bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
                    if bg_match:
                        img_info['src'] = bg_match.group(1)
                        img_info['type'] = 'background_image'
            
            # 转换为绝对URL
            if img_info['src']:
                img_info['absolute_url'] = urljoin(base_url, img_info['src'])
                
                # 过滤掉小图标和装饰性图片
                if self._is_valid_content_image(img_info):
                    images.append(img_info)
        
        # 去重（基于URL）
        seen_urls = set()
        unique_images = []
        for img in images:
            if img['absolute_url'] not in seen_urls:
                seen_urls.add(img['absolute_url'])
                unique_images.append(img)
        
        logger.info(f"找到 {len(unique_images)} 张有效图片")
        return unique_images
    
    def _is_valid_content_image(self, img_info: Dict) -> bool:
        """判断是否为有效的内容图片"""
        src = img_info['src'].lower()
        alt = img_info['alt'].lower()
        title = img_info.get('title', '').lower()
        
        # 过滤掉明显的非内容图片
        exclude_patterns = [
            'logo', 'icon', 'button', 'banner', 'ad', 'advertisement',
            'sponsor', 'sponsored', 'sidebar', 'header', 'footer', 'nav',
            'social', 'share', 'comment', 'like', 'follow', 'loading',
            'placeholder', 'blank', 'transparent', 'qrcode', 'qr-code',
            'wechat', 'weixin', 'follow', 'subscribe', 'decorative', 'divider'
        ]
        
        # 检查URL、alt、title中是否包含排除模式
        for pattern in exclude_patterns:
            if pattern in src or pattern in alt or pattern in title:
                return False
        
        # 过滤掉太小的图片（可能是装饰性图片）
        try:
            width = int(img_info['width']) if img_info['width'] else 0
            height = int(img_info['height']) if img_info['height'] else 0
            if width > 0 and height > 0 and (width < 100 or height < 100):
                return False
        except:
            pass
        
        # 保留封面图片
        if 'cover' in alt or 'cover' in title:
            return True
        
        # 对于微信文章，进一步判断
        if 'mp.weixin.qq.com' in src or 'mmecoa.qpic.cn' in src or 'mmbiz.qpic.cn' in src:
            # 微信文章的图片，但排除明显的头像和装饰图片
            if not alt and not title:
                try:
                    width = int(img_info['width']) if img_info['width'] else 0
                    height = int(img_info['height']) if img_info['height'] else 0
                    if width > 0 and height > 0 and (width < 200 or height < 200):
                        return False
                except:
                    pass
            
            # 对于微信文章，如果图片URL包含特定模式，可能是装饰图片
            decorative_patterns = [
                'avatar', 'head', 'profile', 'icon', 'logo', 'banner', 'ad'
            ]
            for pattern in decorative_patterns:
                if pattern in src:
                    return False
            
            return True
        
        return True
    
    def _extract_author(self, soup: BeautifulSoup, platform: str) -> str:
        """提取作者信息"""
        # 尝试平台特定选择器
        if platform in self.platform_selectors:
            for selector in self.platform_selectors[platform]['author']:
                author_elem = soup.select_one(selector)
                if author_elem:
                    return author_elem.get_text(strip=True)
        
        # 通用选择器
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
    
    def _extract_publish_time(self, soup: BeautifulSoup, platform: str) -> str:
        """提取发布时间"""
        # 尝试平台特定选择器
        if platform in self.platform_selectors:
            for selector in self.platform_selectors[platform]['time']:
                time_elem = soup.select_one(selector)
                if time_elem:
                    return time_elem.get_text(strip=True)
        
        # 通用选择器
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
    
    def _create_error_response(self, url: str, error_message: str) -> Dict:
        """创建错误响应"""
        return {
            'url': url,
            'error': error_message,
            'title': '',
            'content': '',
            'images': [],
            'author': '',
            'publish_time': '',
            'summary': '',
            'tags': [],
            'platform': 'unknown',
            'word_count': 0,
            'image_count': 0
        }


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
    print("平台:", result['platform'])