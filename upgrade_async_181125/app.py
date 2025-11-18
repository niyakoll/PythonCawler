# app.py
from flask import Flask, render_template, request, jsonify
import json, os, shutil, datetime

app = Flask(__name__)
CONFIG = "manifest.json"
BACKUP = "backups"
os.makedirs(BACKUP, exist_ok=True)

def load():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)

def save(cfg):
    # backup
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(CONFIG, f"{BACKUP}/manifest_{ts}.json")
    # write
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

# ---------- Pages ----------
@app.route("/")
def index():
    return render_template("panel.html", cfg=load())

# ---------- API ----------
@app.route("/api/config")
def api_config():
    return jsonify(load())

# update a client (create if missing)
@app.route("/api/client", methods=["POST"])
def api_client():
    data = request.json
    cfg = load()
    name = data["name"].strip()
    initalclientRecordJson = {}
    # create entry if new
    if name not in cfg["client_panel"]:
        cfg["client"].append(name)
        cfg["client_panel"][name] = {
            "threads_run": False,
            "ig_run":False,
            "fb_run":False,
            "keyword": [],
            "message_interval": 15,
            "target_whatsapp_group": "",
            "quiet_mode":False,
            "whapi_group_id": "",
            "ai_prompt": cfg["ai_prompt"]
        }
        try:
            with open(str(os.path.join(os.path.dirname(__file__),"result",f"{name}outputRecord.json")), 'w',encoding="utf-8") as file:
                json.dump(initalclientRecordJson, file, indent=4,ensure_ascii=False)  # indent for pretty-printing
                print("Client threads record json initalised.")
        except Exception as e:
                print(e)

    panel = cfg["client_panel"][name]
    panel["threads_run"]                = data.get("threads_run", panel["threads_run"])
    panel["ig_run"]                = data.get("ig_run", panel["ig_run"])
    panel["fb_run"]                = data.get("fb_run", panel["fb_run"])
    
    if "keyword" in data:
        panel["keyword"] = [k.strip() for k in data["keyword"].split(",") if k.strip()]
    else:
        panel["keyword"] = panel["keyword"]  # unchanged
    panel["message_interval"]   = int(data.get("message_interval", panel["message_interval"]))
    panel["target_whatsapp_group"] = data.get("target_whatsapp_group", panel["target_whatsapp_group"])
    panel["quiet_mode"]                = data.get("quiet_mode", panel["quiet_mode"])
    panel["whapi_group_id"]     = data.get("whapi_group_id", panel["whapi_group_id"])
    panel["ai_prompt"]          = data.get("ai_prompt", panel["ai_prompt"])
    
    save(cfg)
    return jsonify({"status":"ok"})

# delete client
@app.route("/api/client/<name>", methods=["DELETE"])
def api_del(name):
    cfg = load()
    if name in cfg["client_panel"]:
        cfg["client_panel"].pop(name)
        cfg["client"] = [c for c in cfg["client"] if c != name]
        save(cfg)
    return jsonify({"status":"ok"})

# global settings (only the fields you asked for)
@app.route("/api/global", methods=["POST"])
def api_global():
    data = request.json
    cfg = load()
    cfg["hour_range"] = int(data["hour_range"])
    cfg["interval"]   = int(data["interval"])
    cfg["ai_model"]   = data["ai_model"]      # keep as list
    save(cfg)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)