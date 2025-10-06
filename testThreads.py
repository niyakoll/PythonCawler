import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
import threading
import time
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
tempStorge1 = []
tempStorge2 = []
tempStorge3 = []
tempStorge4 = []
tempStorge5 = []
tempStorge6 = []
tempStorge7 = []
tempStorge8 = []
tempStorge9 = []
tempStorge10 = []
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
        
        
        #result["reply_count"] = int(result["reply_count"].split(" ")[0])
        result["reply_count"] = 10
    result[
        "url"
    ] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
    return result


def scrape_thread(url: str,thread_keyword) -> dict:
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
        page.wait_for_selector("[data-pressable-container=true]")
        # find all hidden datasets
        selector = Selector(page.content())
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        #print(f"Originally, there are total :{len(hidden_datasets)} hidden sets.")
        
        
        #print(hidden_datasets)
        # find datasets that contain threads data
        for hidden_dataset in hidden_datasets:
            # skip loading datasets that clearly don't contain threads data
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            #testHiddenSet1.append(hidden_dataset)
            #print(f"After filting ScheduledServerJS(not include), there are total :{len(testHiddenSet1)} hidden sets.")
            #if keyword not in hidden_dataset:
                #continue
            if "thread_items" not in hidden_dataset:
                continue
            #testHiddenSet2.append(hidden_dataset)
            #print(f"After filting thread_items(not include), there are total :{len(testHiddenSet2)} hidden sets.")
            data = json.loads(hidden_dataset)
            
            # datasets are heavily nested, use nested_lookup to find 
            # the thread_items key for thread data
            thread_items = nested_lookup("thread_items", data)
            
            #print(thread_items)
            if not thread_items:
                continue
            if thread_keyword not in str(thread_items):
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


    
    

def writeJson(filePath:str,data:dict,tempStorge):
    try:
        with open(filePath, 'w',encoding="utf-8") as f:
            json.dump(data, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
        print(f"JSON file successfully created at: {filePath}")
    except IOError as e:
        print(f"Error creating JSON file at {filePath}: {e}")
    finally:
        return tempStorge

def add_hidden_comment(url: str,thread_keyword,tempStorge):
    try:
        reply = scrape_thread(url,thread_keyword)
        del reply["thread"]
        del reply["replies"][0]
        tempStorge.append(reply)
    except ValueError as e:
        print(f"Error in add_hidden_comment function: {e}")
    finally:
        return tempStorge
def find_hidden_comment(post:Dict,thread_keyword,tempStorge):
    try:
        for reply in post["replies"]:
            direct_reply_count = reply["direct_reply_count"]
            if direct_reply_count and direct_reply_count > 0:
                username = reply["username"]
                code = reply["code"]
                text = reply["text"]
                print(f"this comment {text} has {direct_reply_count} replies")
            #print(username)
            #print(code)
                url =f"https://www.threads.com/@{username}/post/{code}"
                #print(url)
                add_hidden_comment(url,thread_keyword,tempStorge)
    except ValueError as e:
        print(f"Error in find_hidden_comment function: {e}")
    finally:
        return tempStorge
            
def search_one_keyword(keword:str)->list:
    url_list = []
    try:
        search_url = f"https://www.threads.com/search?q={keword}&serp_type=recent"
        search_result = scrape_thread(search_url,keword)
        firstPost = search_result["thread"]
        firstPostUserName = firstPost["username"]
        firstPostCode = firstPost["code"]
        firstPostUrl = f"https://www.threads.com/@{firstPostUserName}/post/{firstPostCode}"
        url_list.append(firstPostUrl)
        for post in search_result["replies"]:
            postUserName = post["username"]
            postCode = post["code"]
            postUrl = f"https://www.threads.com/@{postUserName}/post/{postCode}"
            url_list.append(postUrl)
    except ValueError as e:
        print(f"Error scraping keyword {keword}: {e}")
    finally:
        return url_list

def search_one_keyword_all_comment(url_list:list,thread_keyword,tempStorge)->dict:
    i = 1
    try:
        if url_list != []:
            for postUrl in url_list:
                try:
                    output = scrape_thread(postUrl,thread_keyword)
                    tempStorge.append(output)
                    print(f"Post{i} start Listening... ")
                    i+=1
                except ValueError as e:
                    print(f"Error scraping post {postUrl}: {e}")
                    continue
                try:
                    find_hidden_comment(output,thread_keyword,tempStorge)
                except ValueError as e:
                    print(f"Error scraping hidden comments for post {postUrl}: {e}")
                    continue
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:

        return tempStorge

def search_multiple_keyword(keyword_list:list,file_path,tempStorge)->dict:
    start = time.time()
    try:
        for keyword in keyword_list:
            time.sleep(2)
            try:
                url_list = search_one_keyword(keyword)
                print(f"Keyword {keyword} Listening...")
            except ValueError as e:
                print(f"Error scraping keyword {keyword}: {e}")
                continue
            try:
                search_one_keyword_all_comment(url_list,keyword,tempStorge)
            except ValueError as e:
                print(f"Error scraping all comments for keyword {keyword}: {e}")
                continue
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        writeJson(file_path,tempStorge,tempStorge)
        print(f"All keywords Listening finished, total {len(tempStorge)} comments collected.")
        end = time.time()
        print(f"Total time taken: {end - start} seconds")
        return tempStorge





file_path = "C:/Users/Alex/threadOutput5.json"

#test_search = scrape_thread("https://www.threads.com/search?q=%E5%BC%B5%E5%A4%A9%E8%B3%A6&serp_type=recent")
#print(test_search)
#writeJson(r"C:/Users/Alex/threadSearchOutput.json",test_search)
if __name__ == "__main__":
    #output = scrape_thread("https://www.threads.com/@cantalkpop/post/DPIcpLNAT-_")
    #tempStorge.append(output)
    #find_hidden_comment(output)
    #writeJson(file_path,tempStorge)
    keyword_list1 = ["長實"]
    keyword_list2 = ["麥當奴"]
    t1 = threading.Thread(target=search_multiple_keyword, args=(keyword_list1,"C:/Users/Alex/stressTest3.json",tempStorge1))
    t2 = threading.Thread(target=search_multiple_keyword, args=(keyword_list2,"C:/Users/Alex/stressTest4.json",tempStorge2))
    t1.start()
    t2.start()
    print("All threads started.")

    