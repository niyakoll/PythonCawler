import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_lihkg_2025(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="zh-HK",
            timezone_id="Asia/Hong_Kong",
            java_script_enabled=True,
            bypass_csp=True,
            # 關鍵！模擬真實香港用戶
            geolocation={"longitude": 114.1694, "latitude": 22.3193},
            permissions=["geolocation"],
        )

        # 超級反偵測（必加！）
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-HK', 'zh', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {}, app: {}, webstore: {} };
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        """)

        page = await context.new_page()

        # 關鍵！攔截並抓出真正的 API 請求（這才是 2025 年王道）
        actual_data = None

        async def intercept_response(response):
            nonlocal actual_data
            if "api_v2/thread" in response.url and response.status == 200:
                try:
                    json_data = await response.json()
                    if json_data.get("success") and json_data["response"].get("items"):
                        actual_data = json_data
                        print(f"成功攔截 API！抓到 {len(json_data['response']['items'])} 篇")
                except:
                    pass

        page.on("response", intercept_response)

        print(f"正在抓取：{url}")
        await page.goto(url, wait_until="networkidle", timeout=120_000)

        # 等個幾秒讓 API 請求發出去
        await asyncio.sleep(8)

        await browser.close()
        return actual_data

# 測試
async def main():
    result = await scrape_lihkg_2025("https://lihkg.com/thread/4026502/page/1")
    if result:
        print(result)
        print("成功！")
        #print("標題：", result["response"]["thread"]["title"])
        #print("總回覆數：", len(result["response"]["items"]))
        with open("lihkg_success.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print("失敗")

asyncio.run(main())