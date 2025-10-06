from bs4 import BeautifulSoup  #网页解析，获取数据
import re  #正则表达式，进行文字匹配
import urllib.request, urllib.error  #制定URL，获取网页数据
#import xlwt  #进行excel操作
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

def URLtoHTML(url):
    i = random.randint(0,3)
    time.sleep(i)
    try:
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
        html = driver.page_source
        driver.quit()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        html = ""
    finally:
        return html
def titleString(html):
    soup = BeautifulSoup(html, 'html.parser')
    titleSet = soup.find('title')
    title = titleSet.get_text()
    return title
def pageCount(html,className):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        pageSet = soup.find('div', attrs={'class':className})
        pageText = pageSet.get_text()
        pageNumber = pageText[-3]
    except Exception as e:
        print(f"Error extracting page count: {e}")
        pageNumber = 1
    finally:
        return pageNumber


def onePageCommentPerPost(html,className):
    onePageCommentList = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        commentSet = soup.find_all('div', attrs={'class':className})
        for commentTag in commentSet:
            comment = commentTag.get_text()
            onePageCommentList.append(comment)   
    except Exception as e:
        print(f"Error extracting comments: {e}")
    finally:
        commentCount = len(onePageCommentList)
        print(f"共找到{commentCount}條留言")
        return onePageCommentList
def allPageCommentPerPost(url:str,className):
    allPageCommentList = {}
    page = 1
    #first page, find total page number
    html = URLtoHTML(url)
    
    try:
        totalPage = int(pageCount(html,'_1H7LRkyaZfWThykmNIYwpH'))
        print(f"共{totalPage}頁留言")
    except Exception as e:
        print(f"Error extracting total page count: {e}")
        totalPage = 1
    onePageCommentList = onePageCommentPerPost(html,className)
    print(f"正在抓取第{page}頁留言...")
    allPageCommentList.append({page:onePageCommentList})
    if totalPage == 1:
        return allPageCommentList
    else:
        page = 2 
    try:
        while page <= int(totalPage):
            url = url[:-1]  # Remove the last character (the page number)
            url = f"{url}{page}"  # Append the current page number
            print(f"正在抓取第{page}頁留言...")
            html = URLtoHTML(url)
            onePageCommentList = onePageCommentPerPost(html,className)
            allPageCommentList.append({page:onePageCommentList})
            page += 1
            print(onePageCommentList)

    except Exception as e:
        print(f"Error extracting comments: {e}")
    finally:
        return allPageCommentList
    

def keywordToUrlList(keyword,className):
    urlList = []
    searchUrl = f"https://lihkg.com/search?q={keyword}&sort=desc_create_time&type=thread"
    try:
        html = URLtoHTML(searchUrl)
        soup = BeautifulSoup(html, 'html.parser')
        urlSet = soup.find_all('a', attrs={'class':className})
        for urlTag in urlSet:
            href = urlTag.get('href')
            fullUrl = f"https://lihkg.com{href}"
            urlList.append(fullUrl)

    except Exception as e:
        print(f"Error fetching search URL {searchUrl}: {e}")
        return urlList
    finally:
        return urlList
def oneKeywordAllComment(keyword):
    allCommentListPerKeyword = {}
    urlList = keywordToUrlList(keyword,'_2A_7bGY9QAXcGu1neEYDJB')
    print(f"共找到{len(urlList)}個相關討論串")
    for url in urlList[0:0]:
        html = URLtoHTML(url)
        title = titleString(html)
        print(f"正在抓取討論串標題：{title}")
        onePostCommentList = allPageCommentPerPost(url,'_2cNsJna0_hV8tdMj3X6_gJ')
        allCommentListPerKeyword.append({title:onePostCommentList})
        print(allCommentListPerKeyword)
    return allCommentListPerKeyword

def writeJson(filePath:str,data:list):
    try:
        with open(filePath, 'w',encoding="utf-8") as f:
            json.dump(data,f, indent=4,ensure_ascii=False)  # indent for pretty-printing
        print(f"JSON file successfully created at: {filePath}")
    except IOError as e:
        print(f"Error creating JSON file at {filePath}: {e}")
    

def keywordListToAllComment(keywordList):
    keywordListToAllCommentDict = []
    for keyword in keywordList:
        oneKeywordAllCommentList = oneKeywordAllComment(keyword)
        keywordListToAllCommentDict.append(oneKeywordAllCommentList)
    return keywordListToAllCommentDict

keywordList = ["張天賦"]
testlist = keywordListToAllComment(keywordList)
writeJson("C:/Users/Alex/lihkgTest1.json",testlist)
print("Success!")
#allPageCommentPerPost('https://lihkg.com/thread/4006470/page/1','_2cNsJna0_hV8tdMj3X6_gJ')
#html = URLtoHTML('https://lihkg.com/thread/3984201/page/1')
#url = 'https://lihkg.com/thread/3991187/page/1'
#urlList = keywordToUrlList("張天賦",'_2A_7bGY9QAXcGu1neEYDJB')
#print(f"共找到{len(urlList)}個相關討論串")
#print(urlList)
#html = URLtoHTML(url)
#title = titleString(html)
#onePageCommentList = onePageCommentPerPost(html,'_2cNsJna0_hV8tdMj3X6_gJ')




