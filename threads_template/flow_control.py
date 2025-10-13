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

currentTime = getCurrentTime.getCurrentTime()


if __name__ == "__main__":
    #schedule.every(30).minutes.do(scan())
    #schedule.every(1).seconds.do(test_schedule)
    #t0 = threading.Thread(target = threads_main.scan())
    #t0.start()
    #t0.join()
    result = result_text_cleaning.formatText("stressTest1.json")
    result += result_text_cleaning.formatText("stressTest2.json")
    aiText = ai_agent.callAI(result)
    sendWhatsapp.sendMessage(aiText,target_whatsapp_group[0])
    print("\n\n\nFinish!")

    #while True:
    # Checks whether a scheduled task 
    # is pending to run or not
        #schedule.run_pending()
        #time.sleep(1)