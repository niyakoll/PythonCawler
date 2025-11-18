from threads_main import scan as startScanning
import sendWhatsapp
import result_text_cleaning
import ai_agent
import json
import threading
import time
import schedule
import os
import logging
import datetime
import psutil
import sys
import pidlock
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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


#After scraping data from thread, distribute data to the right client output record json, call another module - result_text_cleaning
def Distribute(clientName,targetWhatsappGroup,whapi_group_id):
    aiText = ""
    cleanResult = ""
    recentPostList= ""
    #cleaning data by calling another module - result_text_cleaning
    try:
        cleanResult += result_text_cleaning.formatText("searchResult",clientName)
    except Exception as e:
        print(f"flow_control Distribute: {e}")
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
            if client_panel[client]["threads_run"] == False:
                continue
            keyword_list_main.extend(client_panel[client]["keyword"])    
    return keyword_list_main


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
                if client_panel[client]["threads_run"] == False:
                    continue
                target_whatsapp_group = client_panel[client]["target_whatsapp_group"]
                whapi_group_id = client_panel[client]["whapi_group_id"]
                Distribute(client,target_whatsapp_group,whapi_group_id)
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"AllClientFinalOutput.json")), 'r',encoding="utf-8") as file:
                        AllClientFinalOutput = json.load(file)
                        
                except Exception as e:
                    print(f"flow_control read all client final output json: {e}")
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"finalOutput.json")), 'r',encoding="utf-8") as file:
                        clientFinalOutput = json.load(file)
                        AllClientFinalOutput[client] = clientFinalOutput
                except Exception as e:
                    print(f"flow_control read final ouput json: {e}")
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"AllClientFinalOutput.json")), 'w',encoding="utf-8") as file:
                        json.dump(AllClientFinalOutput, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                        print("Final Output saved.")
                except Exception as e:
                    print(f"flow_control write All client final result json: {e}")
    except Exception as e:
        print(f"flow_control OutputResult: {e}")
def log_memory(label: str = ""):
    try:
        process = psutil.Process(os.getpid())
        rss_mb = process.memory_info().rss / 1024 / 1024  # Resident Set Size
        vms_mb = process.memory_info().vms / 1024 / 1024  # Virtual Memory
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp} CET] {label} RAM: {rss_mb:.1f} MB (RSS) | {vms_mb:.1f} MB (VMS)")
    except Exception as e:
        print(e)
#pack all process into one function for better management
def packAllScanner():
    startTime = time.time()
    log_memory("Start")
    clearSearchResultJson()
    startScanning()
    OutputResult()
    reportMessage()
    endTime = time.time()
    wholeProcessTime = (endTime - startTime)/60
    print(f"Whole Process Time: {wholeProcessTime} minutes.")
    now = result_text_cleaning.timestampConvert(time.time())
    
    global counter
    if counter >= 96:
        counter = 0
    counter += 1
    print(f"Program run count:{counter}")
    log_memory("After Whole Process.")
    print(f"{now} : Whole Process Finished.")
    
def clearSearchResultJson():
    #better performance 
    initalsearchResultJson = []
    try:
        for i in range(1,6):
            with open(str(os.path.join(os.path.dirname(__file__),"result",f"searchResult{i}.json")), 'w',encoding="utf-8") as file:
                json.dump(initalsearchResultJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                print(f"Client threads search result json {i} cleared.")
    except Exception as e:
        print(f"flow_control clearSearchResultJson search result json: {e}")
def setupJsonFile():
    initalsearchResultJson = []
    initalclientRecordJson = {}
    initalclientQuietModeCount = {}
    txt = ""
    path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
    try:
        for i in range(1,6):
            with open(str(os.path.join(os.path.dirname(__file__),"result",f"searchResult{i}.json")), 'w',encoding="utf-8") as file:
                json.dump(initalsearchResultJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                print(f"Client threads search result json {i} initalised.")
    except Exception as e:
        print(f"flow_control setupJsonFile search Result: {e}")
    with open(path, 'r',encoding="utf-8") as file:
            manifest = json.load(file)
            clientList = manifest["client"]
            client_panel = manifest["client_panel"]
            for client in clientList:
                if client_panel[client]["threads_run"] == False:
                    continue
                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}outputRecord.json")), 'w',encoding="utf-8") as file:
                        json.dump(initalclientRecordJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                        print("Client threads record json initalised.")
                except Exception as e:
                    print(f"flow_control setupJsonFile {client} output Record: {e}")

                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}AIOutput.txt")), 'w',encoding="utf-8") as file:
                        file.write(txt)
                        print("Client AI text debug file initalised.")
                except Exception as e:
                    print(f"flow_control setupJsonFile {client} AI output: {e}")

                try:
                    with open(str(os.path.join(os.path.dirname(__file__),"result",f"{client}PostListOutput.txt")), 'w',encoding="utf-8") as file:
                        file.write(txt)
                        print("Client post list debug txt file initalised.")
                except Exception as e:
                    print(f"flow_control setupJsonFile {client} postlist output: {e}")
    try:
        with open(str(os.path.join(os.path.dirname(__file__),"result","client_quiet_mode_count.json")),'w',encoding="utf-8") as file:
            json.dump(initalclientQuietModeCount, file, indent=4,ensure_ascii=False)
    except Exception as e:
        print(e)
def sendAIandSendMessage(aiinput:str,recentPostList:str,clientName:str,whapi_group_id:str):
    
    if len(recentPostList) > 15:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            aiText ="AI功能將在未來版本推出" #ai_agent.callAI(aiinput)
            sendWhatsapp.whapi_sendToClient(ai_message=aiText,postListMessage=recentPostList,whapi_group_id=whapi_group_id)
            
            #response  = sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{aiText}\n{recentPostList}",whapi_group_id)
            #if response["error"]["code"] != 200:
                #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{aiText}",recentPostList,targetWhatsappGroup)
        except Exception as e:
            print(f"flow_control sendAIandSendMessage found post condition: {e}")
    else:
        try:
            now = result_text_cleaning.timestampConvert(time.time())
            print(f"{now} , Found no Post for {clientName}.")
            
            sendWhatsapp.whapi_sendMessage(f"{clientName} 你好!\n{now} \nThreads暫時未找到新的帖文。",whapi_group_id)
            #if response["error"]["code"] != 200:
                #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} \nThreads暫時未找到新的帖文。","",targetWhatsappGroup)
        except Exception as e:
            #sendWhatsapp.sendMessage(f"{clientName} 你好!\n{now} 暫時未找到新的帖文。","",targetWhatsappGroup)
            print(f"flow_control sendAIandSendMessage Found no post condition: {e}")
def reportMessage():
    aiText = ""
    recentPostList = ""
    client_message_interval = 30
    global counter
    global quiet_mode_counter_dict
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
                if client_panel[client]["threads_run"] == False:
                    continue
                target_whatsapp_group = client_panel[client]["target_whatsapp_group"]
                whapi_group_id = client_panel[client]["whapi_group_id"]
                client_message_interval = client_panel[client]["message_interval"]
                client_quiet_mode = client_panel[client]["quiet_mode"]
                # === quiet mode off === 
                if client_quiet_mode == False:
                    skip = quietMode_off(client,client_message_interval,whapi_group_id)
                    if skip:
                        continue
                else:
                    # ==== quiet mode On === skip two times if no post was found
                    skip = quietMode(client,client_message_interval,whapi_group_id)
                    if skip:
                        continue
    except Exception as e:
        print(f"flow_control reportMessage: {e}")
def quietMode_off(client,client_message_interval,whapi_group_id):
    isSkip = True
    aiText = ""
    recentPostList = ""
    global counter
    global quiet_mode_counter_dict
    interval_60_countList = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95]
    interval_120_countList = [0,7,15,23,31,39,47,55,63,71,79,87,95]
    interval_240_countList = [0,15,31,47,63,79,95]
    interval_360_countList = [0,23,47,71,95]
    interval_720_countList = [0,47]
    interval_1440_countList = [0]
    try:
        match client_message_interval :
            case 15:
                aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                isSkip = False
            case 30:
                if counter %2 ==1:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 30 minutes interval message for {client} at count {counter}.")
            case 60:
                if counter in interval_60_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 60 minutes interval message for {client} at count {counter}.")
            case 120:
                if counter in interval_120_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 120 minutes interval message for {client} at count {counter}.")
            case 240:
                if counter in interval_240_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 240 minutes interval message for {client} at count {counter}.")
            case 360:
                if counter in interval_360_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 360 minutes interval message for {client} at count {counter}.")
            case 720:
                if counter in interval_720_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 720 minutes interval message for {client} at count {counter}.")
            case 1440:
                if counter in interval_1440_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
                else:
                    print(f"Skip 1440 minutes interval message for {client} at count {counter}.")
            case _:
                print(f"Unknown message interval setting for {client}.")
    except Exception as e:
        print(e)
    finally:
        return isSkip

def quietMode(client,client_message_interval,whapi_group_id):
    global quiet_mode_counter_dict
    isSkip = True
    aiText = ""
    recentPostList = ""
    global counter
    interval_60_countList = [0,3,7,11,15,19,23,27,31,35,39,43,47,51,55,59,63,67,71,75,79,83,87,91,95]
    interval_120_countList = [0,7,15,23,31,39,47,55,63,71,79,87,95]
    interval_240_countList = [0,15,31,47,63,79,95]
    interval_360_countList = [0,23,47,71,95]
    interval_720_countList = [0,47]
    interval_1440_countList = [0]
    if client not in quiet_mode_counter_dict:
        quiet_mode_counter_dict[client] = 0
    if client in quiet_mode_counter_dict:
        quiet_count = quiet_mode_counter_dict[client]
    print(f"{client} quiet count: {quiet_count}")
    
    try:
        match client_message_interval :
            case 15:
                aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                if len(recentPostList) < 15:
                    if quiet_count < 2:
                        quiet_mode_counter_dict[client] += 1
                        print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        quiet_mode_counter_dict[client] = 0
                        isSkip = False 
                else:
                    sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                    isSkip = False
            case 30:
                if counter %2 ==1:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 30 minutes interval message for {client} at count {counter}.")
            case 60:
                if counter in interval_60_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 60 minutes interval message for {client} at count {counter}.")
            case 120:
                if counter in interval_120_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 120 minutes interval message for {client} at count {counter}.")
            case 240:
                if counter in interval_240_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 240 minutes interval message for {client} at count {counter}.")
            case 360:
                if counter in interval_360_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 360 minutes interval message for {client} at count {counter}.")
            case 720:
                if counter in interval_720_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 720 minutes interval message for {client} at count {counter}.")
            case 1440:
                if counter in interval_1440_countList:
                    aiText, recentPostList = result_text_cleaning.prepareOutputText(client,client_message_interval)
                    if len(recentPostList) < 15:
                        if quiet_count < 2:
                            quiet_mode_counter_dict[client] += 1
                            print(f"Found no post and skip {client} at quiet count: {quiet_count}")
                        else:
                            sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                            quiet_mode_counter_dict[client] = 0
                            isSkip = False 
                    else:
                        sendAIandSendMessage(aiText,recentPostList,client,whapi_group_id)
                        isSkip = False
                else:
                    print(f"Skip 1440 minutes interval message for {client} at count {counter}.")
            case _:
                print(f"Unknown message interval setting for {client}.")
    except Exception as e:
        print(e)
    finally:
        return isSkip
    



def print_banner():
    print("\n" + "="*70)
    print("    NEW CYCLE STARTED")
    print(f"    Time: {datetime.datetime.now().strftime('%H:%M:%S %Y-%m-%d')}")
    log_memory("New Cycle")
    print("="*70 + "\n")
def run_in_thread(func):
    threading.Thread(target=func, daemon=True).start()
def sleep_until_restart_time(hour: int, minute: int):
    """Sleep until a specific time (e.g. 12:30 or 12:35)."""
    now = datetime.datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:                     # already past → tomorrow
        target += datetime.timedelta(days=1)
    seconds = (target - now).total_seconds()
    print(f"[{now.strftime('%H:%M:%S')}] Sleeping {seconds/60:.1f}min until {target.strftime('%H:%M')}…")
    time.sleep(seconds)
def sleep_until_next_minute(interval:int):
    now = datetime.datetime.now()
    next_minute = (now + datetime.timedelta(minutes=interval)).replace(second=0, microsecond=0)
    seconds = (next_minute - now).total_seconds()
    print(f"[{now.strftime('%H:%M:%S')}] Sleeping {seconds:.1f}s until next minute...")
    time.sleep(seconds)
def hard_restart():
    log_memory("Before Restart")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Hard-restart → RAM reset")
    
    # This will replace the current process → only one instance ever
    os.execve(sys.executable, [sys.executable] + sys.argv, os.environ)
    # execve NEVER returns (if it does → error)

def main(interval,restart_hour,restart_minute):
    
            #initialize json file to save threads record if not exist
    setupJsonFile()
    print_banner()
    # ----- MAIN LOOP (runs forever until daily restart) -----
    while True:
        packAllScanner()                     # ← your 2‑minute job
        now = datetime.datetime.now()

        # Check if we are approaching the daily restart time
        #restart_hour, restart_minute = 13, 15          # ← CHANGE THIS
        next_restart = now.replace(hour=restart_hour, minute=restart_minute,
                                   second=0, microsecond=0)
        if next_restart <= now:
            next_restart += datetime.timedelta(days=1)

        next_min = (now + datetime.timedelta(minutes=interval)).replace(second=0, microsecond=0)
        next_min = next_min.replace(minute=(next_min.minute // interval) * interval)

        if next_min >= next_restart:
            # Time to do the daily restart
            sleep_until_restart_time(restart_hour, restart_minute)
            hard_restart()
            return  # process restarts → new daily cycle

        # Normal 2‑minute wait
        sleep_until_next_minute(interval)

if __name__ == "__main__":
    if not pidlock.acquire_lock():
        print("Another instance is already running → exiting")
        sys.exit(1)
    try:
        quiet_mode_counter_dict = {"client_demo":0}
        counter = 0
        main(interval,10,30)
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        logger.exception(e)
    finally:
        pidlock.release_lock()
        