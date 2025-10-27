import json
import os
############################Change Setting###############################
manifest = {}
path = str(os.path.join(os.path.dirname(__file__),"manifest.json"))
with open(path, 'r',encoding="utf-8") as file:
    manifest = json.load(file)
    client = manifest["client_panel"]["親愛的BOB"]
    client["run"] = True
with open(path, 'w',encoding="utf-8") as file:
    json.dump(manifest, file, indent=4,ensure_ascii=False)