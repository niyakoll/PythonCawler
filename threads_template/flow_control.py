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



def startRunning(index,clientName,targetGroup):
    
    keyword_list_main = keyword_list[index][clientName]
    threads_main.scan(clientName,keyword_list_main)
    result = result_text_cleaning.formatText(f"{clientName}1.json")
    result += result_text_cleaning.formatText(f"{clientName}2.json")
    result += result_text_cleaning.formatText(f"{clientName}3.json")
    result += result_text_cleaning.formatText(f"{clientName}4.json")
    result += result_text_cleaning.formatText(f"{clientName}5.json")
    result += result_text_cleaning.formatText(f"{clientName}6.json")
    result += result_text_cleaning.formatText(f"{clientName}7.json")
    result += result_text_cleaning.formatText(f"{clientName}8.json")
    recentPostList = "\n\n以下的全部帖文的列表:\n"
    recentPostList += result_text_cleaning.postList(f"{clientName}1.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}2.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}3.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}4.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}5.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}6.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}7.json")
    recentPostList += result_text_cleaning.postList(f"{clientName}8.json")
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
    

def packAllScanner():
    TVBaiText = ""
    TVBpostText = ""
    楊老闆aiText = ""
    楊老闆postText = ""
    華納aiText = ""
    華納postText = ""

    s1 = threading.Thread(target= startRunning ,args=(1,"TVB","GCkNXoXxIL31cpfhwN9NSO"))
    s2 = threading.Thread(target= startRunning ,args=(0,"楊老闆","D5pbC6ipk3G3NMVMWOFA2f"))
    s3 = threading.Thread(target= startRunning ,args=(2,"華納","BxWKGp5kMCf9m50ypl1VDa"))
    #s4 = threading.Thread(target= startRunning ,args=(5,"古天樂","GCkNXoXxIL31cpfhwN9NSO"))
    s1.start()
    s2.start()
    s3.start()
    #s4.start()
    s1.join()
    s2.join()
    s3.join()
    #s4.join()
    with open(target_path+"TVBai.txt",encoding="utf-8") as f:
        text = f.read()
        TVBaiText = ai_agent.callAI(text)
    with open(target_path+"TVBpostList.txt",encoding="utf-8") as f:
        TVBpostText = f.read()
        sendWhatsapp.sendMessage(TVBaiText,TVBpostText,"GCkNXoXxIL31cpfhwN9NSO")

    with open(target_path+"楊老闆ai.txt",encoding="utf-8") as f:
        text = f.read()
        楊老闆aiText = ai_agent.callAI(text)
    with open(target_path+"楊老闆postList.txt",encoding="utf-8") as f:
        楊老闆postText = f.read()
        sendWhatsapp.sendMessage(楊老闆aiText,楊老闆postText,"D5pbC6ipk3G3NMVMWOFA2f")

    with open(target_path+"華納ai.txt",encoding="utf-8") as f:
        text = f.read()
        華納aiText = ai_agent.callAI(text)
    with open(target_path+"華納postList.txt",encoding="utf-8") as f:
        華納postText = f.read()
        sendWhatsapp.sendMessage(華納aiText,華納postText,"BxWKGp5kMCf9m50ypl1VDa")

    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Whole Process Finished.")

def test_schedule():
    currentTime = getCurrentTime.getCurrentTime()
    print(f"{currentTime['hour']}:{currentTime['minute']}:{currentTime['second']} running!")

if __name__ == "__main__":

    try:
        packAllScanner()
        schedule.every(interval).minutes.do(packAllScanner)   
    except:
        print("crash!")

    while True:
    #Checks whether a scheduled task 
    #is pending to run or not
        schedule.run_pending()
        time.sleep(1)
        