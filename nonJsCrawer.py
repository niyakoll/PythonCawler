# @Time : 2025/9/27 16:58
# @Author : LoKaYin
# @File : nonJsCrawer.py
# @Desc : Building Module for non javascript dynamic web crawer
#provide function for URL to HTML, use BeautifulSoup to parse HTML
#URLtoHTML: input URL, return HTML string
#titleString: input HTML string, return title string
#DateString: input HTML string, element, classOrId, name, return list of date string
#CommentString: input HTML string, element, classOrId, name, return list of comment string
#totalPage: input HTML string, element, classOrId, name, return total page number string    
#sample: test with different domain

from bs4 import BeautifulSoup  #網頁分析，獲取所需資料
import re  #正則表達式，文字比對
import urllib.request, urllib.error  #透過URL取得網頁資料
import requests
from urllib.parse import quote
import time #延遲
import pandas as pd #儲存資料至excel檔案
import logging
import json

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
        logging.debug(title)
    return title

def DateString(html,element,classOrId,name)->list:
    soup = BeautifulSoup(html, "html.parser")
    #dateSet = soup.find_all(element,classOrId = className,attrs = {attrs})
    dateSet = soup.find_all(element,attrs = {classOrId : re.compile(name)})
    dateList = []
    for i in dateSet:
        date = str(i.get_text()).replace("\n","")
        dateList.append(date)
        logging.debug(dateList)
    return dateList

def CommentString(html,element,classOrId,name)->list:
    soup = BeautifulSoup(html, "html.parser")
    commentSet = soup.find_all(element,attrs = {classOrId : re.compile(name)})
    commentList = []
    for i in commentSet:
        comment = str(i.get_text()).replace("\n","")
        commentList.append(comment)
    return commentList

def searchKeyword(html,element,classOrId,name)->list:
    soup = BeautifulSoup(html, "html.parser")
    searchSet =  soup.find_all(element,attrs={classOrId:name})
    searchUrlList = []
    for i in searchSet:
        url = str(i.select_one('a').get('href'))
        searchUrlList.append(url)
    return searchUrlList

def totalPage(html,element,classOrId,name)->str:
    soup = BeautifulSoup(html, "html.parser")
    pageSet = soup.find_all(element,attrs = {classOrId : re.compile(name)})
    for item in pageSet:
        if item.get_text()!="" and item.get_text()!=" ":
            print(f"page test:{item.get_text()}")
            page = str(item.get_text()).replace(" ","")
            totalPageNumber = page[-1]
            logging.debug(page)           
    return totalPageNumber

#example function for testing
#註解標注需更改的部分
def sample_babyKindom(tid):
    page = 1
    haveNextPage = True
    TotalcommentList = []
    postCreateDate = ""
    totalPageNumber = 1
    try:
        while haveNextPage == True:
            #目標網址，tid為主題編號，page為頁數
            url = f'https://www.baby-kingdom.com/forum.php?mod=viewthread&tid={tid}&extra=page%3D1&page={page}'
            html = URLtoHTML(url)
            title = titleString(html)
            date = DateString(html,"em","id","^auth")#更改此行的element,classOrId,name參數以取得正確的日期
            if page == 1:
                postCreateDate = date[1]
                postCreateDate = postCreateDate.replace("發表於 ","")#更改此行以取得正確的日期
                
            commentPerPage = CommentString(html,'div',"class",'^t_fsz')#更改此行的element,classOrId,name參數以取得正確的留言
            TotalcommentList.extend(commentPerPage)#儲存所有留言
            totalPageNumber = totalPage(html,"button","class","form-control btn btn-pagination dropdown-toggle")#更改此行的element,classOrId,name參數以取得正確的總頁數
            #print(f"網址:{url}\n標題:{title}\n日期:{date[1]}\n頁數:{totalPageNumber}頁\n留言有{len(comment)}則")
            print(f"第{page}頁留言:")
            
            for i in commentPerPage:#顯示當前頁數的所有留言
                print("\n")
                print(i)
            
            page += 1
            if page>int(totalPageNumber):#判斷是否有下一頁
                haveNextPage = False
        
    except Exception as e:
        print(f"這個主題共有{page}頁")
    finally:
        print(f"網址:{url}\n標題:{title}\n創建主題日期:{postCreateDate}\n頁數:{totalPageNumber}頁\n此主題共有留言{len(TotalcommentList)}則")#顯示主題資訊
        print(f"完成主題{title}的爬取")

def sample_hkdiscuss(tid):
    page = 1
    haveNextPage = True
    TotalcommentList = []
    postCreateDate = ""
    postTotalPage = "1"
    try:
        while haveNextPage == True:
            #目標網址，tid為主題編號，page為頁數
            url = f'https://www.discuss.com.hk/viewthread.php?tid={tid}&extra=&page={page}'
            html = URLtoHTML(url)
            title = titleString(html)
            date = DateString(html,"div","class","^post-date")#更改此行的element,classOrId,name參數以取得正確的日期
            if page == 1:
                postCreateDate = date[1]
                postCreateDate = postCreateDate.replace("發表於 ","").replace(" ","")#更改此行以取得正確的日期
                
            commentPerPage = CommentString(html,'span',"id",'^postorig_')#更改此行的element,classOrId,name參數以取得正確的留言
            TotalcommentList.extend(commentPerPage)#儲存所有留言

            try:
                #totalPageNumber = totalPage(html,"a","class","last")#更改此行的element,classOrId,name參數以取得正確的總頁數
                if(page==1):
                    result = html.find("var maxpage =  ")
                    totalPageNumber = html[result+len("var maxpage =  "):result+len("var maxpage =  ")+1]
                    postTotalPage = totalPageNumber
            except:
                totalPageNumber = postTotalPage 
            
            #print(f"網址:{url}\n標題:{title}\n日期:{date[1]}\n頁數:{totalPageNumber}頁\n留言有{len(comment)}則")
            print(f"\n網址:{url}\n第{page}頁留言:")
            
            for i in commentPerPage:#顯示當前頁數的所有留言
                print("\n")
                print(i)
            
            page += 1
            if page>int(postTotalPage):#判斷是否有下一頁
                haveNextPage = False
        
    except Exception as e:
        print(f"這個主題共有{page}頁")
    finally:
        print(f"網址:{url}\n標題:{title}\n創建主題日期:{postCreateDate}\n頁數:{postTotalPage}頁\n此主題共有留言{len(TotalcommentList)}則")#顯示主題資訊
        print(f"完成主題{title}的爬取")    
    

def search_babyKindom(keywordList:list)->list:
    keywordList = keywordList
    resultList = []
    for keyword in keywordList:
        keyword = quote(keyword)
        html = URLtoHTML(f"https://www.baby-kingdom.com/search.php?mod=forum&searchid=1758984377&srchtxt={keyword}&orderby=lastpost&ascdesc=desc&searchsubmit=yes&keyword={keyword}&")
        #print(html)
        urlList = searchKeyword(html,"h3","class","xs3") 
        resultList.extend(urlList)
    print(f"共找到{len(resultList)}個相關主題")
    return resultList

def search_by_keyword_babykindom(keywordList:list):
    resultList = search_babyKindom(keywordList)
    #print(len(resultList))
    for i in range(0,2):
        tid = str(resultList[i])[-8:]
        sample_babyKindom(tid)

def search_by_keyword(kewordList:list,domain:str):
    match domain:
        case "babykingdom":
            search_by_keyword_babykindom(kewordList)
        case "hkdiscuss":
            print("not support yet!")

#example   
keywordList = ['淘寶','cola']
search_by_keyword(keywordList,"babykingdom")


"""
#test area:########################################################
#sample_babyKindom("23749399")
#sample_hkdiscuss("32043124")

html = URLtoHTML("https://www.discuss.com.hk/viewthread.php?tid=32043123&extra=&page=1")
soup = BeautifulSoup(html, "html.parser")
result = html.find("var maxpage =  ")
result = html[result+len("var maxpage =  "):result+len("var maxpage =  ")+1]
print(result)

# Client data as a Python dictionary
test_data = {
    "Domain": [
        {
            "url": "https://www.baby-kingdom.com/forum.php?mod=viewthread&tid={tid}&extra=page%3D1&page={page}",
            "tid": "我唔想入錶",
            "date": "24-09-2025",
            "topic": {
                "url": "https://www.baby-kingdom.com/forum.php?mod=viewthread&tid={tid}&extra=page%3D1&page={page}",
                "tid": "23749399",
                "date": "2025-09-24",
                "totalPage": "5",
                "commentList": {
                    "comment": "入錶好貴!",
                    "page": "1",
                    "keywords": ["入錶","高齡","淘寶"]
                    
                }
            },
            "active": True
        },
        {
            "id": "CL002",
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "phone": "987-654-3210",
            "address": {
                "street": "456 Oak Ave",
                "city": "Otherville",
                "state": "NY",
                "zip_code": "10001"
            },
            "active": False
        }
    ]
}

# Define the filename for the JSON file
json_filename = "client_information.json"

# Write the client data to the JSON file
try:
    with open(json_filename, 'w',encoding='utf-8') as f:
        json.dump(test_data, f, indent=4,ensure_ascii=False)
    print(f"JSON file '{json_filename}' created successfully.")
except IOError as e:
    print(f"Error writing to file: {e}")

# Optional: Read the JSON file back to verify
try:
    with open(json_filename, 'r',encoding='utf-8') as f:
        loaded_data = json.load(f)
    print("\nContent of the created JSON file:")
    print(json.dumps(loaded_data, indent=4,ensure_ascii=False))
except IOError as e:
    print(f"Error reading from file: {e}")
#test area end########################################################
"""