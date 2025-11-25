# bk_scraper_PRODUCTION.py - FINAL VERSION - SAME AS LIHKG STYLE
import asyncio
import json
import logging
import html
import re
from datetime import datetime
from typing import List, Dict
from playwright.async_api import async_playwright
import os
import shortuuid
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("BK")
def gen_unique_id():
    return shortuuid.uuid()
def strToNum(rawStr:str)->list:
    rawStr = rawStr.split(" ")
    li = []
    for num in rawStr:
        try:
            int(num)
            li.append(num)
        except Exception:
            continue
    return li
def bk_time_to_timestamp(time_str: str) -> int:
    """
    把 Baby Kingdom 的時間字串轉成 Unix timestamp (秒)
    支援兩種格式：
    - "25-11-25 11:07"     → 2025-11-25 11:07
    - "2025-11-25 14:07:31" → 直接轉
    """
    try:
        if len(time_str) <= 14:  # 短格式 "25-11-25 11:07"
            dt = datetime.strptime(time_str, "%y-%m-%d %H:%M")
            # 自動補 20xx 年
            if dt.year < 2000:
                dt = dt.replace(year=dt.year + 2000)
        else:  # 長格式 "2025-11-25 14:07:31"
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        
        return int(dt.timestamp())  # 轉成整數秒
    except Exception as e:
        print(f"時間解析失敗: {time_str} | 錯誤: {e}")
        return int(datetime.now().timestamp())  # 失敗就用現在時間
class BabyKingdomScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1600, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="zh-HK",
        )
        await self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        logger.info("Baby Kingdom scraper started - ONE BROWSER MODE")

    async def close(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    def is_within_hours(self, time_str: str, max_hours: int) -> bool:
        """Correctly parse BK time: 25-11-24 15:47 → 2025-11-24 15:47"""
        try:
            match = re.search(r'(\d{2})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2})', time_str)
            if not match:
                logger.warning(f"Time format not matched: {time_str}")
                return True  # fallback

            year2d, month, day, hour, minute = map(int, match.groups())
            year = 2000 + year2d
            post_dt = datetime(year, month, day, hour, minute)
            now = datetime.now()
            hours_diff = (now - post_dt).total_seconds() / 3600

            logger.info(f"Time check: {time_str} → {post_dt} | Diff: {hours_diff:.1f}h | Max: {max_hours}h → {'OK' if hours_diff <= max_hours else 'SKIP'}")
            return hours_diff <= max_hours
        except Exception as e:
            logger.error(f"Time parse failed: {time_str} | Error: {e}")
            return True

    async def search_and_scrape(self, keyword: str, max_hours: int = 48) -> List[Dict]:
        page = await self.context.new_page()
        results = []

        try:
            try:
                search_url = f"https://www.baby-kingdom.com/search.php?mod=forum&srchtxt={keyword}&searchsubmit=yes&kw={keyword}&orderby=lastpost&ascdesc=desc&range_time=days&srchfrom=86400"
                logger.info(f"[{keyword}] Searching: {search_url}")
                await page.goto(search_url, wait_until="domcontentloaded", timeout=90000)
            except Exception as e:
                print(f"page can not load")
            await asyncio.sleep(2)
            try:
                rows = []
                await page.wait_for_selector("li.pbw", timeout=30000)
                rows = await page.query_selector_all("li.pbw")
                #print(rows)
                logger.info(f"[{keyword}] Found {len(rows)} threads")
            except Exception as e:
                pass
                #print(e)
            if rows:
                for row in rows:
                    try:
                        title_elem = await row.query_selector("h3 a")
                        if not title_elem: continue
                        title = await title_elem.inner_text()
                        href = await title_elem.get_attribute("href")
                        url =  href if href else ""
                        url = html.unescape(url)
                        

                        info_p = await row.query_selector("p:has(span)")
                        info_text = await info_p.inner_text() if info_p else ""
                        time_match = re.search(r'(\d{2}-\d{1,2}-\d{1,2} \d{1,2}:\d{2})', info_text)
                        time_str = time_match.group(1) if time_match else ""

                        if not self.is_within_hours(time_str, max_hours):
                            continue

                        # Extract reply & view count
                        cm_view_p_elem = await row.query_selector("p.xg1")
                        cm_view_p = await cm_view_p_elem.inner_text()
                        #print(f"cm and view text: {cm_view_p}")
                        li = strToNum(cm_view_p)
                        commentCount = li[0] or 0
                        viewCount = li[1] or 0
                        #print(commentCount)
                        # Scrape full thread
                        #print(f"target url: {url}")
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        await asyncio.sleep(2)

                        posts = []
                        while True:
                            post_elems = await page.query_selector_all("div.plc")
                            
                            for elem in post_elems:
                                try:
                                    author = await (await elem.query_selector("a.fwb")).inner_text()
                                except:
                                    author = "匿名"
                                try:
                                    time_elem = await elem.query_selector('em[id^="authorposton"] span[title]')
                                    post_time = ""
                                    if time_elem:
                                        post_time = await time_elem.get_attribute("title")   # 例如 "25-11-25 11:07"
                                        #print(f"postTime: {post_time}")
                                    else:
                                        # 備用：直接抓 em 裡面的文字，再用正則擷取
                                        em = await page.query_selector('em[id^="authorposton"]')
                                        if em:
                                            text = await em.inner_text()
                                            
                                            m = re.search(r'(\d{2}-\d{1,2}-\d{1,2} \d{1,2}:\d{2})', text)
                                            if m:
                                                post_time = m.group(1)
                                except:
                                    post_time = "not found"

                                #if not self.is_within_hours(time_text, max_hours):
                                    #continue

                                content_elem = await elem.query_selector("div.t_f span")
                                
                                comment = ""
                                if content_elem:
                                    comment = await content_elem.inner_text()
                                    comment = comment.strip()
                                    #print(f"comment: {comment}")
                                if comment == "":
                                    continue
                                
                                try:
                                    posts.append({
                                        "source": "BabyKingdom",
                                        "link": url,
                                        "keyword": keyword,
                                        "title": title.strip(),
                                        "commentid": gen_unique_id(),
                                        "comment": comment or "[No content]",
                                        "postid": url.split("tid=")[-1].split("&")[0],
                                        "releaseDate": post_time,
                                        "releaseDate_timeStamp":bk_time_to_timestamp(post_time),
                                        "updateTime_timeStamp":bk_time_to_timestamp(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "likeCount": "not_given",
                                        "commentCount": len(posts),
                                        "author": author,
                                        "gender": "",
                                        "dislikeCount": 0,
                                        "vote": 0
                                    })
                                except Exception as e:
                                    print(e)

                            next_btn = await page.query_selector("a.nxt")
                            if next_btn and "下一頁" in (await next_btn.inner_text()):
                                await next_btn.click()
                                await asyncio.sleep(1)
                            else:
                                break

                        results.append({
                            "url": url,
                            "data": {
                                "success": 1,
                                "response": {
                                    "title": title.strip(),
                                    "item_data": posts,
                                    "metadata": {
                                        "thread_id": url.split("tid=")[-1].split("&")[0],
                                        "create_time": bk_time_to_timestamp(time_str=time_str),
                                        "last_reply_time": int(datetime.now().timestamp()),
                                        "commentCount": commentCount,
                                        "viewCount": viewCount
                                    }
                                }
                            }
                        })
                        logger.info(f"[{keyword}] DONE: {title[:50]}... → {len(posts)} comments")

                    except Exception as e:
                        logger.warning(f"Thread error: {e}")

        finally:
            await page.close()

        return results

    async def run(self, keywords: List[str], max_hours: int = 48, output_file: str = "bk_result.json"):
        await self.start()
        final_output = {kw: [] for kw in keywords}

        try:
            tasks = [self.search_and_scrape(kw, max_hours) for kw in keywords]
            all_results = await asyncio.gather(*tasks)

            for kw, results in zip(keywords, all_results):
                final_output[kw] = results

            path = os.path.join(os.path.dirname(__file__), "result", output_file)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, ensure_ascii=False, indent=4)
            logger.info(f"ALL DONE! Saved to {output_file}")

        finally:
            await self.close()

async def scraper(keyword_list,max_hours,output_file):
    scraper = BabyKingdomScraper()
    #asyncio.run(scraper.run(keyword_list, max_hours=max_hours,output_file=output_file))
    await scraper.run(keyword_list, max_hours=max_hours, output_file=output_file)