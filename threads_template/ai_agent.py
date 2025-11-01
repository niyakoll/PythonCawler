import result_text_cleaning
import json
from openai import OpenAI
import time
import os
#Get setting from manifest json file
#client = ""
#keyword_list = []
interval = 30
#target_path = ""
#light_scan_mode = False
#target_whatsapp_group = ""
ai_agent_api_key = ""
ai_model = []
proxies = []

path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    MarketingClient = manifest["client"]
    interval = manifest["interval"]
    ai_agent_api_key = manifest["ai_agent_api_key"]
    ai_model = manifest["ai_model"]
    proxies = manifest["proxies"]
    prompt = manifest["ai_prompt"]
#def openrouter(api_key,input_text,model):
ai_input = ""
def callAI(resultText)->str:
    now = result_text_cleaning.timestampConvert(time.time())
    print(f"{now} : Start Calling AI Agent.")
    
    ai_input = prompt+"\n"+resultText
    ai_reply = "免費AI暫時用完，請聯絡我們:12345678!"
    try:
        ai_reply = ai_model_shift(ai_input,0)
    except:
        try:
            ai_reply = ai_model_shift(ai_input,1)
        except:
            try:
                ai_reply = ai_model_shift(ai_input,2)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    finally:
        return ai_reply
    

def ai_model_shift(inputText,number):
    print(f"Using Ai model {ai_model[number]}")
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=ai_agent_api_key[0],
    )
    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    model=ai_model[number],
    messages=[
        {
        "role": "user",
        "content": inputText
        }
    ]

    )
    ai_reply = str(completion.choices[0].message.content)
    #print(completion.choices[0].message.content)
    
    return ai_reply