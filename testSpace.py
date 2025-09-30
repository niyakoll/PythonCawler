if __name__ == "__main__":
    output = scrape_thread("https://www.threads.com/@cantalkpop/post/DPIcpLNAT-_")
    formatOutput = json.dumps(output, indent=4, ensure_ascii=False)
    #print(formatOutput)
    file_path = r"C:\Users\Alex\threadOutput2.json"
    

# Open the file in write mode ('w') and use json.dump() to write the data
try:
    with open(file_path, 'w',encoding="utf-8") as f:
        #json.dump(output, f, indent=4,ensure_ascii=False)  # indent for pretty-printing
        json.dump(output, f, indent=4,ensure_ascii=False) 
    print(f"JSON file successfully created at: {file_path}")
except IOError as e:
    print(f"Error creating JSON file at {file_path}: {e}")
#print(len(threadList))
#print(threadItemList)

