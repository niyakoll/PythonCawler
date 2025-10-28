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
client = []
interval = 15
ai_agent_api_key = ""
ai_model = []
proxies = []
path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    client = manifest["client"]
    interval = manifest["interval"]
    ai_agent_api_key = manifest["ai_agent_api_key"]
    ai_model = manifest["ai_model"]
    proxies = manifest["proxies"]
#scrap data from thread, call another module - threads_main
def startScanning():
    keyword_list_main = combineList()
    print(keyword_list_main)
    threads_main.scan(keyword_list_main)

#After scraping data from thread, distribute data to the right client
def Distribute(clientName,targetWhatsappGroup,whapi_group_id):
    aiText = ""
    result = ""
    recentPostList= ""
    #cleaning data by calling another module - result_text_cleaning
    result += result_text_cleaning.formatText(f"searchResult",clientName)
    recentPostList += result_text_cleaning.postList(f"searchResult",clientName)
    #write clean result to a text file for debug session
    PostListpath = str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}PostListOutput.txt"))
    AiOutputpath = str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}AIOutput.txt"))
    with open(PostListpath,"w",encoding="utf-8") as f:
        f.write(recentPostList)
    with open(AiOutputpath,"w",encoding="utf-8") as f:
        f.write(result)
    #check if the clean result contain content, if yes , pass to ai and send whatsapp message, if not, send remind message.    
    if len(result) > 15:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            aiText = ai_agent.callAI(result)
            sendWhatsapp.whapi_sendToClient(ai_message=aiText,postListMessage=recentPostList,whapi_group_id=whapi_group_id)
            
            #response  = sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{aiText}\n{recentPostList}",whapi_group_id)
            #if response["error"]["code"] != 200:
                #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{aiText}",recentPostList,targetWhatsappGroup)
        except Exception as e:
            #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{aiText}",recentPostList,targetWhatsappGroup)
            print(e)
    else:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            print(f"{now} , Found no Post for {clientName}.")
            
            response = sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。",whapi_group_id)
            if response["error"]["code"] != 200:
                sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。","",targetWhatsappGroup)
        except Exception as e:
            #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。","",targetWhatsappGroup)
            print(e)

#pack all process into one function for better management
def packAllScanner():
    startScanning()
    OutputResult()
    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Whole Process Finished.")

#get keyword list from manifest json and combine all keywork list from different client into one list for scraping
def combineList():
    clientList = []
    keyword_list_main = []
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    with open(path, 'r',encoding="utf-8") as file:
        manifest = json.load(file)
        clientList = manifest["client"]
        client_panel = manifest["client_panel"]
        for client in clientList:
            if client_panel[client]["run"] == False:
                continue
            keyword_list_main.extend(client_panel[client]["keyword"])    
    return keyword_list_main

def clearRecord():
    data = {}
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result",f"親愛的BOBoutputRecord.json")), 'w',encoding="utf-8") as file:
            json.dump(data, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
    except IOError as e:
        print(e)

#run all client that are active(true)
def OutputResult():
    clientList = []
    
    try:
        path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
        with open(path, 'r',encoding="utf-8") as file:
            manifest = json.load(file)
            clientList = manifest["client"]
            client_panel = manifest["client_panel"]
            for client in clientList:
                if client_panel[client]["run"] == False:
                    continue
                target_whatsapp_group = client_panel[client]["target_whatsapp_group"]
                whapi_group_id = client_panel[client]["whapi_group_id"]
                Distribute(client,target_whatsapp_group,whapi_group_id)
    except Exception as e:
        print(e)
if __name__ == "__main__":
    try:
        
        #directly run the whole program when click run 
        packAllScanner()
        #schedule the whole program run every {interval}(refer to manifest json setting) minutes.
        schedule.every(interval).minutes.do(packAllScanner)
        #schedule.every(90).minutes.do(clearRecord())
    except Exception as e:
        print(f"{e}")
    while True:
    #Checks whether a scheduled task is pending to run or not, keep running whole program.
        schedule.run_pending()
        time.sleep(1)
        