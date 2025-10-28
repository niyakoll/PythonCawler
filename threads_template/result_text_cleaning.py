import json
from nested_lookup import nested_lookup
from datetime import datetime
import pytz
import time
import os
import threads_main
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  #网页解析，获取数据
import re  #正则表达式，进行文字匹配
import urllib.request, urllib.error  #制定URL，获取网页数据
#import xlwt  #进行excel操作
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import excel_data as ex
#Get setting from manifest json file
client = ""
interval = 15
hour_range = 2
ai_agent_api_key = ""
ai_model = []
proxies = []

#write Excel File
filename = f"Data.xlsx"
sheetName = f"Data"

path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    client = manifest["client"]
    interval = manifest["interval"]
    hour_range = manifest["hour_range"]
    ai_agent_api_key = manifest["ai_agent_api_key"]
    ai_model = manifest["ai_model"]
    proxies = manifest["proxies"]
def timestampConvert(timeStamp):
    # Step 3: Convert timestamp to UTC datetime
    utc_dt = datetime.fromtimestamp(timeStamp, tz=pytz.UTC)
    # Step 4: Convert to Hong Kong timezone
    hk_timezone = pytz.timezone('Asia/Hong_Kong')
    hk_dt = utc_dt.astimezone(hk_timezone)
    # Step 5: Format the datetime to a readable string
    readable_dt = hk_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    return readable_dt

def findClientKeywordList(clientName):
    kList = []
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    with open(path, 'r',encoding="utf-8") as file:
        manifest = json.load(file)
        client_panel = manifest["client_panel"]
        kList.extend(client_panel[clientName]["keyword"])    
    return kList

def formatText(resultFileName,clientName)->str:
    now = timestampConvert(time.time())
    print(f"{now} : Start Cleaning Data.")
    outputRecord = {}
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            outputRecord = json.load(file)
    except Exception as e:
        print(e)
    clientKeywordList = findClientKeywordList(clientName)
    inputAiText = ""
    for r in range(1,11):
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{resultFileName}{r}.json")), 'r',encoding="utf-8") as file:
            result = json.load(file)
            if result != []:
                #print(len(posts))
                i = 0
                for post in result[:]:
                    postTitle = post["thread"]["text"]
                    postUrl = post["thread"]["url"]
                    postTimeStamp = post["thread"]["published_on"]
                    postTime = timestampConvert(postTimeStamp)
                    postId = post["thread"]["id"]
                    #postViewCount = post["thread"]["viewCount"]
                    postKeyword = post["thread"]["keyword"]
                    postLikeCount = post["thread"]["like_count"]
                    postReplyCount = post["thread"]["direct_reply_count"]
                    hrDifferent = threads_main.hourDifferent(postTimeStamp)
                    if hrDifferent > hour_range:
                        continue
                    if postKeyword not in clientKeywordList:
                        continue
                    try:
                        if len(outputRecord) == 0:
                            threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time()    
                                    }
                            outputRecord[postUrl] = threadPost
                            if postUrl not in inputAiText:
                                inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
 
                            #print("test no record")
                        for outputRecordUrl in outputRecord.values():
                            
                            if postUrl == outputRecordUrl["postUrl"]:
                                
                                if (int(postLikeCount) <= int(outputRecordUrl["postLikeCount"])) and  (int(postReplyCount) <= int(outputRecordUrl["postReplyCount"])):
                                    #print("same url, no update")
                                    continue
                                else:
                                    outputRecordUrl["postLikeCount"] = postLikeCount
                                    outputRecordUrl["postReplyCount"] = postReplyCount
                                    outputRecordUrl["updateTime"] = time.time()
                                    #print("test same url, different like/reply count")
                                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                            else:
                                threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time()    
                                    }
                                outputRecord[postUrl] = threadPost
                                #print("test new record")
                                if postUrl not in inputAiText:
                                    
                                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                    except Exception as e:
                        print(e)
                        reply = post["replies"]
                        for comment in reply:
                            commentText = comment["text"]
                            commentTimeStamp = comment["published_on"]
                            commentTime = timestampConvert(commentTimeStamp)
                            commentLikeCount = comment["like_count"]
                            commentUrl = comment["url"]
                            commentReplyCount = comment["direct_reply_count"]
                            inputAiText += f"留言: {commentText}(發佈時間: {commentTime})\n留言讚好數: {commentLikeCount}\n留言回覆數: {commentReplyCount}\n"
                            
                        i+=1
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(outputRecord, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
    except IOError as e:
        print(e)   
    return inputAiText


    
def postList(resultFileName,clientName):
    now = timestampConvert(time.time())
    outputRecord = {}
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            outputRecord = json.load(file)
    except Exception as e:
        print(e)
    clientKeywordList = findClientKeywordList(clientName)
    updatePostList = ""
    for r in range(1,11):
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{resultFileName}{r}.json")), 'r',encoding="utf-8") as file:
            result = json.load(file)
            if result != []:
                i = 1
                for post in result[:]:
                    #postViewCount = post["thread"]["viewCount"]
                    postTimeStamp = post["thread"]["published_on"]
                    postKeyword = post["thread"]["keyword"]
                    postTime = timestampConvert(postTimeStamp)
                    postUrl = post["thread"]["url"]
                    postLikeCount = post["thread"]["like_count"]
                    postReplyCount = post["thread"]["direct_reply_count"]
                    postTitle = post["thread"]["text"]
                    postId = post["thread"]["id"]
                    hrDifferent = threads_main.hourDifferent(postTimeStamp)
                    if hrDifferent > hour_range:
                        continue
                    if postKeyword not in clientKeywordList:
                        continue
                    """ postTitle = post["thread"]["text"]
                    if postTitle in result:
                        print(postTitle)
                        continue
                    if "\n" in postTitle: 
                        postTitle = postTitle.split("\n")[0] """
                    try:
                        if len(outputRecord) == 0:
                            threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time()    
                                    }
                            outputRecord[postUrl] = threadPost
                            #print("test no record 2") 
                        for outputRecordUrl in outputRecord.values():
                            if postUrl == outputRecordUrl["postUrl"]:
                                if (int(postLikeCount) <= int(outputRecordUrl["postLikeCount"])) and  (int(postReplyCount) <= int(outputRecordUrl["postReplyCount"])):
                                    #print("test same url, no update 2")
                                    continue
                                else:
                                    outputRecordUrl["postLikeCount"] = postLikeCount
                                    outputRecordUrl["postReplyCount"] = postReplyCount
                                    outputRecordUrl["updateTime"] = time.time()
                                    #print("test same url, different like/reply count 2")
                                    #if"\n" in postTitle:
                                        #postTitle = postTitle.split("\n")[0]
                                    #updatePostList += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                            else:
                                threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time()    
                                    }
                                outputRecord[postUrl] = threadPost
                                #print("test new record 2")
                                #if"\n" in postTitle:
                                    #postTitle = postTitle.split("\n")[0]
                                #updatePostList += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                    except Exception as e:
                        print(e)
                    """
                    viewCount = ""
                    try:
                        print()
                        print(f"{postUrl}\n scraping view count...")
                        #html = URLtoHTML(postUrl)
                        #viewCount = htmlToViewCount(html)

                    except Exception as e:
                        print(e)
                    
                    #updatePostList += f"關鍵字: {postKeyword}\n標題: {postTitle} \n瀏覽數量: {viewCount}\n發佈時間: {postTime}\n連結: {postUrl}\n讚好: {postLikeCount} 留言: {postReplyCount}\n________"
                    
                    try:
                        attr = ex.findAttrById(filename=filename,sheet_name=sheetName,id=postId)
                    except Exception as e:
                        print(e)
                    if attr == False:

                        updatePostList += f"關鍵字: {postKeyword}\n標題: {postTitle} \n發佈時間: {postTime}\n連結: {postUrl}\n讚好: {postLikeCount} 留言: {postReplyCount}\n________"
                    elif attr != False:
                        try:
                            if attr["likeCount"] == postLikeCount and attr["replyCount"] == postReplyCount:
                                print("This Post has no update!")
                            else:
                                inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                        except Exception as e:
                            print(e)
                    """

                    i+=1 
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(outputRecord, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
    except IOError as e:
        print(e)

    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            cleanData = json.load(file)
            #print(writeToMessage)
            urlList = []
            for url in cleanData:
                urlList.append(url)
                message = cleanData[url]
                source = message["source"]
                updateTime = message["updateTime"]
                postTimeStamp = message["postTimeStamp"]
                postTitle  = message["text"]
                postKeyword  = message["postKeyword"]
                postTime  = message["postTime"]
                postUrl  = message["postUrl"]
                postLikeCount  = message["postLikeCount"]
                postReplyCount  = message["postReplyCount"]
                viewCount=""
                #viewCount= message["postViewCount"]
                #900s means 10 minutes (60*15),if the post information did not updated in 15 minutes, skip it.
                hrDifferent = threads_main.hourDifferent(postTimeStamp)
                if hrDifferent > hour_range:
                    continue
                if time.time() - updateTime > 900:
                    print(f"test no update for post: {postTitle}")
                    continue
                
                
                if"\n" in postTitle:
                    postTitle = postTitle.split("\n")[0]
                #if viewCount != "":
                    #updatePostList += f"資料來源:{source}\n關鍵字:{postKeyword}\n瀏覽量: {viewCount}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                #else:
                updatePostList += f"資料來源:{source}\n關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                
    except Exception as e:
        print(e)

    return updatePostList
def URLtoHTML(url):
    #i = random.randint(0,3)
    #time.sleep(1)
    try:
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        #options.add_argument('user-agent="Mozilla/5.0"')
        options.add_argument("--headless=new")
        options.add_argument("--log-level=3")

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
        })
        driver.get(url)
        html = driver.page_source
        driver.quit()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        html = ""
    finally:
        return html

def htmlToViewCount(html:str):
    viewCountpattern = r'"view_count[s]?":\s*(\d+)\s*}'  # Matches e.g., "view_count": 1200}
    viewCountList = re.findall(viewCountpattern, html, re.IGNORECASE)
    viewCount = str(viewCountList[0])
    return viewCount



