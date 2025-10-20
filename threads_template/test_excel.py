import time
import json
import pandas as pd
import os
import openpyxl
from openpyxl import load_workbook, Workbook
from pathlib import Path
currentPath = os.path.dirname(os.path.abspath(__file__))
outPutPath = Path(currentPath+"/result")
#print(currentPath)
############################## Write Data to Excel #################################
combined_data = {
    "ID":[],
    "text":[],
    "likeCount":[],
    "replyCount":[],
    "link":[],
    "datetime":[],
    "recordTime":[],
    "POR":[]
    
}

post = {
    "ID":"12345678",
    "text":"張敬軒",
    "likeCount":20,
    "replyCount":12,
    "link":"threads.com",
    "datetime":"10-14-2025 09:12:23 HKT",
    "recordTime":"10-14-2025 10:24:23 HKT",
    "POR":True
}
replies ={
    "ID":"3747507342763244724_68163591691",
    "text":"好好聽",
    "likeCount":3,
    "replyCount":1,
    "link":"https://www.threads.net/@vickykwk_kk/post/DQB0hK2kjy0",
    "datetime":"10-14-2025 10:12:23 HKT",
    "recordTime":"10-14-2025 10:24:23 HKT",
    "POR":False
}

combined_data["ID"].append(post["ID"])
combined_data["text"].append(post["text"])
combined_data["likeCount"].append(post["likeCount"])
combined_data["replyCount"].append(post["replyCount"])
combined_data["link"].append(post["link"])
combined_data["datetime"].append(post["datetime"])
combined_data["recordTime"].append(post["recordTime"])
combined_data["POR"].append(post["POR"])

def createExcel():
    df = pd.DataFrame(combined_data)

    with pd.ExcelWriter(outPutPath+"exampleData.xlsx", engine = "openpyxl") as writer:
        df.to_excel(writer, sheet_name="ThreadData",index=False)

############################## Update Data to Excel #################################
sheet_name = "ThreadData"
filename = "exampleData.xlsx"

def UpdateExcel():
    if outPutPath.exists("exampleData.xlsx"):
        workbook = load_workbook("exampleData.xlsx")
    else:
        workbook = Workbook()
        # Remove default sheet if created
        if "Sheet" in workbook.sheetnames:
            workbook.remove(workbook["ThreadData"])

    # Create or get sheet
    if sheet_name not in workbook.sheetnames:
        sheet = workbook.create_sheet(sheet_name)
        # Add headers
        sheet.append(["ID", "text", "likeCount","replyCount","link","datetime","recordTime","POR"])
    else:
        sheet = workbook[sheet_name]

    # Append data
    
        row = [
            replies["ID"],
            replies["text"]
        ]
        sheet.append(row)
    # Save workbook
    workbook.save(filename)
    print(f"Data appended to {filename}, sheet: {sheet_name}")

#with open(currentPath+"/result/searchResult10.json","r",encoding="utf-8") as f:
#data = json.loads(replies,ensure_ascii=False)
UpdateExcel()
############################## Read Data to Excel #################################