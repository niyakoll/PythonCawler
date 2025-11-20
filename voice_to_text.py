#pip install SpeechRecognition PyAudio
#pip install openai
import json
from openai import OpenAI
import time
import os
import speech_recognition as sr
def voice_to_text():
    r = sr.Recognizer()   
    with sr.Microphone() as source:
        print("Say something!")
        r.adjust_for_ambient_noise(source,duration=1) # Adjust for ambient noise
        audio = r.listen(source) # Listen for audio input
        try:
            text = r.recognize_google(audio,language="zh-CN")
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}") 

def callAI(resultText)->str:
    prompt = "你是一個專業的語音助理，請根據用戶的語音內容進行回覆，回覆內容需簡短有用且具體。"
    ai_input = prompt+"\n"+resultText
    ai_reply = ""
    try:
        ai_reply = ai_model_shift(ai_input,0)
    except:
        try:
            ai_reply = ai_model_shift(ai_input,1)
        except:
            try:
                ai_reply = ai_model_shift(ai_input,2)
            except Exception as e:
                print(f"ai_agent callAI: {e}")
    finally:
        return ai_reply
    

def ai_model_shift(inputText):
    #print(f"Using Ai model {ai_model[number]}")
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    )
    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    model="tngtech/deepseek-r1t2-chimera:free",
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

text = voice_to_text()
aiOutput = ai_model_shift(text)
print(aiOutput)