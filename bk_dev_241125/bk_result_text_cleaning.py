import json
import datetime
import pytz
import time
import os
import re   
import json
import sys
# 自動找到 shared 目錄（相對於目前檔案往上兩層）
SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
SHARED_DIR = os.path.abspath(SHARED_DIR)
# 把 shared 加入 import 路徑（給 pidlock 用）
if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

# 讀共用的 manifest.json
MANIFEST_PATH = os.path.join(SHARED_DIR, "manifest.json")
with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
    manifest = json.load(f)
client = ""
interval = 15
hour_range =2

client = manifest["client"]
interval = manifest["interval"]
hour_range = manifest["hour_range"]
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
def compareTimeInMinutes(TimeStamp):
    try:
        now = time.time()
        timeDistance = now - TimeStamp
        timeDistance = int(timeDistance/60)
        #print(f"minutes : {timeDistance}")
    except Exception as e:
        print(f"result_text_cleaning compareTimeMinutes function error: {e}")
    return timeDistance
def timestampConvert(timeStamp):
    # Step 3: Convert timestamp to UTC datetime
    utc_dt = datetime.datetime.fromtimestamp(timeStamp, tz=pytz.UTC)
    # Step 4: Convert to Hong Kong timezone
    hk_timezone = pytz.timezone('Asia/Hong_Kong')
    hk_dt = utc_dt.astimezone(hk_timezone)
    # Step 5: Format the datetime to a readable string
    readable_dt = hk_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    return readable_dt
def findClientKeywordList(clientName):
    kList = []
    #path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
        manifest = json.load(f)
        client_panel = manifest["client_panel"]
        kList.extend(client_panel[clientName]["keyword"])    
    return kList
def cleanOldRecord(clientName:str,timeRange:int):
    data = {}
    dropData = {}
    outDateUrlList = []
    
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            data = json.load(file)
            if data :
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
        print(f"result_text_cleaning cleanOldRecord: {e}")



def prepareOutputText(clientName:str,client_message_interval:int)->str:
    cleanData = {}
    AiinputText = ""
    postListMessage = ""
    finalOutput= {}
    
    
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
            cleanData = json.load(file)
            if cleanData:
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
                    postReply = message["reply"] or []
                    replyTextList = ""
                    if postReply:
                        for reply in postReply:
                            replyText = reply["text"]
                            replyLikeCount = reply["commentLikeCount"]
                            
                            replyTextList += f"留言: {replyText} (讚好數: {replyLikeCount}\n"
                    
                    viewCount=""
                    #viewCount= message["postViewCount"]
                    #900s means 10 minutes (60*15),if the post information did not updated in 15 minutes, skip it.
                    hrDifferent = hourDifferent(postTimeStamp)
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
        print(f"result_text_cleaning prepareOutputText: {e}")

    return AiinputText, postListMessage
def getGobalattrFromManifest(attr:str):
    with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
        manifest = json.load(f)
        result = manifest[attr]
    return result
                    
                


def formatText(resultFileName,clientName):
    client_message_interval = 15
    #path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    try:
        with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
            manifest = json.load(f)
            client_panel = manifest["client_panel"]
            client_message_interval = client_panel[clientName]["message_interval"]
    except Exception as e:
        client_message_interval = 240
        print(f"result_text_cleaning formatText read {clientName} message interval: {e}")
    try:
        clear_time_range = (client_message_interval + 240)*60
        clear_time_range = int(clear_time_range)
    except Exception as e:
        clear_time_range = 90000
        print(f"result_text_cleaning formatText cleaning {client} output record: {e}")
    #cleanOldRecord(clientName=clientName,timeRange=clear_time_range)
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
                json.dump(outputRecord, file, indent=4,ensure_ascii=False)
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'r',encoding="utf-8") as file:
                        outputRecord = json.load(file)
                except Exception as e:
                    print(e)
        except IOError as e:
            print(f"result_text_cleaning formatText write output Record 166(when json not exist): {e}")
        
    clientKeywordList = findClientKeywordList(clientName)
    
    inputAiText = ""
    for r in range(1,6):
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{resultFileName}{r}.json")), 'r',encoding="utf-8") as file:
            result = json.load(file)

            #if clientName not in result:
                #continue
            cl_kw = ""
            if result:
                try:
                    for kw in clientKeywordList:
                        if kw not in result:
                            continue
                        else:
                            cl_kw = kw
                            
                except Exception as e:
                    print(e)
                    continue
                if cl_kw == "":
                    continue
                #print(cl_kw)
            
                clientResult = result[cl_kw]
                if not clientResult:
                    continue
                
                for post_item in clientResult:
                    metadata = post_item["data"]["response"]["metadata"]
                    postSource = "babyKindom"
                    postKeyword = cl_kw
                    postlink = post_item["url"]
                    postTitle = post_item["data"]["response"]["title"]
                    postid = metadata["thread_id"]
                    postReleaseDate = metadata["create_time"]
                    postUpdateTime = metadata["last_reply_time"]
                    postLikeCount = "N.A."
                    postCommentCount = metadata["commentCount"]
                    postAuthor = "N.A."
                    postDislikeCount = "N.A."
                    postViewCount = metadata["viewCount"]
                    
                    hrDifferent = hourDifferent(postReleaseDate)
                    #print(f"clientKeywordList: {clientKeywordList}")
                    if postKeyword not in clientKeywordList:
                        continue
                    if hrDifferent > hour_range:
                        continue
                    
                    try:
                        commentList = []
                        commentObject = {}
                        reply = post_item["data"]["response"]["item_data"] or []
                        for comment in reply:
                            commentLink = comment["link"]
                            commentid = comment["commentid"]
                            commentKeyword = comment["keyword"]
                            commentText = re.sub(r'<.*?>', '', comment["comment"]).strip()
                            #remove html element, such as <br>,<href>...
                            commentPostid = comment["postid"]
                            commentTime = comment["releaseDate_timeStamp"]
                            commentUpdateTime = comment["updateTime_timeStamp"]
                            commentLikeCount  =comment["likeCount"]
                            commentDislikeCount = comment["dislikeCount"]
                            commentObject = {
                                "commentTimeStamp":commentTime,
                                "commentid":commentid,
                                "commentKeyword":commentKeyword,
                                "text":commentText,
                                "commentTime":timestampConvert(int(commentTime)),
                                "commentUrl":commentLink,
                                "commentLikeCount":commentLikeCount,
                                "updateTime":time.time(),
                                "reply":[]
                            }
                            commentList.append(commentObject)
                    except Exception as e:
                        print(f"format_text comment: {e}")
                    try:
                        if len(outputRecord) == 0: #do not contain any record
                            print("no record")
                            threadPost={
                                        "source":"babyKindom",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postReleaseDate,
                                        "postid":postid,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":timestampConvert(postReleaseDate),
                                        "postUrl":postlink,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postCommentCount,
                                        "updateTime":time.time(),
                                        "reply":commentList    
                                    }
                            outputRecord[postlink] = threadPost
                            if postlink not in inputAiText:
                                inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {timestampConvert(postReleaseDate)}\n帖文連結: {postlink}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postCommentCount}\n"
                            print("add the first record")
                        else: #have record
                            for outputRecordUrl in outputRecord.values(): #check each record
                                recordUrl.append(outputRecordUrl["postUrl"])
                                
                            if postlink in recordUrl: #check if the post url is already in record
                                if int(postCommentCount) <= int(outputRecord[postlink]["postReplyCount"]):
                                        readableTime = timestampConvert(outputRecord[postlink]["updateTime"])
                                        print(f"{postlink} last update at {readableTime}\nsame url, no update")
                                        #print(f"source from scanning: {postUrl}\nsource from record  : {outputRecord[postUrl]['postUrl']}")
                                        continue
                                else:
                                    outputRecord[postlink]["postLikeCount"] = postLikeCount
                                    outputRecord[postlink]["postReplyCount"] = postCommentCount
                                    outputRecord[postlink]["updateTime"] = time.time()
                                    ouputRecordReadableTime = timestampConvert(outputRecord[postlink]["updateTime"])
                                    print(f"{postlink} at {ouputRecordReadableTime}\n same url, different like/reply count")
                                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {timestampConvert(postReleaseDate)}\n帖文連結: {postlink}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postCommentCount}\n"
                            else:
                                threadPost={
                                        "source":"babyKondom",
                                        #"postViewCount":postViewCount,
                                        "postTimeStamp":postReleaseDate,
                                        "postid":postid,
                                        "postKeyword":postKeyword,
                                        "text":postTitle,
                                        "postTime":timestampConvert(postReleaseDate),
                                        "postUrl":postlink,
                                        "postLikeCount":postLikeCount,
                                        "postReplyCount":postCommentCount,
                                        "updateTime":time.time(),
                                        "reply":commentList    
                                    }
                                if postlink not in inputAiText:
                                    outputRecord[postlink] = threadPost
                                    readableTime = timestampConvert(outputRecord[postlink]["updateTime"])
                                    print(f"{postlink} at {readableTime}\n find a new record")
                                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {timestampConvert(postReleaseDate)}\n帖文連結: {postlink}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postCommentCount}\n"

                    except Exception as e:
                        print(f"format Text ouputrecord:{e}")
                    try:
                        reply = post_item["data"]["response"]["item_data"] or []
                        for comment in reply:
                            commentLink = comment["link"]
                            commentid = comment["commentid"]
                            commentKeyword = comment["keyword"]
                            commentText = re.sub(r'<.*?>', '', comment["comment"]).strip()
                            #remove html element, such as <br>,<href>...
                            commentPostid = comment["postid"]
                            commentTime = comment["releaseDate_timeStamp"]
                            commentUpdateTime = comment["updateTime_timeStamp"]
                            commentLikeCount  =comment["likeCount"]
                            commentDislikeCount = comment["dislikeCount"]
                            inputAiText += f"留言: {commentText}(發佈時間: {commentTime})\n留言讚好數: {commentLikeCount}\n"
                    except Exception as e:
                        print(e)
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}outputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(outputRecord, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
    except IOError as e:
        print(f"result_text_cleaning formatText write output Record: {e}")   
    return inputAiText

if __name__ == "__main__":
    formatText("bk_result","chessman")