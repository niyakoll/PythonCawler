import pywhatkit as pwk
import schedule
import time
import pyperclip
import pyautogui
import threading
import getCurrentTime


def paste(input:str):
    print("t2 open!")
    time.sleep(120)
    print("t2 started!")
    pyperclip.copy(input)
    #time.sleep(1)
    pyautogui.hotkey("Ctrl","V")
    pyautogui.hotkey("enter")

def openWhatsapp(hour,minute,targetGroup):
    currentTime = getCurrentTime.getCurrentTime()
    second = currentTime['second']
    openTime = 60 - second
    print(openTime)
    print("t2 started!")
    pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+2, wait_time=15, tab_close=True, close_time=120)

def sendMessage(outputText,targetGroup):
    currentTime = getCurrentTime.getCurrentTime()

    year = currentTime['year']
    month = currentTime['month']
    day = currentTime['day']
    hour = currentTime['hour']
    minute = currentTime['minute']
    second = currentTime['second']
    print("I'm working...")
    print(f"{hour}:{minute}:{second}")
    
    t1 = threading.Thread(target=openWhatsapp,args=(hour,minute,targetGroup,)).start()
    t2 = threading.Thread(target=paste,args = (outputText,)).start()
    t1.join()
    t2.join()
    print(f"Date: {year}-{month:02d}-{day:02d}, Time: {hour:02d}:{minute:02d}:{second:02d} Successfully Send Whatsapp Message!")

#use case example
#sendMessage("我是測試信息","LZTI3ZH7xkq3Nm9zoZyohX")
