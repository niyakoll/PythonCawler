import pywhatkit as pwk
from datetime import datetime
import pytz
import schedule
import time
import pyperclip
import pyautogui
import threading

def getCurrentTime()->dict:
    currentTime = {}
    # Get current time in Hong Kong (HKT)
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    hk_time = datetime.now(hk_tz)

    # Format date and time
    formatted_time = hk_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    print(formatted_time)  # Output: 2025-10-09 08:53:00 HKT

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
def paste(input:str):
    print("t2 open!")
    time.sleep(60)
    print("t2 started!")
    pyperclip.copy(input)
    #time.sleep(1)
    pyautogui.hotkey("Ctrl","V")
    pyautogui.hotkey("enter")
def openWhatsapp(hour,minute):
    print("t2 started!")
    pwk.sendwhatmsg_to_group("JrwTpeYb4A4Gvtelv3bw3Y", " ",time_hour=hour, time_min=minute+1, wait_time=80, tab_close=True, close_time=1)

def job():
    currentTime = getCurrentTime()
    year = currentTime['year']
    month = currentTime['month']
    day = currentTime['day']
    hour = currentTime['hour']
    minute = currentTime['minute']
    second = currentTime['second']
    print("I'm working...")
    print(f"{hour}:{minute}:{second}")
    
    t1 = threading.Thread(target=openWhatsapp,args=(hour,minute,)).start()
    t2 = threading.Thread(target=paste,args = ("楊老闆!")).start()
    #pwk.sendwhatmsg_to_group("D5pbC6ipk3G3NMVMWOFA2f", f"Dear Mr.Yeung! I am Auto Testing Message! push at{currentTime['hour']}:{currentTime['minute']}",time_hour=currentTime['hour'], time_min=currentTime['minute']+3, wait_time=20, tab_close=True, close_time=1)
    #pwk.sendwhatmsg_to_group("JrwTpeYb4A4Gvtelv3bw3Y", " ",time_hour=currentTime['hour'], time_min=currentTime['minute']+1, wait_time=20, tab_close=True, close_time=1)
    
schedule.every(60).seconds.do(job).run()
while True:
    schedule.run_pending()
    time.sleep(1)