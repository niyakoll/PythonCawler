import pywhatkit as pwk
import schedule
import time
import pyperclip
import pyautogui
import threading
import getCurrentTime
import result_text_cleaning
def directPasteAndSend(input:str):
    pyperclip.copy(input)
    time.sleep(1)
    pyautogui.hotkey("Ctrl","V")
    pyautogui.hotkey("enter")
    

def paste(AIinput:str,postListMessage:str):
    time.sleep(120)
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
def openWhatsapp(hour,minute,targetGroup):
    currentTime = getCurrentTime.getCurrentTime()
    second = currentTime['second']
    openTime = 60 - second
    #print(openTime)
    #print("t2 started!")
    pwk.sendwhatmsg_to_group(targetGroup, " ",time_hour=hour, time_min=minute+2, wait_time=15, tab_close=True, close_time=120)

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

#use case example
#sendMessage("我是測試信息","LZTI3ZH7xkq3Nm9zoZyohX")
