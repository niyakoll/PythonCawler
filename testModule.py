#example for using nonJsCrawer module to develop web monitor project
# @Time : 2025/9/24 17:10
# @Author : LoKaYin
# @File : testModule.py
# @Desc : test nonJsCrawer module

import nonJsCrawer

tid = 23814257
for i in range(0,5):
    try:
        nonJsCrawer.sample_babyKindom(str(tid))
    except:
        print(f"主題代號{tid}爬取失敗")
        continue
    finally:
        tid+=1