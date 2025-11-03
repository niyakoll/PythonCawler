import threads_main
import sendWhatsapp
import result_text_cleaning
import ai_agent
import json
import threading
import time
import schedule
import os

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

#After scraping data from thread, distribute data to the right client output record json, call another module - result_text_cleaning
def Distribute(clientName,targetWhatsappGroup,whapi_group_id):
    aiText = ""
    cleanResult = ""
    recentPostList= ""
    #cleaning data by calling another module - result_text_cleaning
    try:
        cleanResult += result_text_cleaning.formatText("searchResult",clientName)
    except Exception as e:
        print(e)
    #aiText, recentPostList = result_text_cleaning.prepareOutputText(clientName)
    
    #write clean result to a text file for debug session
    PostListpath = str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}PostListOutput.txt"))
    AiOutputpath = str(os.path.join(os.path.dirname(__file__),"result",f"{clientName}AIOutput.txt"))
    with open(PostListpath,"w",encoding="utf-8") as f:
        f.write(recentPostList)
    with open(AiOutputpath,"w",encoding="utf-8") as f:
        f.write(aiText)
    

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
    AllClientFinalOutput = {}
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    try:
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
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"finalOutput.json")), 'r',encoding="utf-8") as file:
                        clientFinalOutput = json.load(file)
                        AllClientFinalOutput[client] = clientFinalOutput
                except Exception as e:
                    print(e)
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"AllClientFinalOutput.json")), 'w',encoding="utf-8") as file:
                        json.dump(AllClientFinalOutput, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                        print("Final Output saved.")
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)

#pack all process into one function for better management
def packAllScanner():
    startTime = time.time()
    startScanning()
    OutputResult()
    reportMessage()
    endTime = time.time()
    wholeProcessTime = (endTime - startTime)/60
    print(f"Whole Process Time: {wholeProcessTime} minutes.")
    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Whole Process Finished.")
    global counter
    if counter >= 96:
        counter = 0
    counter += 1
    print(f"Program run count:{counter}")
    

def setupJsonFile():
    initalsearchResultJson = []
    initalclientRecordJson = {}
    txt = ""
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    try:
        for i in range(1,11):
            with open(str(os.path.join(os.path.dirname(__file__),"result",f"searchResult{i}.json")), 'w',encoding="utf-8") as file:
                json.dump(initalsearchResultJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                print(f"Client threads search result json {i} initalised.")
    except Exception as e:
        print(e)
    with open(path, 'r',encoding="utf-8") as file:
            manifest = json.load(file)
            clientList = manifest["client"]
            client_panel = manifest["client_panel"]
            for client in clientList:
                if client_panel[client]["run"] == False:
                    continue
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}outputRecord.json")), 'w',encoding="utf-8") as file:
                        json.dump(initalclientRecordJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                        print("Client threads record json initalised.")
                except Exception as e:
                    print(e)

                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}AIOutput.txt")), 'w',encoding="utf-8") as file:
                        file.write(txt)
                        print("Client AI text debug file initalised.")
                except Exception as e:
                    print(e)

                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}PostListOutput.txt")), 'w',encoding="utf-8") as file:
                        file.write(txt)
                        print("Client post list debug txt file initalised.")
                except Exception as e:
                    print(e)
def sendAIandSendMessage(aiinput:str,recentPostList:str,clientName:str,whapi_group_id:str):
    
    if len(recentPostList) > 15:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            aiText =ai_agent.callAI(aiinput)
            sendWhatsapp.whapi_sendToClient(ai_message=aiText,postListMessage=recentPostList,whapi_group_id=whapi_group_id)
            
            #response  = sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{aiText}\n{recentPostList}",whapi_group_id)
            #if response["error"]["code"] != 200:
                #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{aiText}",recentPostList,targetWhatsappGroup)
        except Exception as e:
            print(e)
    else:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            print(f"{now} , Found no Post for {clientName}.")
            
            sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{now} \nThreads暫時未找到新的帖文。",whapi_group_id)
            #if response["error"]["code"] != 200:
                #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} \nThreads暫時未找到新的帖文。","",targetWhatsappGroup)
        except Exception as e:
            #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。","",targetWhatsappGroup)
            print(e)
def reportMessage():
    aiText = ""
    recentPostList = ""
    client_message_interval = 30
    global counter
    interval_60_countList = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95]
    interval_120_countList = [0,7,15,23,31,39,47,55,63,71,79,87,95]
    interval_240_countList = [0,15,31,47,63,79,95]
    interval_360_countList = [0,23,47,71,95]
    interval_720_countList = [0,47]
    interval_1440_countList = [0]
    
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    try:
        with open(path, 'r',encoding="utf-8") as file:
            manifest = json.load(file)
            clientList = manifest["client"]
            client_panel = manifest["client_panel"]
            for client in clientList:
                if client_panel[client]["run"] == False:
                    continue
                target_whatsapp_group = client_panel[client]["target_whatsapp_group"]
                whapi_group_id = client_panel[client]["whapi_group_id"]
                client_message_interval = client_panel[client]["message_interval"]
                match client_message_interval :
                    case 15:
                        aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    case 30:
                        if counter %2 ==1:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 30 minutes interval message for {client} at count {counter}.")
                            continue
                    case 60:
                        if counter in interval_60_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 60 minutes interval message for {client} at count {counter}.")
                            continue
                    case 120:
                        if counter in interval_120_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 120 minutes interval message for {client} at count {counter}.")
                            continue
                    case 240:
                        if counter in interval_240_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 240 minutes interval message for {client} at count {counter}.")
                            continue
                    case 360:
                        if counter in interval_360_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 360 minutes interval message for {client} at count {counter}.")
                            continue
                    case 720:
                        if counter in interval_720_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 720 minutes interval message for {client} at count {counter}.")
                            continue
                    case 1440:
                        if counter in interval_1440_countList:
                            aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        else:
                            print(f"Skip 1440 minutes interval message for {client} at count {counter}.")
                            continue
                    case _:
                        print(f"Unknown message interval setting for {client}.")
    except Exception as e:
        print(e)
                
if __name__ == "__main__":
    try:
        counter = 0
            #initialize json file to save threads record if not exist
        setupJsonFile()
            #directly run the whole program when click run 
        packAllScanner()
            #schedule the whole program run every {interval}(refer to manifest json setting) minutes.
        schedule.every(interval).minutes.do(packAllScanner)
        
        #schedule.every().minute.at(":00").do(packAllScanner)
        #schedule.every().minute.at(":15").do(packAllScanner)
        #schedule.every().minute.at(":30").do(packAllScanner)
        #schedule.every().minute.at(":45").do(packAllScanner)
        
    except Exception as e:
        print(f"{e}")
    while True:
            #Checks whether a scheduled task is pending to run or not, keep running whole program.
        schedule.run_pending()
        time.sleep(1)
        