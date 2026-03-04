import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, BrowserContext
import time

logger = logging.getLogger(__name__)

class WechatCrawler:
    """微信公众号爬虫"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def initialize(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        logger.info("浏览器已初始化")
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("浏览器已关闭")
    
    async def get_articles_list(self, account_id: str, max_pages: int = 5) -> List[dict]:
        """
        爬取公众号文章列表
        
        Args:
            account_id: 微信公众号ID
            max_pages: 最多爬取页数
        
        Returns:
            文章列表，每项包含: title, url, published_at, author
        """
        articles = []
        
        try:
            page = await self.context.new_page()
            page.set_default_timeout(self.timeout * 1000)
            
            # 访问公众号主页
            search_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin=0&count=5&type=9&query&token=&lang=zh_CN&searchscene&biz={account_id}"
            
            # 注：实际微信爬虫需要登录态，这里是简化示例
            # 真实场景需要集成登录流程或使用搜狗API
            logger.warning(f"微信直接爬虫需要登录态和反爬虫对策，示例URL: {search_url}")
            
            await page.close()
        
        except Exception as e:
            logger.error(f"爬取公众号 {account_id} 失败: {str(e)}")
            raise
        
        return articles
    
    async def get_article_content(self, url: str) -> Optional[dict]:
        """
        爬取文章全文内容
        
        Args:
            url: 文章URL
        
        Returns:
            文章内容和元数据
        """
        try:
            page = await self.context.new_page()
            page.set_default_timeout(self.timeout * 1000)
            
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(2)  # 等待JS渲染
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # 提取文章内容（微信页面结构）
            title = soup.select_one("h1.rich_media_title")
            content = soup.select_one("div.rich_media_content")
            publish_time = soup.select_one("span.rich_media_meta_text")
            author = soup.select_one("span.rich_media_meta_nickname")
            
            result = {
                "title": title.get_text(strip=True) if title else "Unknown",
                "content": str(content) if content else "",
                "plain_text": content.get_text(strip=True) if content else "",
                "published_at": datetime.now(),  # 需要从页面提取真实时间
                "author": author.get_text(strip=True) if author else None,
            }
            
            logger.info(f"成功爬取文章: {result['title']}")
            await page.close()
            return result
        
        except Exception as e:
            logger.error(f"爬取文章内容失败 {url}: {str(e)}")
            if page:
                await page.close()
            return None


# Sogou搜索API备选方案（不需要登录，风险低）
class SogouWechatCrawler:
    """搜狗微信搜索爬虫（推荐用于发现新文章）"""
    
    def __init__(self):
        self.base_url = "https://weixin.sogou.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def search_articles(self, keyword: str, page: int = 1) -> List[dict]:
        """
        通过搜狗搜索微信文章
        
        Args:
            keyword: 搜索关键词
            page: 页码
        
        Returns:
            搜索结果列表
        """
        # 实现调用搜狗API的逻辑
        # 注：搜狗API也有频率限制和反爬虫机制
        pass
