import json
from typing import Dict
import jmespath
from nested_lookup import nested_lookup
import threading
import time
import schedule
import result_text_cleaning
from datetime import datetime
import getCurrentTime
import math
import os

def checkIsUrlExist(url:str)->list:
    RecentUrlDict = {}
    resultDict = {}
    #print(__file__)
    #print(os.path.join(os.path.dirname(__file__),"result","stressTest2.json"))
    for i in range(1,9):
        path = str(os.path.join(os.path.dirname(__file__),"result",f"stressTest{i}.json"))
        #print(path)
        with open(path, 'r',encoding="utf-8") as file:
            data = json.load(file)
            if data != []:
        
                for post in data:
                    postUrl = post["thread"]["url"]
                    postLike = post["thread"]["like_count"]
                    postReply = post["thread"]["direct_reply_count"]
                    RecentUrlDict[str(postUrl)] ={"like_count":postLike,
                                            "direct_reply_count":postReply}
            else:
                resultDict["haveUrl"] = False
                resultDict["like_count"] = 1000000000
                resultDict["direct_reply_count"] = 100000000

    #print(RecentUrlDict)          
    if url in RecentUrlDict:
        #print(f"{url} already exist!")
        resultDict["haveUrl"] = True
        resultDict["like_count"] = RecentUrlDict[url]["like_count"]
        resultDict["direct_reply_count"] = RecentUrlDict[url]["direct_reply_count"]
        
        #print(like_count)
        #print(direct_reply_count)
        return resultDict
    else:
        #print("This is new url!")
        resultDict = None
        return resultDict

if __name__ == "__main__":
    i = checkIsUrlExist("https://www.threads.net/@amberloo.0201/post/DPx4BsiDWQ7") 
    
    print(i["haveUrl"])
    
    