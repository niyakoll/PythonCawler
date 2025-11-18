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
import datetime
import pytz
import logging
import math
import threading
from threads_main_async import search_multiple_keyword_async as scraper
import psutil

# === set up Logging ===
#logger.warning() -report on docker container
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === read manifest.json (only once) ===
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "manifest.json")
with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
    manifest = json.load(f)
# === get manifest.json variable (gobal setting)===

def hourDifferent(postTimeStamp):
    try:
        now = time.time()
        timeDistance = now - postTimeStamp
        timeDistance = int(timeDistance/60)
        #return time difference in seconds
    except Exception as e:
        print(f"threads_main compareTimeMinutes function error: {e}")
    hour = timeDistance/60
    #return hour in float (e.g. 1.54442323)
    return hour
    


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
def log_memory(label: str = ""):
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / 1024 / 1024  # Resident Set Size
    vms_mb = process.memory_info().vms / 1024 / 1024  # Virtual Memory
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp} CET] {label} RAM: {rss_mb:.1f} MB (RSS) | {vms_mb:.1f} MB (VMS)")
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

def run_scraper(keyword_list, threading_id):
    async def inner():
        await scraper(
            keyword_list,
            f"searchResult{threading_id}.json"
        )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(inner())
    finally:
        loop.close()

def scan():
    currentTime = timestampConvert(time.time())
    keyword_list_main = combineList()
    print(f"{currentTime} : Start Working ...")
    print(f"{currentTime} : Distributing Keyword...")
    print(keyword_list_main)
    t = ThreadDistribue(keyword_list_main)
    #print(f"Total of {len(keyword_list_main)} keywords, each thread scans {len(t["t1"])} keywords...")
    t1 = threading.Thread(target=run_scraper, args=(t["t1"],1))
    t2 = threading.Thread(target=run_scraper, args=(t["t2"],2))
    t3 = threading.Thread(target=run_scraper, args=(t["t3"],3))
    t4 = threading.Thread(target=run_scraper, args=(t["t4"],4))
    t5 = threading.Thread(target=run_scraper, args=(t["t5"],5))
    
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


