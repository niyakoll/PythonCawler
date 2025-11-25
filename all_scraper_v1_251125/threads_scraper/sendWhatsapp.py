from datetime import datetime
import requests
import json
import os
import pytz
import sys
# 自動找到 shared 目錄（相對於目前檔案往上兩層）
SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
SHARED_DIR = os.path.abspath(SHARED_DIR)

# 把 shared 加入 import 路徑（給 pidlock 用）
if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

# 讀共用的 manifest.json
MANIFEST_PATH = os.path.join(SHARED_DIR, "manifest.json")
with open(MANIFEST_PATH, 'r', encoding="utf-8") as f:
    manifest = json.load(f)
whapi_token = ""
whapi_api_url = ""

whapi_token = manifest["whapi_token"]
whapi_api_url = manifest["whapi_api_url"]

def getCurrentTime()->dict:
    currentTime = {}
    # Get current time in Hong Kong (HKT)
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    hk_time = datetime.now(hk_tz)

    # Format date and time
    formatted_time = hk_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    #print(formatted_time)  # Output: 2025-10-09 08:53:00 HKT

    # Extract components
    year = hk_time.year
    month = hk_time.month
    day = hk_time.day
    hour = hk_time.hour
    minute = hk_time.minute
    second = hk_time.second
    currentTime['year']=year
    currentTime['month']=month
    currentTime['day']=day
    currentTime['hour']=hour
    currentTime['minute']=minute
    currentTime['second']=second
    #print(f"Date: {year}-{month:02d}-{day:02d}, Time: {hour:02d}:{minute:02d}:{second:02d}")
    return currentTime
"""
def directPasteAndSend(input:str):
    pyperclip.copy(input)
    time.sleep(1)
    pyautogui.hotkey("Ctrl","V")
    pyautogui.hotkey("enter")
    

def paste(AIinput:str,postListMessage:str):
    time.sleep(30)
    #print("t2 open!")
    #print("t2 started!")
    pyperclip.copy(AIinput)
    pyautogui.hotkey("Ctrl","V")
    pyautogui.hotkey("enter")
    if postListMessage != "":
        postListMessageList = postListMessage.split("________")
        i = 1
        for text in postListMessageList[:-1]:
            heading = f"\n******帖文{i}******\n"
            heading += text
            directPasteAndSend(heading)
            i += 1
    else:
        print("NO Output Text!")
def sendAtPerfectMinutes():
    while True:
        current_time = datetime.now()

        if current_time.second == 0:
            print(current_time.second)
            break

    

def openWhatsapp(hour,minute,targetGroup):
    currentTime = getCurrentTime()
    second = currentTime['second']
    openTime = 60 - second
    
    waitTime = openTime -  1
    if waitTime <= 0:
        waitTime = 7
    closeTime = 80 - waitTime
    if closeTime <= 0:
        closeTime = 1
    print(f"now second is {second}, opentime is {openTime}, waiting time is {waitTime}, close time is {closeTime}")
    pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+1, wait_time=waitTime, tab_close=True, close_time=closeTime)
    

def sendMessage(outputText,postListMessage,targetGroup):
    currentTime = getCurrentTime()

    year = currentTime['year']
    month = currentTime['month']
    day = currentTime['day']
    hour = currentTime['hour']
    minute = currentTime['minute']
    second = currentTime['second']
    #print("I'm working...")
    #print(f"{hour}:{minute}:{second}")
    
    t1 = threading.Thread(target=openWhatsapp,args=(hour,minute,targetGroup,))
    t2 = threading.Thread(target=paste,args = (outputText,postListMessage,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    #print(f"Date: {year}-{month:02d}-{day:02d}, Time: {hour:02d}:{minute:02d}:{second:02d} Successfully Send Whatsapp Message!")
"""
def whapi_sendMessage(message,whapi_group_id):
    

    url = f"{whapi_api_url}messages/text"

    payload = {
        "typing_time": 0,
        "to": whapi_group_id,
        "no_link_preview": False,
        "wide_link_preview": False,
        "body": message
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {whapi_token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    #print(response.text)

def whapi_sendToClient(ai_message,postListMessage,whapi_group_id):
    whapi_sendMessage(ai_message,whapi_group_id)
    if len(postListMessage) > 20:
        postListMessageList = postListMessage.split("________")
        i = 1
        for text in postListMessageList[:-1]:
            heading = f"\n******帖文{i}******\n"
            heading += text
            whapi_sendMessage(heading,whapi_group_id)
            i += 1
    else:
        print("NO Output Text!")
    