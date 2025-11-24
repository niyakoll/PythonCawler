import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import jmespath
from playwright.async_api import async_playwright, Response, TimeoutError
import time
import os
import math
import pytz
import threading
# Set up logging for debugging and progress tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("LIHKGScraper")

# JMESPath expressions for parsing API responses
# For search results: extract thread URLs, titles, and create_time
SEARCH_EXPR = """
response.items[].{
    url: join('', ['https://lihkg.com/thread/', to_string(thread_id), '/page/1']), 
    title: title,
    create_time: create_time
}
"""
# For thread details: extract title
TITLE_EXPR = "response.title"
# For thread replies: extract post details (reply_time kept as raw timestamp)
# Control the output json format of each comment
REPLY_EXPR = """
response.item_data[].{
    source: null,
    link: null,
    keyword: null,
    title: null,
    commentid: post_id,
    comment: msg,
    postid: null,
    releaseDate: reply_time,
    updateTime: null,
    likeCount: like_count,
    commentCount: null,
    author: user_nickname,
    gender: user_gender,
    dislikeCount: dislike_count,
    vote: vote_score
}
"""

class LIHKGScraper:
    """
    A class-based scraper for LIHKG using Playwright asynchronously.
    Manages one browser instance with multiple tabs to save RAM.
    Handles keyword searches to get URL lists per keyword, then scrapes thread details.
    """
    def __init__(self):
        # Initialize internal state
        self.playwright = None
        self.browser = None
        self.context = None
        self.keyword_to_urls: Dict[str, List[str]] = {}  # Will store {keyword: [url1, url2, ...]}

    async def start(self):
        """
        Start the Playwright browser and context.
        Configured to mimic a real Hong Kong user to avoid detection.
        """
        logger.info("Starting Playwright browser and context...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="zh-HK",
            timezone_id="Asia/Hong_Kong",
            java_script_enabled=True,
            bypass_csp=True,
            geolocation={"longitude": 114.1694, "latitude": 22.3193},
            permissions=["geolocation"],
        )
        # Add anti-detection script to mimic real browser
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-HK', 'zh', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {}, app: {}, webstore: {} };
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        """)
        logger.info("Browser and context started successfully.")

    async def close(self):
        """
        Cleanly close the context, browser, and Playwright instance.
        """
        logger.info("Closing browser and context...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser and context closed.")

    async def search_keywords(self, keywords: List[str], max_hours: int = 2) -> Dict[str, List[str]]:
        """
        Search for each keyword on LIHKG and collect unique thread URLs per keyword.
        Filters threads to only include those created within the last 'max_hours' hours.
        Uses semaphore to limit concurrent tabs (e.g., 10) to manage RAM.
        Returns a dict {keyword: [url1, url2, ...]}
        """
        self.keyword_to_urls = {}  # Reset
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent tabs

        async def search_one(keyword: str):
            async with semaphore:
                page = await self.context.new_page()
                keyword_urls = set()  # Use set to avoid duplicates per keyword
                try:
                    async def on_response(response: Response):
                        if "api_v2/thread" in response.url and response.status == 200:
                            try:
                                data = await response.json()
                                if data.get("success") == 1:
                                    threads = jmespath.search(SEARCH_EXPR, data) or []
                                    current_time = time.time()
                                    threshold = current_time - (max_hours * 3600)
                                    for thread in threads:
                                        try:
                                            create_time = int(thread.get("create_time", 0))
                                            if create_time > threshold:
                                                keyword_urls.add(thread["url"])
                                                logger.info(f"Added recent thread for '{keyword}': {thread['url']} (created at {create_time})")
                                            else:
                                                logger.info(f"Skipped old thread for '{keyword}': {thread['url']} (created at {create_time})")
                                        except ValueError:
                                            logger.warning(f"Invalid create_time for thread in '{keyword}': {thread.get('create_time')}")
                                    logger.info(f"Keyword '{keyword}': Found {len(threads)} threads. Added {len(keyword_urls)} recent ones.")
                            except Exception as e:
                                logger.error(f"Error processing search response for '{keyword}': {e}")
                    page.on("response", on_response)
                    search_url = f"https://lihkg.com/search?q={keyword}&sort=desc_create_time&type=thread"
                    logger.info(f"Searching for keyword '{keyword}' at {search_url}")
                    # Wait dynamically for the API response triggered by goto
                    async with page.expect_response(lambda response: "api_v2/thread" in response.url, timeout=30000) as response_info:
                        await page.goto(search_url, wait_until="networkidle", timeout=120000)
                    # Optionally: response = await response_info.value
                except TimeoutError:
                    logger.warning(f"Timeout waiting for API response for '{keyword}'. Proceeding with collected data.")
                except Exception as e:
                    logger.error(f"Error during search for '{keyword}': {e}")
                finally:
                    await page.close()
                self.keyword_to_urls[keyword] = list(keyword_urls)

        # Run searches concurrently
        await asyncio.gather(*[search_one(kw) for kw in keywords])
        logger.info(f"Keyword search completed. Found URLs for {len(self.keyword_to_urls)} keywords.")
        return self.keyword_to_urls

    async def scrape_thread(self,kw:str, url: str) -> Dict[str, Any]:
        """
        Scrape details for a single thread URL, handling multiple pages.
        Intercepts the API response to get thread data (title, items/posts).
        Returns the aggregated JSON data from all pages (as dict).
        """
        thread_data = {"success": 1, "response": {"title": "", "item_data": [], "metadata": {}}}  # Adjusted structure
        page_num = 1
        max_retries = 3
        thread_id = url.split("/thread/")[1].split("/")[0]

        while True:
            current_url = f"https://lihkg.com/thread/{thread_id}/page/{page_num}"
            actual_data = None
            for attempt in range(max_retries):
                page = await self.context.new_page()
                try:
                    async def on_response(response: Response):
                        nonlocal actual_data
                        if "api_v2/thread" in response.url and thread_id in response.url and response.status == 200:
                            try:
                                json_data = await response.json()
                                if json_data.get("success") and json_data["response"].get("item_data"):
                                    actual_data = json_data
                                    logger.info(f"Intercepted API data for {current_url} (attempt {attempt+1}): {len(json_data['response']['item_data'])} items")
                            except Exception as e:
                                logger.error(f"Error processing thread response for {current_url}: {e}")

                    page.on("response", on_response)
                    logger.info(f"Scraping thread page {page_num}: {current_url} (attempt {attempt+1})")
                    # Wait dynamically for a matching API response triggered by goto
                    async with page.expect_response(lambda response: "api_v2/thread" in response.url and thread_id in response.url, timeout=30000) as response_info:
                        await page.goto(current_url, wait_until="networkidle", timeout=120000)
                    # Optionally: response = await response_info.value

                    if actual_data:
                        break
                except TimeoutError:
                    logger.warning(f"Timeout waiting for API on {current_url} (attempt {attempt+1}). Retrying...")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error during scrape for {current_url} (attempt {attempt+1}): {e}")
                finally:
                    await page.close()
                if attempt == max_retries - 1:
                    logger.error(f"Failed to scrape {current_url} after {max_retries} attempts.")
                    return None  # Or handle partial data

            if not actual_data or not actual_data["response"].get("item_data"):
                logger.info(f"No more data for thread {thread_id} at page {page_num}. Stopping.")
                break

            # Use JMESPath to extract data
            if page_num == 1:
                thread_data["response"]["title"] = jmespath.search(TITLE_EXPR, actual_data) or ""
                # Extract other metadata flat from response
                metadata = {
                    "thread_id": jmespath.search("response.thread_id", actual_data),
                    "cat_id": jmespath.search("response.cat_id", actual_data),
                    "sub_cat_id": jmespath.search("response.sub_cat_id", actual_data),
                    "user_id": jmespath.search("response.user_id", actual_data),
                    "user_nickname": jmespath.search("response.user_nickname", actual_data),
                    "user_gender": jmespath.search("response.user_gender", actual_data),
                    "create_time": jmespath.search("response.create_time", actual_data),
                    "last_reply_time": jmespath.search("response.last_reply_time", actual_data),
                    # Add more as needed
                }
                thread_data["response"]["metadata"] = metadata

            # Extract replies using JMESPath
            replies = jmespath.search(REPLY_EXPR, actual_data) or []
            thread_data["response"]["item_data"].extend(replies)

            # Check for more pages
            total_pages = actual_data["response"].get("total_page", 1)
            if page_num >= total_pages:
                break
            page_num += 1

        # Post-process reply times (convert timestamp to HK time string) and set dynamic fields
        title = thread_data["response"]["title"]

        update_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        comment_count = (len(thread_data["response"]["item_data"])-1)
        #postLikeCount = thread_data["response"]["like_count"] or 0
        

        for item in thread_data["response"]["item_data"]:
            item["source"] = "Lihkg"
            item["keyword"] = kw
            item["title"] = title
            item["link"] = url
            item["postid"] = thread_id
            item["updateTime"] = time.time() #update_time_str for readable time format
            item["commentCount"] = comment_count
            if "releaseDate" in item:
                try:
                    ts = int(item["releaseDate"])
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(timezone(timedelta(hours=8)))  # HK is UTC+8
                    #item["releaseDate"] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    item["releaseDate"] = ts
                except ValueError:
                    item["releaseDate"] = "Invalid timestamp"

        if not thread_data["response"]["item_data"]:
            logger.warning(f"No data found for thread {thread_id}")
            return None
        return thread_data

    async def scrape_all_threads(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape details for all URLs collected in keyword_to_urls.
        Uses semaphore to limit concurrent tabs (e.g., 8).
        Returns {keyword: [thread_data1, thread_data2, ...]} where each thread_data is the aggregated API JSON.
        """
        if not self.keyword_to_urls:
            logger.warning("No URLs to scrape. Run search_keywords first.")
            return {}

        results: Dict[str, List[Dict[str, Any]]] = {kw: [] for kw in self.keyword_to_urls}
        semaphore = asyncio.Semaphore(8)  # Limit to 8 concurrent tabs

        async def scrape_one(kw: str, url: str):
            async with semaphore:
                data = await self.scrape_thread(kw, url)
                if data:
                    results[kw].append({"url": url, "data": data})

        # Flatten all (kw, url) pairs and scrape concurrently
        tasks = []
        for kw, urls in self.keyword_to_urls.items():
            for url in urls:
                tasks.append(scrape_one(kw, url))
        await asyncio.gather(*tasks)

        logger.info("All threads scraped.")
        return results

    async def run(self, keywords: List[str], max_hours: int = 2, output_file: str = "lihkg_results.json"):
        """
        Main workflow: Start browser, search keywords with time filter, scrape threads, save to JSON file, close.
        """
        start_time = datetime.now()
        await self.start()
        try:
            url_dict = await self.search_keywords(keywords, max_hours=max_hours)
            results = await self.scrape_all_threads()
            # Save to JSON file
            with open(str(os.path.join(os.path.dirname(__file__),"result",output_file)), "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error during run: {e}")
        finally:
            await self.close()
        logger.info(f"Total execution time: {datetime.now() - start_time}")

async def scraper(keyword_list,max_hours,output_file):
    scraper = LIHKGScraper()
    #asyncio.run(scraper.run(keyword_list, max_hours=max_hours,output_file=output_file))
    await scraper.run(keyword_list, max_hours=max_hours, output_file=output_file)
