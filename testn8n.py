import json
import requests

# Your existing scraping code here...
# Assume 'data' is your scraped JSON as a Python dict, e.g.:
# data = {
#     "posts": [
#         {"title": "Post 1", "comments": ["Comment A"], "likes": 50, "replies": 10},
#         # ... more posts
#     ]
# }

# Or, if loading from a file:

def SendToN8n():

    with open('C:/Users/Alex/stressTest3.json', 'r',encoding='utf-8') as file1:
        data = json.load(file1)
        #print(data)
        #print(len(data))
        
        
            
        #print(data)
        print("successfully open json file!")
        
    webhook_url = 'https://chessmanit033.app.n8n.cloud/webhook-test/5a43edc9-9bb8-4f10-beb3-bcdd4b62e221'

# Optional: Add headers if your webhook requires authentication (e.g., API key)
    headers = {
        'Content-Type': 'application/json',
    # 'Authorization': 'Bearer your-api-key'  # Uncomment if needed
    }

# Send the POST request

    response = requests.post(webhook_url, headers=headers, json=data)
# n8n Webhook URL (get this from your n8n workflow)


# Check the response
    if response.status_code == 200:
        print("Data sent to n8n successfully!")
    else:
        print(f"Error sending data: {response.status_code} - {response.text}")

#SendToN8n()