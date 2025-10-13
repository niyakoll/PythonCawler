import json
from nested_lookup import nested_lookup
from datetime import datetime
import pytz
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

with open('C:/Users/Alex/ListeningTool/github/threads_template/manifest.json', 'r',encoding="utf-8") as file:
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

def formatText(resultFileName)->str:
    outputText = ""
    with open(target_path+resultFileName, 'r',encoding="utf-8") as file:
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
            outputText += f"帖文標題: {postTitle}\n發佈時間: {postTime}\n帖文連結: {postUrl}\n帖文讚好數: {postLikeCount}\n帖文留言數: {postReplyCount}\n"
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
                outputText += f"留言: {commentText}(發佈時間: {commentTime})\n留言讚好數: {commentLikeCount}\n留言回覆數: {commentReplyCount}\n"
                #print(f"Comment Text: {commentText}(Publish on {commentTime})\n")
                #print(f"Comment Like Count: {commentLikeCount}\n")
                #print(f"Comment Reply Count: {commentReplyCount}\n")
            i+=1
    return outputText

def test():
    output = formatText("stressTest2.json")
    output += formatText("stressTest1.json")
    # Writing a single string to a filetext = "Hello, this is a sample text!"

    with open('test.txt', 'w',encoding='utf-8') as file:
        file.write(output)
"""
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