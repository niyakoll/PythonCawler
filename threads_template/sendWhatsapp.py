import pywhatkit as pwk
import schedule
import time
import pyperclip
import pyautogui
import threading
import getCurrentTime
import result_text_cleaning
from datetime import datetime
import requests
import json
import os

whapi_token = ""
whapi_api_url = ""
path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    whapi_token = manifest["whapi_token"]
    whapi_api_url = manifest["whapi_api_url"]

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
    currentTime = getCurrentTime.getCurrentTime()
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
    """
    if second >= 50:
        pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+1, wait_time=20, tab_close=True, close_time=85)
    elif second <= 20:
        pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+1, wait_time=45, tab_close=True, close_time=60)
    else:
        pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+1, wait_time=25, tab_close=True, close_time=80)
    """


def sendMessage(outputText,postListMessage,targetGroup):
    currentTime = getCurrentTime.getCurrentTime()

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
    print(f"Date: {year}-{month:02d}-{day:02d}, Time: {hour:02d}:{minute:02d}:{second:02d} Successfully Send Whatsapp Message!")

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
    