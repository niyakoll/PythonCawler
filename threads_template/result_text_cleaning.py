import json
from nested_lookup import nested_lookup
from datetime import datetime
import pytz
import time
import os
import threads_main
#Get setting from manifest json file
client = ""
keyword_list = []
interval = 30
target_path = ""
light_scan_mode = False
target_whatsapp_group = ""
ai_agent_api_key = ""
ai_model = []
proxies = []

path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    client = manifest["client"]
    keyword_list = manifest["keyword_list"]
    interval = manifest["interval"]
    target_path = manifest["target_path"]
    light_scan_mode = manifest["light_scan_mode"]
    target_whatsapp_group = manifest["target_whatsapp_group"]
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
    for i in keyword_list:
        try:
            targetList = i.get(clientName)
            if targetList != None:
                kList.extend(targetList)
                break
        except:
            print("can not found!")
    return kList
def formatText(resultFileName,clientName)->str:
    now = timestampConvert(time.time())
    print(f"{now} : Start Cleaning Data.")
    clientKeywordList = findClientKeywordList(clientName)
    inputAiText = ""
    #updatePostList = ""
    for r in range(1,11):
        with open(f"{target_path}{resultFileName}{r}.json", 'r',encoding="utf-8") as file:
            result = json.load(file)
            if result != []:
                #print(len(posts))
                i = 0
                for post in result[:]:
                    postTimeStamp = post["thread"]["published_on"]
                    hrDifferent = threads_main.hourDifferent(postTimeStamp)
                    if hrDifferent > 2:
                        continue
                    postKeyword = post["thread"]["keyword"]
                    if postKeyword not in clientKeywordList:
                        continue
                    postTitle = post["thread"]["text"]
                    if postTitle in inputAiText:
                        continue
                    postTime = timestampConvert(postTimeStamp)
                    postUrl = post["thread"]["url"]
                    postLikeCount = post["thread"]["like_count"]
                    postReplyCount = post["thread"]["direct_reply_count"]
                    inputAiText += f"關鍵字:{postKeyword}\n帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                    #updatePostList += f"帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
                    #print(f"Post Title: {postTitle}\n")
                    #print(f"Publish on: {postTime}\n")
                    #print(f"Post Link: {postUrl}\n")
                    #print(f"Post Like Count: {postLikeCount}\n")
                    #print(f"Post Reply Count: {postReplyCount}\n")
                    replies = nested_lookup("replies",result)
                    commentList = replies[i]
                    for comment in commentList:
                        commentText = comment["text"]
                        commentTimeStamp = comment["published_on"]
                        commentTime = timestampConvert(commentTimeStamp)

                        commentLikeCount = comment["like_count"]
                        commentReplyCount = comment["direct_reply_count"]
                        inputAiText += f"留言: {commentText}(發佈時間: {commentTime})\n留言讚好數: {commentLikeCount}\n留言回覆數: {commentReplyCount}\n"
                        #print(f"Comment Text: {commentText}(Publish on {commentTime})\n")
                        #print(f"Comment Like Count: {commentLikeCount}\n")
                        #print(f"Comment Reply Count: {commentReplyCount}\n")
                    i+=1
            
                
    return inputAiText


    
def postList(resultFileName,clientName):
    now = timestampConvert(time.time())
    #print(f"{now} : Start Creating Post List.")
    clientKeywordList = findClientKeywordList(clientName)
    updatePostList = ""
    for r in range(1,11):
        with open(f"{target_path}{resultFileName}{r}.json", 'r',encoding="utf-8") as file:
            result = json.load(file)
            if result != []:
                #print(len(posts))
                i = 1
                for post in result[:]:
                    postTimeStamp = post["thread"]["published_on"]
                    postKeyword = post["thread"]["keyword"]
                    hrDifferent = threads_main.hourDifferent(postTimeStamp)
                    if hrDifferent > 2:
                        continue
                    postKeyword = post["thread"]["keyword"]
                    if postKeyword not in clientKeywordList:
                        #print(postKeyword)
                        continue
                    postTitle = post["thread"]["text"]
                    if postTitle in result:
                        print(postTitle)
                        continue
                    if "\n" in postTitle: 
                        postTitle = postTitle.split("\n")[0]
                    
                    postTime = timestampConvert(postTimeStamp)
                    postUrl = post["thread"]["url"]
                    postLikeCount = post["thread"]["like_count"]
                    postReplyCount = post["thread"]["direct_reply_count"]
                    updatePostList += f"關鍵字: {postKeyword}\n標題: {postTitle} \n發佈時間: {postTime}\n連結: {postUrl}\n讚好: {postLikeCount} 留言: {postReplyCount}\n________"
                    i+=1
            
                
    return updatePostList

def test():
    output = formatText("stressTest2.json")
    output += formatText("stressTest1.json")
    # Writing a single string to a filetext = "Hello, this is a sample text!"

    with open('test.txt', 'w',encoding='utf-8') as file:
        file.write(output)



"""
with open(target_path+"stressTest1.json", 'r',encoding="utf-8") as file:
        test = json.load(file)
        
        if test == None:
            print("none")
        elif test == []:
            print("[]")
        else:
            print("not work!")


with open(target_path+"stressTest1.json", 'r',encoding="utf-8") as file:
    result = json.load(file)
   
    #print(len(posts))
    i = 0
    for post in result[:]:
        postTitle = post["thread"]["text"]
        postTimeStamp = post["thread"]["published_on"]
        postTime = timestampConvert(postTimeStamp)
        postUrl = post["thread"]["url"]
        postLikeCount = post["thread"]["like_count"]
        postReplyCount = post["thread"]["direct_reply_count"]
        print(f"Post Title: {postTitle}\n")
        print(f"Publish on: {postTime}\n")
        print(f"Post Link: {postUrl}\n")
        print(f"Post Like Count: {postLikeCount}\n")
        print(f"Post Reply Count: {postReplyCount}\n")
        replies = nested_lookup("replies",result)
        commentList = replies[i]
        for comment in commentList:
            commentText = comment["text"]
            commentTimeStamp = comment["published_on"]
            commentTime = timestampConvert(commentTimeStamp)
            commentLikeCount = comment["like_count"]
            commentReplyCount = comment["direct_reply_count"]
            print(f"Comment Text: {commentText}(Publish on {commentTime})\n")
            print(f"Comment Like Count: {commentLikeCount}\n")
            print(f"Comment Reply Count: {commentReplyCount}\n")
        i+=1
        
    #for i in result[:]:
        #post = result[i.index()]['thread']['text']
        #post = result[0]['thread']['text']
        #print(i)
"""
