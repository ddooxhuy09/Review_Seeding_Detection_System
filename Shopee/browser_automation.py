import asyncio
from undetected_playwright.async_api import async_playwright, Playwright

async def open_url_with_playwright(url):
    """Hàm mở URL bằng Undetected Playwright"""
    try:
        async with async_playwright() as p:
            # Khởi tạo trình duyệt Chromium với các options để tránh detection
            browser = await p.chromium.launch(
                headless=False,  # Để thấy trình duyệt
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Tạo context với các cài đặt để tránh detection
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='vi-VN',
                timezone_id='Asia/Ho_Chi_Minh'
            )
            
            page = await context.new_page()
            
            # Thêm script để ẩn webdriver (undetected_playwright tự động handle nhiều thứ rồi)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['vi-VN', 'vi', 'en-US', 'en'],
                });
            """)

            # Mở URL
            print(f"🌐 Đang mở URL: {url}")
            await page.goto(url, wait_until='networkidle')

            # Lấy tiêu đề trang
            title = await page.title()
            print(f"📄 Tiêu đề trang: {title}")
            
            # Chờ một chút để trang load hoàn toàn
            await asyncio.sleep(3)
            
            # Kiểm tra xem có phải trang Shopee không
            if 'shopee' in url.lower():
                print("🛒 Phát hiện trang Shopee, đang xử lý...")
                
                # Có thể thêm logic xử lý đặc biệt cho Shopee ở đây
                try:
                    # Chờ trang load
                    await page.wait_for_load_state('networkidle', timeout=10000)
                    
                    # Scroll xuống một chút để trigger lazy loading
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight/4)")
                    await asyncio.sleep(2)
                    
                except Exception as scroll_error:
                    print(f"⚠️ Không thể scroll: {scroll_error}")
            
            # Giữ trang mở trong 60 giây để người dùng có thể xem
            print("⏰ Giữ trang mở trong 60 giây...")
            await asyncio.sleep(60)

            # Đóng trình duyệt
            await browser.close()
            
            return {"success": True, "title": title, "url": url}
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Lỗi khi mở URL: {error_msg}")
        return {"success": False, "error": error_msg, "url": url}

def run_browser_automation(url):
    """Hàm wrapper để chạy automation từ bên ngoài"""
    try:
        return asyncio.run(open_url_with_playwright(url))
    except Exception as e:
        print(f"❌ Lỗi trong run_browser_automation: {str(e)}")
        return {"success": False, "error": str(e), "url": url}

async def main():
    """Hàm main để test trực tiếp"""
    print("🚀 Khởi động Undetected Playwright Browser Automation")
    url = input("📝 Nhập URL: ")
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        print(f"🔧 Đã thêm https:// vào URL: {url}")
    
    result = await open_url_with_playwright(url)
    print(f"📊 Kết quả: {result}")

# Chỉ chạy khi file được gọi trực tiếp
if __name__ == "__main__":
    asyncio.run(main())