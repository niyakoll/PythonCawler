import threads_main
import sendWhatsapp
import getCurrentTime
import json
import threading
import time
import schedule
import result_text_cleaning
import ai_agent
import os
from itertools import chain
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



def startScanning():
    keyword_list_main = combineList()
    print(keyword_list_main)
    threads_main.scan(keyword_list_main)

def Distribute(clientName,targetWhatsappGroup):
    result = ""
    recentPostList= ""
    result += result_text_cleaning.formatText(f"searchResult",clientName)
    recentPostList += result_text_cleaning.postList(f"searchResult",clientName)
    
    with open(f"C:/Users/Alex/ListeningTool/github/threads_template/result/{clientName}PostListOutput.txt","w",encoding="utf-8") as f:
        f.write(recentPostList)
    with open(f"C:/Users/Alex/ListeningTool/github/threads_template/result/{clientName}AIOutput.txt","w",encoding="utf-8") as f:
        f.write(result)
    if len(result) > 15:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            aiText = ai_agent.callAI(result)
            sendWhatsapp.sendMessage(f"{clientName} 你好!\n{aiText}",recentPostList,targetWhatsappGroup)
            #print("have thing")
        except Exception as e:
            print(e)
    else:
        now = result_text_cleaning.timestampConvert(time.time())
        print(f"{now} , Found no Post for {clientName}.")
        sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。","",targetWhatsappGroup)
        #print("nothing!")

"""
    with open(target_path+f"{clientName}ai.txt","w",encoding="utf-8") as f:
        f.write(result)
    with open(target_path+f"{clientName}postList.txt","w",encoding="utf-8") as f:
        f.write(recentPostList)



    #if result != "":
        #aiText = ai_agent.callAI(result)
    #else:
        #aiText = "暫時未有找到更多相關帖文..."
    #sendWhatsapp.sendMessage(aiText,target_whatsapp_group[0])
    

    #sendWhatsapp.sendMessage(aiText,recentPostList,targetGroup)

    #print(targetGroup)
"""

def packAllScanner():
    startScanning()
    #Distribute("TVB","GCkNXoXxIL31cpfhwN9NSO")
    Distribute("楊老闆","D5pbC6ipk3G3NMVMWOFA2f")
    Distribute("華納","BxWKGp5kMCf9m50ypl1VDa")
    Distribute("林盛斌","ERiHadsFxk91XroB2Vyvdz")

    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Whole Process Finished.")

def test_schedule():
    currentTime = getCurrentTime.getCurrentTime()
    print(f"{currentTime['hour']}:{currentTime['minute']}:{currentTime['second']} running!")
def combineList()->list:
    allKeyword = []
    try:
        merge = list(chain.from_iterable([list(client.values()) for client in keyword_list]))
        for cList in merge:
             allKeyword.extend(cList)
        #print(allKeyword)   
    except Exception as e:
        print(f"{e}\nCombine List Error!")
    finally:
        return allKeyword

if __name__ == "__main__":
    
    try:
        #print(combineList())
        packAllScanner()
        #schedule.every(interval).minutes.do(packAllScanner)
    except Exception as e:
        print(f"{e}")

    #while True:
    #Checks whether a scheduled task 
    #is pending to run or not
        #schedule.run_pending()
        #time.sleep(1)
        