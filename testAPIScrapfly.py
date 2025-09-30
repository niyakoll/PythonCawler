from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse

# Replace 'YOUR_API_KEY' with your actual Scrapfly API key
client = ScrapflyClient(key="YOUR_API_KEY")

# Configure the scrape request
api_response: ScrapeApiResponse = client.scrape(
    ScrapeConfig(
        # Add the URL of the Threads.net post you want to scrape
        url='https://www.threads.net/@instagram/post/C0-UZnOsiPW/', # Example URL, replace with a real Threads.net URL
        # Enable bypass anti-scraping protection if necessary
        asp=True,
        # Enable headless browser if the content is rendered by JavaScript
        render_js=True,
        # Use AI to extract social media post data
        extraction_model='social_media_post'
    )
)

# Use AI extracted data
if api_response.scrape_result and 'extracted_data' in api_response.scrape_result:
    thread_data = api_response.scrape_result['extracted_data']['data']
    print("Extracted Thread Data:")
    print(thread_data)
else:
    print("No extracted data found.")

# Or parse the HTML yourself if you prefer
if api_response.scrape_result and 'content' in api_response.scrape_result:
    html_content = api_response.scrape_result.content
    print("
Raw HTML Content:")
    print(html_content[:500]) # Print first 500 characters of HTML for brevity
