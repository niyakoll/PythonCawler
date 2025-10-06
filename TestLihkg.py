import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
import threading
import time

extra_headers = {
    'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept-Language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com/',
    "Cache-Control": "no-cache"
    
}
cache_header = "'Cache-Control': 'max-age=31536000'"

def scrape_lihkg(url: str) -> dict:
    """Scrape Threads post and replies from a given URL"""
    
    with sync_playwright() as pw:
        # start Playwright browser
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        
        page = context.new_page()
        cdp_session = context.new_cdp_session(page)
        # Enable network domain
        #cdp_session.send("Network.enable")
        cdp_session.send("Network.clearBrowserCookies")
        cdp_session.send("Network.setExtraHTTPHeaders", {"headers": extra_headers})
        # Clear browser cache
        cdp_session.send("Network.clearBrowserCache")
        #page.set_extra_http_headers(extra_headers)

        # go to url and wait for the page to load
        page.goto(url)
        # wait for page to finish loading
        #page.wait_for_selector("[data-pressable-container=true]")
        # find all hidden datasets
        time.sleep(3)
        selector = Selector(page.content())
        #hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        hidden_datasets = selector.css('<script').getall()
        #print(f"Originally, there are total :{len(hidden_datasets)} hidden sets.")
        print(len(hidden_datasets))
        
        #print(hidden_datasets)
        # find datasets that contain threads data
        for hidden_dataset in hidden_datasets:
            print(len(hidden_dataset))
            # skip loading datasets that clearly don't contain threads data
            #if '"ScheduledServerJS"' not in hidden_dataset:
                #continue
            #testHiddenSet1.append(hidden_dataset)
            #print(f"After filting ScheduledServerJS(not include), there are total :{len(testHiddenSet1)} hidden sets.")
            #if keyword not in hidden_dataset:
                #continue
            #if "thread_items" not in hidden_dataset:
                #continue
            #testHiddenSet2.append(hidden_dataset)
            #print(f"After filting thread_items(not include), there are total :{len(testHiddenSet2)} hidden sets.")
            #data = json.loads(hidden_dataset)
            data = hidden_dataset
            # datasets are heavily nested, use nested_lookup to find 
            # the thread_items key for thread data
            #thread_items = nested_lookup("thread_items", data)
            
            #print(thread_items)
            #if not thread_items:
                #continue
            #if thread_keyword not in str(thread_items):
                #continue
            
            

            # use our jmespath parser to reduce the dataset to the most important fields
            #threads = [parse_thread(t) for thread in thread_items for t in thread]
            
            
            return {
                hidden_datasets
                # the first parsed thread is the main post:
                #"thread": threads[0],
                # other threads are replies:
                #"replies": threads[1:],
            }
        raise ValueError("could not find thread data in page")
    page.close()
    browser.close()

data = scrape_lihkg("https://lihkg.com/thread/3439405/page/1")
print(data)