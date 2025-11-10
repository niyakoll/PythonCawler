import threads_main
import json
from nested_lookup import nested_lookup
from datetime import datetime
import pytz
import time
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  
import re  
import urllib.request, urllib.error 
#import xlwt  
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#import excel_data as ex
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
def cleanOldRecord(clientName:str,timeRange:int):
    data = {}
    dropData = {}
    outDateUrlList = []
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            data = json.load(file)
            if data != {}:
                for url in data.values():
                #86400s = 24 hours, 3600s = 1 hour
                    if time.time() - url["postTimeStamp"] > timeRange:
                        recordUrl = url['postUrl']
                        print(f"{recordUrl} is older than 3 hours.")
                        outDateUrlList.append(url['postUrl'])
                    else:
                        recordUrl = url['postUrl']
                        print(f"{recordUrl} is within 3 hours.")
        for outDateUrl in outDateUrlList:
            #dropData.append(data[outDateUrl])
            data.pop(outDateUrl, None)
            
        
        
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(data, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
        
    except IOError as e:
        print(e)

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
    cleanOldRecord(clientName=clientName,timeRange=90000) #clean old record older than 25 hours
    now = timestampConvert(time.time())
    print(f"{now} : Start Cleaning Data.")
    outputRecord = {}
    recordUrl = []
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            outputRecord = json.load(file) 
    except Exception as e:
        try:
            outputRecord = {}
            with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
                json.dump(outputRecord, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
        except IOError as e:
            print(e)
        print(e)
    clientKeywordList = findClientKeywordList(clientName)
    inputAiText = ""
    for r in range(1,11):
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{resultFileName}{r}.json")), 'r',encoding="utf-8") as file:
            result = json.load(file)
            if result != []:
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
                        commentList = []
                        commentObject = {}
                        reply = post["replies"]
                        for comment in reply:
                            commentText = comment["text"]
                            commentTimeStamp = comment["published_on"]
                            commentid = comment["id"]
                            commentKeyword = comment["keyword"]
                            commentTime = timestampConvert(commentTimeStamp)
                            commentLikeCount = comment["like_count"]
                            commentUrl = comment["url"]
                            commentReplyCount = comment["direct_reply_count"]
                            commentObject = {
                                "commentTimeStamp":commentTimeStamp,
                                "commentid":commentid,
                                "commentKeyword":commentKeyword,
                                "text":commentText,
                                "commentTime":commentTime,
                                "commentUrl":commentUrl,
                                "commentLikeCount":commentLikeCount,
                                "commentReplyCount":commentReplyCount,
                                "updateTime":time.time(),
                                "reply":[]
                            }
                            commentList.append(commentObject)
                    except Exception as e:
                        print(e)
                    try:
                        if len(outputRecord) == 0: #do not contain any record
                            print("no record")
                            threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postid":postId,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time(),
                                        "reply":commentList    
                                    }
                            outputRecord[postUrl] = threadPost
                            if postUrl not in inputAiText:
                                inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                            print("add the first record")
                        else: #have record
                            for outputRecordUrl in outputRecord.values(): #check each record
                                recordUrl.append(outputRecordUrl["postUrl"])
                                
                            if postUrl in recordUrl: #check if the post url is already in record
                                if (int(postLikeCount) <= int(outputRecord[postUrl]["postLikeCount"])) and  (int(postReplyCount) <= int(outputRecord[postUrl]["postReplyCount"])):
                                        readableTime = timestampConvert(outputRecord[postUrl]["updateTime"])
                                        print(f"{postUrl} last update at {readableTime}\nsame url, no update")
                                        #print(f"source from scanning: {postUrl}\nsource from record  : {outputRecord[postUrl]['postUrl']}")
                                        continue
                                else:
                                    outputRecord[postUrl]["postLikeCount"] = postLikeCount
                                    outputRecord[postUrl]["postReplyCount"] = postReplyCount
                                    outputRecord[postUrl]["updateTime"] = time.time()
                                    ouputRecordReadableTime = timestampConvert(outputRecord[postUrl]["updateTime"])
                                    print(f"{postUrl} at {ouputRecordReadableTime}\n same url, different like/reply count")
                                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                            else:
                                threadPost={
                                        "source":"Threads",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postTimeStamp,
                                        "postid":postId,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":postTime,
                                        "postUrl":postUrl,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postReplyCount,
                                        "updateTime":time.time(),
                                        "reply":commentList    
                                    }
                                if postUrl not in inputAiText:
                                    outputRecord[postUrl] = threadPost
                                    readableTime = timestampConvert(outputRecord[postUrl]["updateTime"])
                                    print(f"{postUrl} at {readableTime}\n find a new record")
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
                            
                        
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(outputRecord, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
    except IOError as e:
        print(e)   
    return inputAiText


    
def postList(resultFileName,clientName):
    now = timestampConvert(time.time())
    cleanData = {}
    finalOutput= {}
    updatePostList = ""
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            cleanData = json.load(file)
            #print(writeToMessage)
            urlList = []
            for message in cleanData.values():
                #urlList.append(url)
                #message = cleanData[url]
                source = message["source"]
                updateTime = message["updateTime"]
                postTimeStamp = message["postTimeStamp"]
                text  = message["text"]
                postKeyword  = message["postKeyword"]
                postTime  = message["postTime"]
                postUrl  = message["postUrl"]
                postLikeCount  = message["postLikeCount"]
                postReplyCount  = message["postReplyCount"]
                postReply = message["reply"]
                viewCount=""
                #viewCount= message["postViewCount"]
                #900s means 10 minutes (60*15),if the post information did not updated in 15 minutes, skip it.
                hrDifferent = threads_main.hourDifferent(postTimeStamp)
                if hrDifferent > hour_range:
                    continue
                if time.time() - updateTime > (interval * 60):
                    readableUpdateTime = timestampConvert(updateTime)
                    print(f"No update for post: {postUrl} since {readableUpdateTime}")
                    continue
                if"\n" in text:
                    text = text.split("\n")[0]
                #if viewCount != "":
                    #updatePostList += f"資料來源:{source}\n關鍵字:{postKeyword}\n瀏覽量: {viewCount}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                #else:
                updatePostList += f"資料來源:{source}\n關鍵字:{postKeyword}\n帖文標題: {text}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                finalOutputPost = {
                    
                        "postKeyword":postKeyword,
                        "text":text,
                        "likeCount":postLikeCount,
                        "replyCount":postReplyCount,
                        "link":postUrl,
                        "datetime":postTime,
                        "recordTime":timestampConvert(updateTime),
                        "type":"post",
                        "reply":[]
                    }
                finalOutput[postUrl] = finalOutputPost
                #print(finalOutput)
        with open(str(os.path.join(os.path.dirname(__file__),"result","finalOutput.json")), 'w',encoding="utf-8") as file:
            json.dump(finalOutput, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
            print(f"finalOutput.json successfully saved")                       
    except Exception as e:
        print("finalOutput.json fail to saved")  
        print(e)

    return updatePostList
def getGobalattrFromManifest(attr:str):
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    with open(path, 'r',encoding="utf-8") as file:
        manifest = json.load(file)
        result = manifest[attr]
    return result

def prepareOutputText(clientName:str,client_message_interval:int)->str:
    cleanData = {}
    AiinputText = ""
    postListMessage = ""
    finalOutput= {}
    
    
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            cleanData = json.load(file)
            for message in cleanData.values():
                #urlList.append(url)
                #message = cleanData[url]
                source = message["source"]
                updateTime = message["updateTime"]
                postTimeStamp = message["postTimeStamp"]
                title  = message["text"]
                postKeyword  = message["postKeyword"]
                postTime  = message["postTime"]
                postUrl  = message["postUrl"]
                postLikeCount  = message["postLikeCount"]
                postReplyCount  = message["postReplyCount"]
                postReply = message["reply"]
                replyTextList = ""
                if postReply != []:
                    for reply in postReply:
                        replyText = reply["text"]
                        replyLikeCount = reply["commentLikeCount"]
                        replyReplyCount = reply["commentReplyCount"]
                        replyTextList += f"留言: {replyText} (讚好數: {replyLikeCount}, 回覆數: {replyReplyCount})\n"
                
                viewCount=""
                #viewCount= message["postViewCount"]
                #900s means 10 minutes (60*15),if the post information did not updated in 15 minutes, skip it.
                hrDifferent = threads_main.hourDifferent(postTimeStamp)
                try:
                    hour_range = getGobalattrFromManifest("hour_range")
                    if client_message_interval != 15:
                        range = 0
                        client_message_interval_hour = int(client_message_interval/60)
                        range = hour_range + client_message_interval_hour
                        
                    else:
                        range = hour_range
                except Exception as e:
                    hour_range = 2
                
                if hrDifferent > range:
                    continue
                if time.time() - updateTime > (client_message_interval * 60):
                    readableUpdateTime = timestampConvert(updateTime)
                    print(f"No update for post: {postUrl} since {readableUpdateTime}")
                    continue
                if"\n" in title:
                    text = title.split("\n")[0]
                else:
                    text = title
                #if viewCount != "":
                    #updatePostList += f"資料來源:{source}\n關鍵字:{postKeyword}\n瀏覽量: {viewCount}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                #else:
                AiinputText += f"資料來源:{source}\n關鍵字:{postKeyword}\n帖文標題: {title}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n{replyTextList}\n"
                postListMessage += f"資料來源:{source}\n關鍵字:{postKeyword}\n帖文標題: {text}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n________\n"
                finalOutputPost = {
                    
                        "postKeyword":postKeyword,
                        "text":text,
                        "likeCount":postLikeCount,
                        "replyCount":postReplyCount,
                        "link":postUrl,
                        "datetime":postTime,
                        "recordTime":timestampConvert(updateTime),
                        "type":"post",
                        "reply":postReply
                    }
                finalOutput[postUrl] = finalOutputPost
                #print(finalOutput)
        with open(str(os.path.join(os.path.dirname(__file__),"result","finalOutput.json")), 'w',encoding="utf-8") as file:
            json.dump(finalOutput, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
            print(f"finalOutput.json successfully saved")                       
    except Exception as e:
        print("finalOutput.json fail to saved")  
        print(e)

    return AiinputText, postListMessage

   
