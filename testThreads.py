import json
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
import threading
import time
#from urllib.parse import quote

# specify the request headers
extra_headers = {
    'sec-ch-ua': '\'Not A(Brand\';v=\'99\', \'Google Chrome\';v=\'121\', \'Chromium\';v=\'121\'',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept-Language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com/',
    "Cache-Control": "no-cache"
    
}
cache_header = "'Cache-Control': 'max-age=31536000'"
testHiddenSet1 = []
testHiddenSet2 = []
testHiddenSet3 = []
testHiddenSet4 = []
tempStorge = []
def parse_thread(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    result = jmespath.search(
        """{
        text: post.caption.text,
        published_on: post.taken_at,
        id: post.id,
        pk: post.pk,
        code: post.code,
        username: post.user.username,
        user_pic: post.user.profile_pic_url,
        user_verified: post.user.is_verified,
        user_pk: post.user.pk,
        user_id: post.user.id,
        has_audio: post.has_audio,
        reply_count: view_replies_cta_string,
        direct_reply_count: post.text_post_app_info.direct_reply_count,
        like_count: post.like_count,
        images: post.carousel_media[].image_versions2.candidates[1].url,
        image_count: post.carousel_media_count,
        videos: post.video_versions[].url
        
    }""",
        data,
    )
    result["videos"] = list(set(result["videos"] or []))
    if result["reply_count"] and type(result["reply_count"]) != int:
        
        
        #result["reply_count"] = int(result["reply_count"].split(" ")[0])
        result["reply_count"] = 10
    result[
        "url"
    ] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
    return result


def scrape_thread(url: str,thread_keyword) -> dict:
    """Scrape Threads post and replies from a given URL"""
    
    with sync_playwright() as pw:
        # start Playwright browser
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        
        page = context.new_page()
        cdp_session = context.new_cdp_session(page)
        # Enable network domain
        #cdp_session.send("Network.enable")
        cdp_session.send("Network.clearBrowserCookies")
        cdp_session.send("Network.setExtraHTTPHeaders", {"headers": extra_headers})
        # Clear browser cache
        cdp_session.send("Network.clearBrowserCache")
        #page.set_extra_http_headers(extra_headers)

        # go to url and wait for the page to load
        page.goto(url)
        # wait for page to finish loading
        page.wait_for_selector("[data-pressable-container=true]")
        # find all hidden datasets
        selector = Selector(page.content())
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        #print(f"Originally, there are total :{len(hidden_datasets)} hidden sets.")
        
        
        #print(hidden_datasets)
        # find datasets that contain threads data
        for hidden_dataset in hidden_datasets:
            # skip loading datasets that clearly don't contain threads data
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            testHiddenSet1.append(hidden_dataset)
            #print(f"After filting ScheduledServerJS(not include), there are total :{len(testHiddenSet1)} hidden sets.")
            #if keyword not in hidden_dataset:
                #continue
            if "thread_items" not in hidden_dataset:
                continue
            testHiddenSet2.append(hidden_dataset)
            #print(f"After filting thread_items(not include), there are total :{len(testHiddenSet2)} hidden sets.")
            data = json.loads(hidden_dataset)
            
            # datasets are heavily nested, use nested_lookup to find 
            # the thread_items key for thread data
            thread_items = nested_lookup("thread_items", data)
            
            #print(thread_items)
            if not thread_items:
                continue
            if thread_keyword not in str(thread_items):
                continue
            testHiddenSet3.append(hidden_dataset)
            print(f"After json loads and nested lookup thread_items, there are total :{len(testHiddenSet3)} hidden sets.")

            # use our jmespath parser to reduce the dataset to the most important fields
            threads = [parse_thread(t) for thread in thread_items for t in thread]
            
            
            return {
                
                # the first parsed thread is the main post:
                "thread": threads[0],
                # other threads are replies:
                "replies": threads[1:],
            }
        raise ValueError("could not find thread data in page")
    page.close()
    browser.close()


    
    

def writeJson(filePath:str,data:dict):
    try:
        with open(filePath, 'w',encoding="utf-8") as f:
            json.dump(data, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
        print(f"JSON file successfully created at: {filePath}")
    except IOError as e:
        print(f"Error creating JSON file at {filePath}: {e}")
    finally:
        return tempStorge

def add_hidden_comment(url: str,thread_keyword):
    try:
        reply = scrape_thread(url,thread_keyword)
        del reply["thread"]
        del reply["replies"][0]
        tempStorge.append(reply)
    except ValueError as e:
        print(f"Error in add_hidden_comment function: {e}")
    finally:
        return tempStorge
def find_hidden_comment(post:Dict,thread_keyword):
    try:
        for reply in post["replies"]:
            direct_reply_count = reply["direct_reply_count"]
            if direct_reply_count and direct_reply_count > 0:
                username = reply["username"]
                code = reply["code"]
                text = reply["text"]
                print(f"this comment {text} has {direct_reply_count} replies")
            #print(username)
            #print(code)
                url =f"https://www.threads.com/@{username}/post/{code}"
                print(url)
                add_hidden_comment(url,thread_keyword)
    except ValueError as e:
        print(f"Error in find_hidden_comment function: {e}")
    finally:
        return tempStorge
            
def search_one_keyword(keword:str)->list:
    url_list = []
    try:
        search_url = f"https://www.threads.com/search?q={keword}&serp_type=recent"
        search_result = scrape_thread(search_url,keword)
        firstPost = search_result["thread"]
        firstPostUserName = firstPost["username"]
        firstPostCode = firstPost["code"]
        firstPostUrl = f"https://www.threads.com/@{firstPostUserName}/post/{firstPostCode}"
        url_list.append(firstPostUrl)
        for post in search_result["replies"]:
            postUserName = post["username"]
            postCode = post["code"]
            postUrl = f"https://www.threads.com/@{postUserName}/post/{postCode}"
            url_list.append(postUrl)
    except ValueError as e:
        print(f"Error scraping keyword {keword}: {e}")
    finally:
        return url_list

def search_one_keyword_all_comment(url_list:list,thread_keyword)->dict:
    i = 1
    try:
        if url_list != []:
            for postUrl in url_list:
                try:
                    output = scrape_thread(postUrl,thread_keyword)
                    tempStorge.append(output)
                    print(f"Post{i} start Listening... ")
                    i+=1
                except ValueError as e:
                    print(f"Error scraping post {postUrl}: {e}")
                    continue
                try:
                    find_hidden_comment(output,thread_keyword)
                except ValueError as e:
                    print(f"Error scraping hidden comments for post {postUrl}: {e}")
                    continue
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:

        return tempStorge

def search_multiple_keyword(keyword_list:list,file_path)->dict:
    try:
        for keyword in keyword_list:
            time.sleep(2)
            try:
                url_list = search_one_keyword(keyword)
                print(f"Keyword {keyword} Listening...")
            except ValueError as e:
                print(f"Error scraping keyword {keyword}: {e}")
                continue
            try:
                search_one_keyword_all_comment(url_list,keyword)
            except ValueError as e:
                print(f"Error scraping all comments for keyword {keyword}: {e}")
                continue
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        writeJson(file_path,tempStorge)
        return tempStorge





file_path = "C:/Users/Alex/threadOutput5.json"

#test_search = scrape_thread("https://www.threads.com/search?q=%E5%BC%B5%E5%A4%A9%E8%B3%A6&serp_type=recent")
#print(test_search)
#writeJson(r"C:/Users/Alex/threadSearchOutput.json",test_search)
if __name__ == "__main__":
    #output = scrape_thread("https://www.threads.com/@cantalkpop/post/DPIcpLNAT-_")
    #tempStorge.append(output)
    #find_hidden_comment(output)
    #writeJson(file_path,tempStorge)
    keyword_list_1 = ["張天賦", "劉德華", "陳蕾", "張學友", "張國榮", "陳奕迅", "郭富城", "黎明", "周潤發", "梁朝偉",
    "黃子華", "曾志偉", "鄭中基", "林家謙", "Serrini", "鄭欣宜", "許冠傑", "羅家英", "古巨基", "陳百強",
    "譚詠麟", "張衛健", "陳小春", "謝霆鋒", "容祖兒", "楊千嬅", "何韻詩", "Twins", "衛蘭", "王菲",
    "李克勤", "林宥嘉", "林子祥", "徐小鳳", "草蜢", "Beyond", "達明一派", "黃耀明", "關正傑", "甄妮"]
    
    keyword_list_2 = ["呂方", "張國燾", "側田", "林保怡", "蘇永康", "梁漢文", "洪天明", "吳業坤", "陳柏宇",
    "炎明熹", "姜濤", "Mirror", "Error", "陳卓賢", "詹天文", "黃明志", "AGA", "吳若希", "MC張天賦",
    "周柏豪", "吳千語", "黃德斌", "朱栢康", "陳蕾樂隊", "林二汶", "盧巧音", "葉蒨文", "蔡琴", "費玉清",
    "張明敏", "羅大佑", "李壽全", "溫拿樂隊", "肥龍", "王杰", "湯寶如", "杜德偉", "李玟", "鄭伊健",
    "梁靜茹", "孫燕姿", "周杰倫", "蔡依林", "林俊傑", "王力宏", "陶喆", "張韶涵", "S.H.E", "五月天"]

    keyword_list_3 = ["英皇娛樂", "華星唱片", "環球唱片", "環球音樂", "華納音樂", "Sony Music", "EMI", "寶麗金", "星夢娛樂", "ViuTV",
    "TVB", "無綫電視", "亞洲電視", "Now TV", "香港電台", "嘉禾娛樂", "寰亞媒體", "太陽娛樂", "中國3D數碼娛樂", "MakerVille",
    "Team Wang", "J-Team", "華納唱片", "BMG", "PolyGram", "ATV音樂", "上華唱片", "中國創意數碼", "藝能動音", "拿索斯唱片",
    "OLAY", "LAURA MERCIER", "shu uemura", "Drunk Elephant", "KAIBEAUTY", "Nude Story", "WULT", "Sephora", "ZALORA", "Harbour City",
    "OP Beauty", "ELLE", "VOGUE", "Harper's Bazaar", "Cosme", "FashionGuide", "iStyle", "東薈城Outlet", "佛羅倫斯小鎮", "杏花新城",
    "海怡半島Outlet", "Prada Outlet", "香港品牌", "Brand HK", "亞洲國際都會", "香港娛樂圈", "香港歌手", "香港明星", "香港藝人"]
    keyword_list_4 = ["Cantopop", "廣東歌", "香港電影", "香港電視劇", "金像獎", "金曲獎", "十大中文金曲", "叱咤樂壇", "新城國語力", "RTHK音樂",
    "Mirror成員", "姜濤粉絲", "炎明熹Gigi", "陳蕾演唱會", "張天賦專輯", "劉德華演唱會", "四大天王", "無綫藝人", "ViuTV藝人", "英皇歌手",
    "華星天王", "環球巨星", "Sony藝人", "華納歌手", "寶麗金經典", "星夢新人", "TVB劇集", "香港偶像", "樂壇天后", "影帝影后",
    "周星馳", "成龍", "李連杰", "甄子丹", "吳彥祖", "古天樂", "劉青雲", "黃秋生", "吳鎮宇", "任達華"]
    keyword_list_5 = ["張家輝", "林峯", "陳浩民", "袁詠儀", "楊采妮", "舒淇", "張曼玉", "林青霞", "王菲演唱會", "容祖兒巡演",
    "黃子韜", "鹿晗", "吳亦凡", "EXO", "Big Bang", "Blackpink", "BTS", "K-pop香港", "香港時裝", "時尚品牌",
    "美妝品牌", "護膚品", "化妝品", "香水", "手袋", "鞋履", "珠寶", "手錶", "眼鏡", "服飾",
    "牛仔褲", "T恤", "連身裙", "外套", "圍巾", "帽子", "腰帶", "錢包", "行李箱", "家居用品"]
    keyword_list_6 = ["香港設計師", "本地品牌", "優．惠．港", "名牌特區", "購物天堂", "尖沙咀購物", "銅鑼灣商場", "中環精品", "旺角街頭", " IFC商場",
    "太古廣場", "海港城", "時代廣場", "新世界百貨", "連卡佛", "周大福", "周生生", "謝瑞麟", "佐卡伊", "潘多拉",
    "Tiffany", "Cartier", "Chanel", "Louis Vuitton", "Gucci", "Prada", "Dior", "Hermes", "Burberry", "Versace"]
    keyword_list_7 = ["香港娛樂新聞", "Yahoo娛樂", "東網娛樂", "明報娛樂", "蘋果日報", "頭條日報", "TVB新聞", "ViuTV節目", "無綫節目", "香港綜藝",
    "跑馬地", "紅磡體育館", "亞博館", "演唱會門票", "音樂節", "Clockenflap", "Art Basel", "香港藝術", "電影節", "金馬獎"]
    #search_multiple_keyword(keyword_list_1,file_path)
    t1 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_1,"C:/Users/Alex/stressTest1.json"))
    t2 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_2,"C:/Users/Alex/stressTest2.json"))
    t3 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_3,"C:/Users/Alex/stressTest3.json"))
    t4 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_4,"C:/Users/Alex/stressTest4.json"))
    t5 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_5,"C:/Users/Alex/stressTest5.json"))
    t6 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_6,"C:/Users/Alex/stressTest6.json"))
    t7 = threading.Thread(target=search_multiple_keyword, args=(keyword_list_7,"C:/Users/Alex/stressTest7.json"))
    

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()

    print("All threads started.")

    