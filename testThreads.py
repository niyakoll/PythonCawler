import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
#from urllib.parse import quote

# specify the request headers
extra_headers = {
    'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept-Language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com/',
    "Cache-Control": "no-cache"
    
}
cache_header = "'Cache-Control': 'max-age=31536000'"
testHiddenSet1 = []
testHiddenSet2 = []
testHiddenSet3 = []
testHiddenSet4 = []
def parse_thread(data: Dict) -> Dict:
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
        reply_count: view_replies_cta_string,
        direct_reply_count: post.text_post_app_info.direct_reply_count,
        like_count: post.like_count,
        images: post.carousel_media[].image_versions2.candidates[1].url,
        image_count: post.carousel_media_count,
        videos: post.video_versions[].url
        
    }""",
        data,
    )
    result["videos"] = list(set(result["videos"] or []))
    if result["reply_count"] and type(result["reply_count"]) != int:
        #print(result["direct_reply_count"].split(" "))
        
        #result["reply_count"] = int(result["reply_count"].split(" ")[0])
        result["reply_count"] = 10
    result[
        "url"
    ] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
    return result


def scrape_thread(url: str) -> dict:
    """Scrape Threads post and replies from a given URL"""
    #keyword = quote("張天賦")
    keyword = ""
    #utf8_bytes = keyword.encode('utf-8')
    #print(utf8_bytes)
    
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
        page.wait_for_selector("[data-pressable-container=true]")
        # find all hidden datasets
        selector = Selector(page.content())
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        print(f"Originally, there are total :{len(hidden_datasets)} hidden sets.")
        
        
        #print(hidden_datasets)
        # find datasets that contain threads data
        for hidden_dataset in hidden_datasets:
            # skip loading datasets that clearly don't contain threads data
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            testHiddenSet1.append(hidden_dataset)
            print(f"After filting ScheduledServerJS(not include), there are total :{len(testHiddenSet1)} hidden sets.")
            #if keyword not in hidden_dataset:
                #continue
            if "thread_items" not in hidden_dataset:
                continue
            testHiddenSet2.append(hidden_dataset)
            print(f"After filting thread_items(not include), there are total :{len(testHiddenSet2)} hidden sets.")
            data = json.loads(hidden_dataset)
            
            # datasets are heavily nested, use nested_lookup to find 
            # the thread_items key for thread data
            thread_items = nested_lookup("thread_items", data)
            
            #print(thread_items)
            if not thread_items:
                continue
            if "張天賦" not in str(thread_items):
                continue
            testHiddenSet3.append(hidden_dataset)
            print(f"After json loads and nested lookup thread_items, there are total :{len(testHiddenSet3)} hidden sets.")

            # use our jmespath parser to reduce the dataset to the most important fields
            threads = [parse_thread(t) for thread in thread_items for t in thread]
            
            
            return {
                
                # the first parsed thread is the main post:
                "thread": threads[0],
                # other threads are replies:
                "replies": threads[1:],
            }
        raise ValueError("could not find thread data in page")
    page.close()
    browser.close()

def test(url: str,json_number:int):
    reply = scrape_thread(url)
    del reply["thread"]
    del reply["replies"][0]
    print(reply)
    file_path = fr"C:\Users\Alex\threadOutput{json_number}.json"
    try:
        with open(file_path, 'w',encoding="utf-8") as f:
        #json.dump(output, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
            json.dump(reply, f, indent=4,ensure_ascii=False) 
            print(f"JSON file successfully created at: {file_path}")
    except IOError as e:
        print(f"Error creating JSON file at {file_path}: {e}")

file_path = "C:/Users/Alex/threadOutput2.json"
with open(file_path, 'r',encoding="utf-8") as f:
    data = json.load(f)
    #print(data["replies"][0])
    for reply in data["replies"][4:5]:
        direct_reply_count = reply["direct_reply_count"]
        #print(direct_reply_count)
        if direct_reply_count and direct_reply_count > 0:
            username = reply["username"]
            code = reply["code"]
            text = reply["text"]
            print(f"this comment {text} has {direct_reply_count} replies")
            #print(username)
            #print(code)
            url =f"https://www.threads.com/@{username}/post/{code}"
            print(url)
            test(url,3)
            break






