import asyncio
import json
import logging
import datetime
from typing import List, Dict, Any
import jmespath
from playwright.async_api import async_playwright, Response, TimeoutError
import time
import os
import math
import pytz
import threading
from lihkg_scraper import scraper
# === read manifest.json (only once) ===
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
    manifest = json.load(f)
    max_hours = manifest["hour_range"] or 2  
# Set up logging for debugging and progress tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("LIHKGScraper")


def timestampConvert(timeStamp):
    # Step 3: Convert timestamp to UTC datetime
    utc_dt = datetime.datetime.fromtimestamp(timeStamp, tz=pytz.UTC)
    # Step 4: Convert to Hong Kong timezone
    hk_timezone = pytz.timezone('Asia/Hong_Kong')
    hk_dt = utc_dt.astimezone(hk_timezone)
    # Step 5: Format the datetime to a readable string
    readable_dt = hk_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    return readable_dt



def combineList():
    clientList = []
    keyword_list_main = []
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    with open(path, 'r',encoding="utf-8") as file:
        manifest = json.load(file)
        clientList = manifest["client"]
        client_panel = manifest["client_panel"]
        for client in clientList:
            if client_panel[client]["threads_run"] == False:
                continue
            keyword_list_main.extend(client_panel[client]["keyword"])    
    return keyword_list_main
def ThreadDistribue(keyword_list_main): 
    totalKeyword = len(keyword_list_main)
    keywordPerThread = 0
    lastThread = 0
    if totalKeyword%5 == 0:
        keywordPerThread = int(totalKeyword/5)
    else:
        keywordPerThread = math.floor(totalKeyword/4)
    threadKeywordList = {"t1":keyword_list_main[:keywordPerThread],
                         "t2":keyword_list_main[keywordPerThread:keywordPerThread*2],
                         "t3":keyword_list_main[keywordPerThread*2:keywordPerThread*3],
                         "t4":keyword_list_main[keywordPerThread*3:keywordPerThread*4],
                         "t5":keyword_list_main[keywordPerThread*4:]
                         }
    return threadKeywordList

def run_scraper(keyword_list,max_hours, threading_id):
    async def inner():
        await scraper(
            keyword_list,
            max_hours,
            f"lihkg_result{threading_id}.json"
        )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(inner())
    finally:
        loop.close()
# Example usage
def scan():
    currentTime = timestampConvert(time.time())
    keyword_list_main = combineList()
    print(f"{currentTime} : Start Working ...")
    print(f"{currentTime} : Distributing Keyword...")
    print(keyword_list_main)
    t = ThreadDistribue(keyword_list_main)
    #print(f"Total of {len(keyword_list_main)} keywords, each thread scans {len(t["t1"])} keywords...")
    t1 = threading.Thread(target=run_scraper, args=(t["t1"],max_hours,1))
    t2 = threading.Thread(target=run_scraper, args=(t["t2"],max_hours,2))
    t3 = threading.Thread(target=run_scraper, args=(t["t3"],max_hours,3))
    t4 = threading.Thread(target=run_scraper, args=(t["t4"],max_hours,4))
    t5 = threading.Thread(target=run_scraper, args=(t["t5"],max_hours,5))
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    
    currentTime = timestampConvert(time.time())
    print(f"{currentTime} : Scanning Started.")
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    
    currentTime = timestampConvert(time.time())
    print(f"{currentTime} : Scanning Finished.")
if __name__ == "__main__":
    scan()