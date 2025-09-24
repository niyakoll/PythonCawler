# @Time : 2025/9/24 17:03
# @Author : LoKaYin
# @File : nonJsCrawer.py
# @Desc : Building Module for non javascript dynamic web crawer
#provide function for URL to HTML, use BeautifulSoup to parse HTML
#URLtoHTML: input URL, return HTML string
#titleString: input HTML string, return title string
#sample: test function

from bs4 import BeautifulSoup  #網頁分析，獲取所需資料
import re  #正則表達式，文字比對
import urllib.request, urllib.error  #透過URL取得網頁資料
import time #延遲
import pandas as pd #儲存資料至excel檔案

def URLtoHTML(url)->str:
    time.sleep(1)#每次request間隔一秒，防止被server ban
    head = {  
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

def titleString(html)->str:
    soup = BeautifulSoup(html, "html.parser")
    titleSet = soup.find('title')
    for i in titleSet:
        title = str(i.get_text())
    return title

def sample():
    url = 'https://www.baby-kingdom.com/forum.php?mod=viewthread&tid=23749399&extra=page%3D1&page='
    html = URLtoHTML(url)
    title = titleString(html)
    print(title)

sample()