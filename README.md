Listening Tool For Threads

This repository integrates a python scraping tool for threads and a simple web application panel by using flask. The following instruction will explain the function of each file and how to deploy in local, xampp and cloud environments.

Prerequisite

This repository is a python base program, you should first make sure you have python installed.

Install python in window(bash)

.\python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

verify
python –version

Content

1. Deploy at local 

2. Deploy at xampp

3. Deploy at cloud (AWS EC2)

4. Directory Explanation

5. External API service setup
Deploy at Local

Install dependencies
at bash(go to the ltc directory):

pip install -r requirements.txt 

1. Manually configure manifest.json

Follow the format at the client_panel:
*target_whatsapp_group can be empty
*whapi_group_id can follow the following guide

"run" :
 set true to run this client

"message_interval" : 
interval (minutes)that the client will receive message(not the scrapping interval),only enter 15,30,60,120,240,360,720,1440, otherwise crash

"whapi_group_id" : 
send to which group

"ai_prompt" : 
prompt for ai agent 


Also add client name to the client key:

Add API key and configure the global setting:

"hour_range":
 set the time range(hours) of the threads post time(if a post is posted on two hours ago, program will drop the post to ensure only scrap the most recent post.)

"interval":
scraping interval(minutes), how much time to wait for second scanning

"ai_model": 
follow the guide

"whapi_token" and "whapi_api_url":
follow the guide


2. Make sure that all file are in the right Hierarchy

3.At bash, go to the ltc directory

cmd:

python flow_control.py

Deploy at xampp

Download Xampp: https://www.apachefriends.org/

Put ltc directory into htdoc (explorer)

Open XAMPP Shell and run:

cd C:\xampp\htdocs\ltc 
python -m venv venv
venv\Scripts\activate 
pip install flask 
pip install -r C:\xampp\htdocs\ltc\requirements.txt 
playwright install --with-deps chromium
verify if playwright browser installed correctly:

python testp.py

expected output:
SUCCESS → Playwright OK on XAMPP!

Open XAMPP Shell and run:
bat
@echo off
cd /d "C:\xampp\htdocs\ltc"
call venv\Scripts\activate
python app.py
pause

Allow port 5000 in Windows Firewall
Run as Admin:
cmd
netsh advfirewall firewall add rule name="Flask 5000" dir=in action=allow protocol=TCP localport=5000


Find your PC’s local IP
at local computer bash:
ipconfig
look for your IPv4 address(something like 192.168.xx.xx)


Open from ANY device On phone / other PC, open browser: text
http://<your ip address>:5000
e.g. http://192.168.1.100:5000


*Only the device that connect with the same network can access your server


Deploy at Cloud(AWS EC2)
Directory Explanation

This repository includes the following directory - ltc (short for “Listening Tool Control”)

Directory Hierarchy

-ltc
	–static
		–style.css
–templates
	–panel.html
–result
	–{client}outputRecord.json
	–{client}AIOutput.txt
	–{client}PostListOutput.txt
	–finalOutput
	–AllClientFinalOutput
	–searchResult{1-10}.json
–app.py
–manifest.json
	–flow_control.py
	–threads_main.py
	–result_text_cleaning.py
–ai_agent.py
–sendWhatsapp.py
–testp.py
–requirements.txt

Main function brief of each file is shown in the following:

File name
Function
app.py
Building Panel web application with flask
control route function 
actually run the panel web
panel.html
Core web structure by HTML for the panel
including javascript to control render and button action
style.css
Style the front end of panel web application
manifest.json
Configure setting of the scraping program

 include:
client, keywordlist,message_interval,target_whatsapp_group…

scraping program read the manifest and run

*manifest contains API key of ai agent and whapi(sendWhatsapp), do not push this file directly to public repository.


flow_control.py
Main control of the scraping program, run this program to start entire scraping process(including call ai agent and send message)
threads_main.py
scrap web data from threads and store to searchResult{1-10}.json, called by flow_control.py
result_text_cleaning.py
read searchResult{1-10}.json and clean the raw data to be readable. Store cleaned data to {client}outputRecord.json. 
ai_agent.py
input data and call openroute ai agent, output ai analysis text
sendWhatsapp.py
input message body and send to target group(group id provided by whapi:https://whapi.readme.io/reference/getgroups)
requirements.txt
dependencies used in python program

in bash: 
pip install -r requirements.txt
to install all needed dependencies 
*guideline of installing playwright browser is introduced in deployment part. 
{client}outputRecord.json
	
cleaned data will store to this json, this json is client-base,each client owns one record. This file will delete outdated data(3 days ago) to prevent storage leak
finalOutput
this is a temporary storage of the final output of each scrap
AllClientFinalOutput
this is the final output that combine all client cleaned data from each scrap
searchResult{1-10}.json
this is the temporary storage to store scraping raw data
{client}AIOutput.txt
	
this is for debug and testing, to observe the input text for ai agent
{client}PostListOutput.txt
This is for debugging and testing, to observe the output text for sending messages.


External API service setup
	
AI agent : https://openrouter.ai/
Function: call ai model to process and analysis scraped data
1. Create Account/Login Account
2. Navigate to Account/Key/Create API Key
3. Enter a name of API key and save the key in a secure file
4. Paste the Model ID to the manifest.json/ai_agent_api_key
5. Navigate to Model and select a model that suit your need
6. Copy the Model ID
7. Paste the Model ID to the manifest.json/ai_model
8. You can amend AI prompt by rewrite the manifest.json/client_panel/ai_prompt

Whapi:https://panel.whapi.cloud/dashboard
Function: use request to call whapi to send whatsapp message to the target group
1. Create Account/Login Account
2. Navigate to dashboard
3. Navigate to your channel(register before, connect to your whatsapp account,scan QR code)
4. Copy your channel token
5. Paste channel token to the manifest.json/whapi_token
6. Copy API URL and paste to the manifest.json/whapi_api_url

Get Client group ID:https://whapi.readme.io/reference/getgroups
1. Copy your channel token and click "get"
2. Find your target group ID (something like : 1203000029491703@g.us)
3. Copy group ID and paste it to the manifest.json/client_panel/whapi_group_id

