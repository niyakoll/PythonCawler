from datetime import datetime
import pytz


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
    

