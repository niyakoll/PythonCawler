from bs4 import BeautifulSoup  #网页解析，获取数据
import re  #正则表达式，进行文字匹配
import urllib.request, urllib.error  #制定URL，获取网页数据
#import xlwt  #进行excel操作
import requests
#import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time



#url = 'https://www.threads.com/@faustinemakmak/post/C8oCIStyLen'
url = 'https://lihkg.com/thread/3991187/page/1'
#url = 'https://www.discuss.com.hk/viewthread.php?tid=31970736&utm_source=festival_home&utm_medium=home&utm_campaign=711'
options = Options()
options.add_argument('--ignore-certificate-errors')
#options.add_argument('user-agent="Mozilla/5.0"')
options.add_argument("--headless=new")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
driver.get(url)
time.sleep(2)

print("\nsuccess! 0")
"""
commentTag = driver.find_element(By.ID,'postmessage_573768850')
comment = commentTag.text
print("\nsuccess! 1")
print(comment)
print(comment+"\nsuccess!2")
print("\nsuccess!3")
"""
#print(driver.page_source)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
title = soup.find('title').text
print(title)
try:
    
    commentSet = soup.find_all('div', attrs={'class':'_2cNsJna0_hV8tdMj3X6_gJ'})
    for commentTag in commentSet:
        comment = commentTag.get_text()
        print(comment)
        
        
except:
  print("Error!")
finally:
    commentCount = len(commentSet)
    print(f"共找到{commentCount}條留言")

driver.quit()