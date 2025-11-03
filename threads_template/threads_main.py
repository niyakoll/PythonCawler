import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
import threading
import time
import schedule
import result_text_cleaning
from datetime import datetime
import math
import os 
import re
#Get setting from manifest json file
client = []
hour_range = 2
proxies = []
proxies_api_key = ""
path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    client = manifest["client"]
    hour_range = manifest['hour_range']
    proxies = manifest["proxies"]
    proxies_api_key = manifest["proxies_api_key"]

# Proxy configuration (replace with your Oxylabs credentials)



# specify the request headers
extra_headers = {
    'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept-Language': 'zh-HK,zh;q=0.9',
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
    result["viewCount"] = viewCount
        
        
        #result["reply_count"] = int(result["reply_count"].split(" ")[0])
    result["keyword"] = keyword
    uName = result["username"]
    cCode = result["code"]
    result["url"] = f"https://www.threads.net/@{uName}/post/{cCode}"
    return result

def hourDifferent(postTimeStamp)->int:
    timeDifferentHour = 24
    now = result_text_cleaning.timestampConvert(time.time())
    postTime = result_text_cleaning.timestampConvert(postTimeStamp)
    postyear = int(postTime[:4])
    postMonth = int(postTime[5:7])
    postDay = int(postTime[8:10])
    postHour = int(postTime[11:13])
    postMinute = int(postTime[14:16])
    postSecond = int(postTime[17:19])
    nowYear = int(now[:4])
    nowMonth = int(now[5:7])
    nowDay = int(now[8:10])
    nowHour = int(now[11:13])
    nowMinute = int(now[14:16])
    nowSecond = int(now[17:19])
    publishDay = datetime(year = postyear, month = postMonth, day = postDay,hour=postHour,minute= postMinute,second= nowSecond)
    today = datetime(year = nowYear, month= nowMonth, day= nowDay,hour=nowHour,minute= nowMinute, second= postSecond)
    if (today-publishDay).days != 0:
        timeDifferentHour = 24
    elif (today-publishDay).days == 0:
        timeDifferentHour = math.ceil((((today-publishDay).seconds)/60)/60)
    else:
        timeDifferentHour = 24
    #print(timeDifferentHour)
    return timeDifferentHour
def htmlToViewCount(html:str):
    viewCountpattern = r'"view_count[s]?":\s*(\d+)\s*}'  # Matches e.g., "view_count": 1200}
    try:
        viewCountList = re.findall(viewCountpattern, html, re.IGNORECASE)
        viewCount = str(viewCountList[0])
        
    except Exception as e:
        print(e)
        print("cannot find view count.")
    return viewCount
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
        viewCount = ""
        #viewCount = htmlToViewCount(page.content())
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
            #print(f"After json loads and nested lookup thread_items, there are total :{len(testHiddenSet3)} hidden sets.")

            # use our jmespath parser to reduce the dataset to the most important fields
            threads = [parse_thread(t,thread_keyword,viewCount) for thread in thread_items for t in thread]
            
            
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
        title =  reply["thread"]["text"]
        del reply["thread"]
        del reply["replies"][0]
        tempStorge[title].append(reply)
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
                url =f"https://www.threads.com/@{username}/post/{code}"
                add_hidden_comment(url,thread_keyword,tempStorge)
    except ValueError as e:
        print(f"Error in find_hidden_comment function: {e}")
    finally:
        return tempStorge
            
def search_one_keyword(keyword:str)->list:
    url_list = []
    searchType = ["serp_type=recent","filter=recent"]
    try:
        for type in searchType:
            #search_url = f"https://www.threads.com/search?q={keyword}&serp_type=recent"
            #time.sleep(1)
            search_url = f"https://www.threads.com/search?q={keyword}&{type}"
            search_result = scrape_thread(search_url,keyword)
            firstPost = search_result["thread"]
            firstPostUserName = firstPost["username"]
            firstPostCode = firstPost["code"]
            firstPostLike = firstPost["like_count"]
            firstPostReply = firstPost["direct_reply_count"]
            firstPostUrl = f"https://www.threads.com/@{firstPostUserName}/post/{firstPostCode}"
            #exclude some old posts
            postTimeStamp = firstPost["published_on"]
            hour = hourDifferent(postTimeStamp)
            #print(hour)
            #url_list.append(firstPostUrl)
            if hour > hour_range:
                print(f"{firstPostUrl}\nThis Post was published over {hour_range} hours!")
            else:
                url_list.append(firstPostUrl)
            

            for post in search_result["replies"]:
                postUserName = post["username"]
                postCode = post["code"]
                postLike = post["like_count"]
                postReply = post["direct_reply_count"]
                postUrl = f"https://www.threads.com/@{postUserName}/post/{postCode}"
                #exclude some old post
                postTimeStamp = post["published_on"]
                hour = hourDifferent(postTimeStamp)
                #print(hour)
                if hour > hour_range:
                    print(f"{postUrl}\nThis Post was published over {hour_range} hours!")
                else:
                    url_list.append(postUrl)

                    

                
    except ValueError as e:
        print(f"Error scraping keyword {keyword}: {e}")
    finally:
        return url_list

def search_one_keyword_all_comment(url_list:list,thread_keyword,tempStorge)->dict:
    i = 1
    try:
        if url_list != []:
            totalPosts = len(url_list)
            print(f"Keyword {thread_keyword} found {totalPosts} Posts in recent {hour_range} hours.")
            for postUrl in url_list:
                try:
                    print(f"Post{i} : {postUrl} start Listening... ")
                    output = scrape_thread(postUrl,thread_keyword)
                    tempStorge.append(output)
                    
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

def search_multiple_keyword(all_keyword_list:list,file_path,tempStorge)->dict:
    start = time.time()
    try:
        for keyword in all_keyword_list:
            time.sleep(2)
            try:
                print(f"Keyword {keyword} Start Listening...")
                url_list = search_one_keyword(keyword)
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
        totalPost = len(tempStorge)
        print(f"All keywords Listening finished, total {totalPost} Post collected.")
        end = time.time()
        timeTaken =int((end - start)/60)
        print(f"Total time taken: {timeTaken} minutes")
        return tempStorge


def scan(keyword_list_main):
    currentTime = result_text_cleaning.timestampConvert(time.time())
    print(f"{currentTime} : Start Working ...")
    print(f"{currentTime} : Distributing Keyword...")
    t = ThreadDistribue(keyword_list_main)
    #print(f"Total of {len(keyword_list_main)} keywords, each thread scans {len(t["t1"])} keywords...")
    t1 = threading.Thread(target=search_multiple_keyword, args=(t["t1"],str(os.path.join(os.path.dirname(__file__),"result","searchResult1.json")),tempStorge1))
    t2 = threading.Thread(target=search_multiple_keyword, args=(t["t2"],str(os.path.join(os.path.dirname(__file__),"result","searchResult2.json")),tempStorge2))
    t3 = threading.Thread(target=search_multiple_keyword, args=(t["t3"],str(os.path.join(os.path.dirname(__file__),"result","searchResult3.json")),tempStorge3))
    t4 = threading.Thread(target=search_multiple_keyword, args=(t["t4"],str(os.path.join(os.path.dirname(__file__),"result","searchResult4.json")),tempStorge4))
    t5 = threading.Thread(target=search_multiple_keyword, args=(t["t5"],str(os.path.join(os.path.dirname(__file__),"result","searchResult5.json")),tempStorge5))
    t6 = threading.Thread(target=search_multiple_keyword, args=(t["t6"],str(os.path.join(os.path.dirname(__file__),"result","searchResult6.json")),tempStorge6))
    t7 = threading.Thread(target=search_multiple_keyword, args=(t["t7"],str(os.path.join(os.path.dirname(__file__),"result","searchResult7.json")),tempStorge7))
    t8 = threading.Thread(target=search_multiple_keyword, args=(t["t8"],str(os.path.join(os.path.dirname(__file__),"result","searchResult8.json")),tempStorge8))
    t9 = threading.Thread(target=search_multiple_keyword, args=(t["t9"],str(os.path.join(os.path.dirname(__file__),"result","searchResult9.json")),tempStorge9))
    t10 = threading.Thread(target=search_multiple_keyword, args=(t["t10"],str(os.path.join(os.path.dirname(__file__),"result","searchResult10.json")),tempStorge10))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t9.start()
    t10.start()
    
    currentTime = result_text_cleaning.timestampConvert(time.time())
    print(f"{currentTime} : Scanning Started.")
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    t9.join()
    t10.join()
    currentTime = result_text_cleaning.timestampConvert(time.time())
    print(f"{currentTime} : Scanning Finished.")

#seperate the keywork list and distribute equally to each thread(total ten threads)    
def ThreadDistribue(keyword_list_main): 
    totalKeyword = len(keyword_list_main)
    keywordPerThread = 0
    lastThread = 0
    if totalKeyword%10 == 0:
        keywordPerThread = int(totalKeyword/10)
    else:
        keywordPerThread = math.floor(totalKeyword/9)
    threadKeywordList = {"t1":keyword_list_main[:keywordPerThread],
                         "t2":keyword_list_main[keywordPerThread:keywordPerThread*2],
                         "t3":keyword_list_main[keywordPerThread*2:keywordPerThread*3],
                         "t4":keyword_list_main[keywordPerThread*3:keywordPerThread*4],
                         "t5":keyword_list_main[keywordPerThread*4:keywordPerThread*5],
                         "t6":keyword_list_main[keywordPerThread*5:keywordPerThread*6],
                         "t7":keyword_list_main[keywordPerThread*6:keywordPerThread*7],
                         "t8":keyword_list_main[keywordPerThread*7:keywordPerThread*8],
                         "t9":keyword_list_main[keywordPerThread*8:keywordPerThread*9],
                         "t10":keyword_list_main[keywordPerThread*9:]
                         }
    return threadKeywordList

#if __name__ == "__main__":        