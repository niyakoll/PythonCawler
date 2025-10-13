import threads_main
import sendWhatsapp
import getCurrentTime
import json
import threading
import time
import schedule
import result_text_cleaning
import ai_agent
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



def startRunning():
    threads_main.scan()
    result = result_text_cleaning.formatText("stressTest1.json")
    result += result_text_cleaning.formatText("stressTest2.json")
    aiText = ai_agent.callAI(result)
    sendWhatsapp.sendMessage(aiText,target_whatsapp_group[0])
    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Whole Process Finished.")

def test_schedule():
    currentTime = getCurrentTime.getCurrentTime()
    print(f"{currentTime['hour']}:{currentTime['minute']}:{currentTime['second']} running!")

if __name__ == "__main__":
    
    
    try:
        startRunning()
        schedule.every(interval).minutes.do(startRunning)

            
    except:
        print("crash!")

    while True:
    #Checks whether a scheduled task 
    #is pending to run or not
        schedule.run_pending()
        time.sleep(1)
        