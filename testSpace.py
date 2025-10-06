if __name__ == "__main__":
    output = scrape_thread("https://www.threads.com/@cantalkpop/post/DPIcpLNAT-_")
    formatOutput = json.dumps(output, indent=4, ensure_ascii=False)
    #print(formatOutput)
    file_path = r"C:\Users\Alex\threadOutput2.json"
    

# Open the file in write mode ('w') and use json.dump() to write the data
try:
    with open(file_path, 'w',encoding="utf-8") as f:
        #json.dump(output, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
        json.dump(output, f, indent=4,ensure_ascii=False) 
    print(f"JSON file successfully created at: {file_path}")
except IOError as e:
    print(f"Error creating JSON file at {file_path}: {e}")
#print(len(threadList))
#print(threadItemList)

file_path = fr"C:\Users\Alex\threadOutput{json_number}.json"
    try:
        with open(file_path, 'w',encoding="utf-8") as f:
        #json.dump(output, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
            json.dump(reply, f, indent=4,ensure_ascii=False) 
            print(f"JSON file successfully created at: {file_path}")
    except IOError as e:
        print(f"Error creating JSON file at {file_path}: {e}")



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

keyword_list = [
    "TVB", "容祖兒", "黎明", "張天賦", "林家謙", "陳健安", "VIUTV", "古天樂", "林奕匡",
    "陳百祥", "張敬軒", "劉德華", "湯令山", "魏浚笙", "馮允謙", "李駿傑", "林峯", "李駿傑", "陳柏宇",
    "曾志偉", "古巨基", "張學友", "陳蕾", "Kiri T", "黃淑蔓", "呂爵安", "宣萱", "呂爵安", "布志綸",
    "王祖藍", "謝霆鋒", "郭富城", "洪嘉豪", "Tyson Yoshi", "雲浩影", "盧瀚霆", "游學修", "盧瀚霆", "葉巧琳",
    "樂易玲", "曾傲棐", "梁朝偉", "歸綽嶢", "Serrini", "Amy Lo", "何啟華", "陳苡臻", "何啟華", "女歌手",
    "黎瑞剛", "許靖韻", "吳鎮宇", "陳凱詠", "阿正", "姜濤", "岑珈其", "姜濤", "黃妍",
    "VIVA", "黃秋生", "周殷庭", "阿正", "姜濤", "岑珈其", "姜濤", "黃妍",
    "李幸倪", "曾比特", "ANSONBEAN", "江𤒹生", "吳肇軒", "江𤒹生", "力臻",
    "楊千嬅", "柳應廷", "林家熙", "柳應廷",
    "邱士縉", "倪安慈", "邱士縉",
    "邱傲然", "何洛瑤", "邱傲然",
    "邱彥筒",
    "陳泳伽",
    "蘇雅琳",
    "沈貞巧",
    "李芯駖",
    "王家晴",
    "蘇芷晴",
    "長實", "可口可樂", "大家樂", "麥當奴", "激光脫毛", "TESLA", "幸福傷風素", "八達通",
    "李嘉誠", "雪碧", "大快活", "KFC", "皮秒 PICO", "byd 海豹", "必利痛", "支付寶",
    "PCCW", "芬達", "評仔三哥", "HIFU", "byd 海獅", "樂信感冒靈", "WECHAT PAY",
    "百佳", "玉泉忌廉", "保濟丸", "PAYME",
    "喇叭牌正露丸", "轉數快",
    "胃仙U", "BOC PAY"
]