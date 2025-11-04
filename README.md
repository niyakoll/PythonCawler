```markdown
# Listening Tool For Threads

This repository integrates a **Python scraping tool for Threads** and a **simple web application panel** using **Flask**. The instructions below explain the function of each file and how to deploy it in **local**, **XAMPP**, and **cloud (AWS EC2)** environments.

---

## Prerequisite

This is a **Python-based program**. Make sure you have **Python installed**.

### Install Python on Windows (via installer)
```bash
.\python-3.11.0-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
```

### Verify Installation
```bash
python --version
```

---

## Content

1. [Deploy at Local](#deploy-at-local)  
2. [Deploy at XAMPP](#deploy-at-xampp)  
3. [Deploy at Cloud (AWS EC2)](#deploy-at-cloud-aws-ec2)  
4. [Directory Explanation](#directory-explanation)  
5. [External API Service Setup](#external-api-service-setup)

---

## Deploy at Local

### 1. Install Dependencies
```bash
cd ltc
pip install -r requirements.txt
```

> **Note**: Playwright browser installation is covered in the [XAMPP section](#deploy-at-xampp).

---

### 2. Manually Configure `manifest.json`

Follow the format under `client_panel`:

| Field | Description |
|------|-------------|
| `target_whatsapp_group` | Can be empty |
| `whapi_group_id` | See [Whapi guide](#whapi-setup) |
| `run` | Set `true` to run this client |
| `message_interval` | Interval (minutes) to **receive** messages: **only** `15, 30, 60, 120, 240, 360, 720, 1440` (others will crash) |
| `whapi_group_id` | Group to send messages |
| `ai_prompt` | Prompt for AI agent |

Also add the client name to the `client` key:

```json
"client": ["Client A", "Client B"]
```

---

### 3. Configure Global Settings in `manifest.json`

| Field | Description |
|------|-------------|
| `hour_range` | Time range (hours) for post age (e.g., drop posts older than 2 hours) |
| `interval` | Scraping interval in **minutes** |
| `ai_model` | Follow [OpenRouter guide](#ai-agent-setup) |
| `whapi_token` | From [Whapi dashboard](#whapi-setup) |
| `whapi_api_url` | Usually `https://gate.whapi.cloud/` |

---

### 4. Ensure Correct File Hierarchy

```
ltc/
├── app.py
├── manifest.json
├── flow_control.py
└── ...
```

---

### 5. Run the Scraper
```bash
python flow_control.py
```

---

## Deploy at XAMPP

### 1. Download XAMPP
[https://www.apachefriends.org/](https://www.apachefriends.org/)

### 2. Place `ltc` Folder
```
C:\xampp\htdocs\ltc
```

### 3. Open **XAMPP Shell** and Run:
```bash
cd C:\xampp\htdocs\ltc
python -m venv venv
venv\Scripts\activate
pip install flask
pip install -r C:\xampp\htdocs\ltc\requirements.txt
playwright install --with-deps chromium
```

### 4. Verify Playwright
```bash
python testp.py
```
**Expected Output**:
```
SUCCESS → Playwright OK on XAMPP!
```

---

### 5. Create `run.bat` (Auto-start Script)
```bat
@echo off
cd /d "C:\xampp\htdocs\ltc"
call venv\Scripts\activate
python app.py
pause
```

Double-click `run.bat` to start the web panel.

---

### 6. Allow Port 5000 in Windows Firewall
Run as **Admin**:
```cmd
netsh advfirewall firewall add rule name="Flask 5000" dir=in action=allow protocol=TCP localport=5000
```

---

### 7. Find Your Local IP
```bash
ipconfig
```
Look for **IPv4 Address** (e.g., `192.168.1.100`)

---

### 8. Access from Any Device (Same Network)
Open browser on phone or another PC:
```
http://192.168.1.100:5000
```

> Only devices on the **same network** can access.

---

## Deploy at Cloud (AWS EC2)

> See [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md) for full steps (coming soon).

---

## Directory Explanation

```
ltc/
├── static/
│   └── style.css                 # Frontend styling
├── templates/
│   └── panel.html                # Main web UI
├── result/
│   ├── {client}outputRecord.json # Cleaned scraped data
│   ├── {client}AIOutput.txt      # AI input debug
│   ├── {client}PostListOutput.txt# Message output debug
│   ├── finalOutput/              # Temp per-scrape output
│   ├── AllClientFinalOutput/     # Combined final output
│   └── searchResult{1-10}.json   # Raw scraped data
├── app.py                        # Flask web panel
├── manifest.json                 # Configuration (DO NOT commit API keys)
├── flow_control.py               # Main scraper controller
├── threads_main.py               # Scrapes Threads → searchResult*.json
├── result_text_cleaning.py       # Cleans raw data → readable format
├── ai_agent.py                   # Calls OpenRouter AI
├── sendWhatsapp.py               # Sends message via Whapi
├── testp.py                      # Playwright test
└── requirements.txt              # Python dependencies
```

---

### File Functions Summary

| File | Function |
|------|---------|
| `app.py` | Builds Flask panel, handles routes |
| `panel.html` | Core HTML + JS for UI |
| `style.css` | Styles the panel |
| `manifest.json` | Config: clients, keywords, intervals, API keys |
| `flow_control.py` | Orchestrates scraping, AI, WhatsApp |
| `threads_main.py` | Scrapes Threads → raw JSON |
| `result_text_cleaning.py` | Cleans raw data → readable format |
| `ai_agent.py` | Sends data to OpenRouter AI |
| `sendWhatsapp.py` | Sends final message via Whapi |
| `requirements.txt` | All Python dependencies |

> **Warning**: `{client}outputRecord.json` auto-deletes data older than **3 days**.

---

## External API Service Setup

### AI Agent: [OpenRouter](https://openrouter.ai/)

1. Create/Login account
2. Go to **Account → Keys → Create API Key**
3. Save key → paste in `manifest.json` → `ai_agent_api_key`
4. Choose model → copy **Model ID**
5. Paste in `manifest.json` → `ai_model`
6. Edit `ai_prompt` in `client_panel` as needed

---

### Whapi: [https://panel.whapi.cloud](https://panel.whapi.cloud)

1. Create/Login account
2. Go to **Dashboard → Your Channel**
3. Connect WhatsApp (scan QR)
4. Copy **Channel Token** → `manifest.json` → `whapi_token`
5. Copy **API URL** → `manifest.json` → `whapi_api_url` (usually `https://gate.whapi.cloud/`)

---

### Get Group ID: [Whapi Docs](https://whapi.readme.io/reference/getgroups)

1. Use your token → click **"Get Groups"**
2. Find target group → copy ID (e.g., `1203000029491703@g.us`)
3. Paste in `manifest.json` → `client_panel` → `whapi_group_id`

---

## Security Note

> **Never commit `manifest.json`** with API keys to public GitHub.

Use `.gitignore`:
```gitignore
manifest.json
*.pem
.env
```

---

## Screenshots

![Panel UI](image1.png)
![Edit Modal](image2.png)
![Whapi Groups](image3.png)

---

## License

MIT
```
```
