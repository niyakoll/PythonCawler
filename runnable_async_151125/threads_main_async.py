# threads_main_async.py
#use async playwright to scrape data
import json
import re
import time
import asyncio
import os
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from nested_lookup import nested_lookup
from parsel import Selector
import jmespath
import result_text_cleaning
import logging

# === set up Logging ===
#logger.warning() -report on docker container
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === read manifest.json (only once) ===
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
    manifest = json.load(f)
# === get manifest.json variable (gobal setting)===
# === post time range (discard all post that posted 2 hours ago)
hour_range = manifest["hour_range"]

extra_headers = {
    'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept-Language': 'zh-HK,zh;q=0.9',
    'referer': 'https://www.google.com/',
    "Cache-Control": "no-cache" 
}

def parse_thread(data: Dict,keyword:str,viewCount) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        text: post.caption.text,
        published_on: post.taken_at,
        id: post.id,
        pk: post.pk,
        code: post.code,
        username: post.user.username,
        user_pic: post.user.profile_pic_url,
        user_verified: post.user.is_verified,
        user_pk: post.user.pk,
        user_id: post.user.id,
        has_audio: post.has_audio,
        keyword: post.like_count,
        direct_reply_count: post.text_post_app_info.direct_reply_count,
        like_count: post.like_count,
        viewCount:post.like_count,
        images: post.carousel_media[].image_versions2.candidates[1].url,
        image_count: post.carousel_media_count,
        videos: post.video_versions[].url
        
        }""",
        data,
    )
    result["videos"] = list(set(result["videos"] or []))
    result["viewCount"] = viewCount or "0"
        
        
        #result["reply_count"] = int(result["reply_count"].split(" ")[0])
    result["keyword"] = keyword
    uName = result["username"]
    cCode = result["code"]
    result["url"] = f"https://www.threads.net/@{uName}/post/{cCode}"
    return result
def compareTimeInMinutes(TimeStamp):
    try:
        now = time.time()
        timeDistance = now - TimeStamp
        timeDistance = int(timeDistance/60)
        #return time difference in seconds
    except Exception as e:
        print(f"threads_main compareTimeMinutes function error: {e}")
    return timeDistance
def convertMinuteToHour(min):
    hour = min/60
    #return hour in float (e.g. 1.54442323)
    return hour
def checkCompoundKeyword(keyword:str,thread_item:str):
    haveKeyword = False
    try:
        if " " in keyword:
            compound_keyword_list = keyword.split(" ")
            if compound_keyword_list[0] in str(thread_item):
                haveKeyword = True
        else:
            if keyword in thread_item:
                haveKeyword = True
    except Exception as e:
        print(f"thread_main checkCompoundKeyword error ({keyword}): {e}")
    return haveKeyword
def htmlToViewCount(html:str):
    viewCountpattern = r'"view_count[s]?":\s*(\d+)\s*}'  # Matches e.g., "view_count": 1200}
    try:
        viewCountList = re.findall(viewCountpattern, html, re.IGNORECASE)
        viewCount = str(viewCountList[0])
        
    except Exception as e:
        print(e)
        print("cannot find view count.")
    return viewCount
# === scrape a single Threads url page (by url, match with keyword) ===
async def scrape_thread(page: Page, url: str, keyword: str) -> Dict[str, Any]:
    try:
        
        #await page.goto(url, timeout=40000)
        await page.goto(url, wait_until="networkidle", timeout=40000)
        #await page.wait_for_selector("[data-pressable-container=true]", timeout=15000)

        # 提取 view_count
        #viewCount = htmlToViewCount(await page.content())
        viewCount = ""
        #  read JSON data in threads
        hidden_jsons = await page.query_selector_all('script[type="application/json"][data-sjs]')
        for elem in hidden_jsons:
            content = await elem.inner_text()
            if '"ScheduledServerJS"' not in content or "thread_items" not in content:
                continue

            data = json.loads(content)
            thread_items = nested_lookup("thread_items", data)
            if not thread_items:
                continue
            if not checkCompoundKeyword(keyword, str(thread_items)):
                #print(f"have not contain keyword!")
                continue

            threads = [
                parse_thread(t, keyword, viewCount)
                for thread in thread_items
                for t in thread
            ]
            return {
                "thread": threads[0],
                "replies": threads[1:]
            }
        raise ValueError("No thread data found")
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        raise

# === search single keyword and retrun url list with keyword(dict) ===
async def search_one_keyword(keyword: str, context: BrowserContext) -> List[str]:
    url_list = []
    search_types = ["serp_type=recent", "filter=recent"]
    keyword_with_urlList = {}

    for stype in search_types:
        search_url = f"https://www.threads.com/search?q={keyword}&{stype}"
        page = await context.new_page()
        try:
            result = await scrape_thread(page, search_url, keyword)
            post = result["thread"]
            posthourDifference = convertMinuteToHour(compareTimeInMinutes(post["published_on"]))
            if posthourDifference <= hour_range:
                url_list.append(post["url"])
            

            for reply in result["replies"]:
                replyhourDifference = convertMinuteToHour(compareTimeInMinutes(reply["published_on"]))
                if replyhourDifference <= hour_range:
                    url_list.append(reply["url"])
                
        except Exception:
            pass
        finally:
            if len(url_list) != 0:
                keyword_with_urlList[keyword] = list(set(url_list))
            else:
                keyword_with_urlList[keyword] = []
            await page.close()
    return keyword_with_urlList  # remove deduplication

# === 刮取所有貼文 + 隱藏留言 ===
async def scrape_post_with_comments(context: BrowserContext, url: str, keyword: str) -> Dict:
    page = await context.new_page()
    try:
        post_data = await scrape_thread(page, url, keyword)
        # 這裡可加入 find_hidden_comment 邏輯（若需）
        return post_data
    finally:
        await page.close()

# === main Scraping Programming (multiple keywords)===
async def search_multiple_keyword_async(keyword_list: List[str], file_name: str) -> List[Dict]:
    results = []
    start_time = time.time()
    

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=True)
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=extra_headers,
            ignore_https_errors=True
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        await context.clear_cookies()

        # 並行搜尋所有關鍵字
        search_tasks = [
            search_one_keyword(kw, context) for kw in keyword_list
        ]
        url_lists = await asyncio.gather(*search_tasks, return_exceptions=True)
        #print(f"url_lists: {url_lists}")
        # 收集所有有效 URL
        keyword_url_pairs = []
        for item in url_lists:
            if isinstance(item, Exception):
                continue
            if isinstance(item, dict) and item:
                keyword_url_pairs.append(item)
        #print(f"all_urls: {all_urls}")
        logger.info(f"Found {len(keyword_url_pairs)} posts to scrape in detail.")

        # 並行刮取詳細內容（限制同時頁面數）
        semaphore = asyncio.Semaphore(8)  # 最多 8 個頁面同時開啟

        async def bounded_scrape(url,keyword):
            async with semaphore:
                return await scrape_post_with_comments(context, url, keyword)
        detail_tasks = []
        for keywordDict in keyword_url_pairs:
            keyword = next(iter(keywordDict))
            urlList = keywordDict[keyword]
            for url in urlList:
                detail_tasks.append(bounded_scrape(url,keyword))
        
        detailed_results = await asyncio.gather(*detail_tasks, return_exceptions=True)

        # 過濾成功結果
        for result in detailed_results:
            if not isinstance(result, Exception):
                results.append(result)

        await browser.close()

    # 寫入檔案
    os.makedirs(str(os.path.join(os.path.dirname(__file__),"result")), exist_ok=True)
    with open(str(os.path.join(os.path.dirname(__file__),"result",file_name)), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    elapsed = (time.time() - start_time) / 60
    logger.info(f"Scraped {len(results)} posts in {elapsed} minutes.")
    return results





    

    #filename = "searchResult1.json"
    #keyword_list = ["張天賦","陳蕾","張敬軒","莊思敏","湯令山","洪嘉豪","jacquelinchng","莊b敏","魏浚笙","殺手Jeffrey"]
    
    #asyncio.run(search_multiple_keyword_async(keyword_list,filename))