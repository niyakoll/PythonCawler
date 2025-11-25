# lihkg_perfect_final_low_ram.py
import asyncio
import jmespath
import logging
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Response
import json
#from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("LIHKG")

# JMESPath 表達式
SEARCH_EXPR = """
response.items[].{url: join('', ['https://lihkg.com/thread/', to_string(thread_id)]), title: title}
"""
REPLY_EXPR = "response.items[].{post_id: post_id, author: user.nickname, gender: user.gender, message: msg, reply_time_hk: to_number(reply_time) | strftime('%Y-%m-%d %H:%M', 'Asia/Hong_Kong'), likes: like_count, dislikes: dislike_count, vote: vote_score}"
TITLE_EXPR = "response.thread.title"

class LIHKGScraper:
    def __init__(self):
        self.all_thread_urls = set()
        self.results = []
        self.playwright = None
        self.browser = None
        self.context = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="zh-HK",
            timezone_id="Asia/Hong_Kong",
            java_script_enabled=True,
            bypass_csp=True,
            # 關鍵！模擬真實香港用戶
            geolocation={"longitude": 114.1694, "latitude": 22.3193},
            permissions=["geolocation"],
        )
        # 正確！唯一有效嘅 stealth
        #await stealth.Stealth.apply_stealth_async(self,self.context)   # 唔使 await！就係咁簡單！
        #logger.info("單一 Browser 啟動完成（極省 RAM）")

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def search_keywords(self, keywords: List[str]):
        semaphore = asyncio.Semaphore(10)

        async def search_one(kw: str):
            async with semaphore:
                page = await self.context.new_page()
                try:
                    def on_response(resp: Response):
                        if "api_v2/thread" in resp.url and resp.status == 200:
                            asyncio.create_task(process(resp))

                    async def process(resp: Response):
                        try:
                            data = await resp.json()
                            if data.get("success") == 1:
                                print(f"data: {data}")
                                threads = jmespath.search(SEARCH_EXPR, data) or []
                                for t in threads:
                                    print(f"t: {t}")
                                    self.all_thread_urls.add(t["url"])

                                logger.info(f"「{kw}」搜到 {len(threads)} 個 → 總共 {len(self.all_thread_urls)} 個 thread")
                                return self.all_thread_urls
                        except Exception as e:
                            logger.info(f"process: {e}")

                    page.on("response", on_response)
                    await page.goto(f"https://lihkg.com/search?q={kw}", wait_until="networkidle", timeout=90000)
                    await asyncio.sleep(8)
                finally:
                    await page.close()

        await asyncio.gather(*[search_one(kw) for kw in keywords])
        logger.info(f"搜尋完成！共找到 {len(self.all_thread_urls)} 個唯一 thread")
    async def run(self, keywords: List[str]):
        await self.start()
        
            #start_time = datetime.now()
        await self.search_keywords(keywords)
    async def scrape_threads(self):
        semaphore = asyncio.Semaphore(8)

        async def scrape_one(url: str):
            async with semaphore:
                page = await self.context.new_page()
                try:
                    thread_id = url.split("/thread/")[1].split("/")[0]
                    replies = []
                    title = "未知"

                    def on_response(resp: Response):
                        if f"api_v2/thread/{thread_id}/page" in resp.url and resp.status == 200:
                            asyncio.create_task(process(resp))

                    async def process(resp: Response):
                        nonlocal title
                        try:
                            data = await resp.json()
                            if data.get("success") != 1:
                                return
                            t = jmespath.search(TITLE_EXPR, data)
                            if t and title == "未知":
                                title = t
                            return t
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
if __name__ == "__main__":
    scraper = LIHKGScraper()
    keywords = ["張敬軒"]
    asyncio.run(scraper.run(keywords))               
