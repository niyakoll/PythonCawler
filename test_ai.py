from openai import OpenAI
import json
#def openrouter(api_key,input_text,model):
prompt = f"""你是一位社交平台留言分析專家，請根據以下來自Threads的數據，幫我分析這些網上帖文和留言，
並且總結成一個不多於1000字的分析報告，報告以列點形式表示:
輸出內容要求如下:
1. 主要內容摘要: (用一至兩句話總結帖文的主要內容)
2.日期: (帖文發佈的日期)
3. 情緒分析: (分析帖文和留言的整體情緒是正面、負面還是中立，並量化成數字)
4. 讚好數量: (帖文的讚好數量)
5. 留言數量: (帖文的留言數量)
6. 分享數量: (帖文的分享數量)
7. 最負面留言: (列出最負面的留言，並解釋為何這留言被認為是最負面的)以emoji表示情緒強度
8. 最引起關注的留言: (列出最引起關注的留言，並解釋為何這留言被認為是最引起關注的)
9. 結論: (根據以上分析，給出總結)

請用繁體中文回答，以情緒強度、留言數量及讚好數量評估並篩選出需要注意的帖文和留言。
以下是數據:\n
"""
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
with open("C:/Users/user/pythonSpider/threadOutput_test.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    post = data[0]['thread']['text']
    post_like = data[0]['thread']['like_count']
    post_replies = data[0]['thread']['direct_reply_count']
    post_link = data[0]['thread']['url']
    replies =""
    for reply in data[0]['replies']:
        replies += reply['text'] + "\n"
    #print(data[2]['thread']['text'])
    #print(data[0]['thread']['text'])
    #print(data[0]['replies'][0]['text'])
    #print(replies)
    prompt += f"帖文內容:{post}\n讚好數量:{post_like}\n留言數量:{post_replies}\n帖文連結:{post_link}\n回覆內容:{replies}\n帖文二:{data[2]['thread']['text']}"
    #prompt.append(data)
    #print(prompt[0])


completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  model="tngtech/deepseek-r1t2-chimera:free",
  messages=[
    {
      "role": "user",
      "content": prompt
    }
  ]

)



print(completion.choices[0].message.content)
