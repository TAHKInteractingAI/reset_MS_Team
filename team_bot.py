import os
import time
import pytz
import tempfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# ====== Cấu hình thông tin ======
email = os.environ.get('TEAMS_EMAIL')
password = os.environ.get('TEAMS_PASSWORD')
message_content = "Thông báo: Reset 15min (Giải lao)"
local_tz = pytz.timezone("Asia/Ho_Chi_Minh")

# Danh sách nhóm
groups = [
    "BoomWTF..AiLàmViệcRiêng*ThựcNÃO*ProofFileNGAY",
    "iX000s iSSale Boom&Task_1h TTS AA POSITIVE iShowOff/Top-iUp",
    "iX000s iSSale Boom CMT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AU GlobalGroup.NỆN*iHugeNewRev*TiUp",
    "iX000s iSSale Boom QT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AH GlobalGroup.NỆN*iHugeNewRev*TiUp",
    "SAM Foundation TTSVol",
    "iX000s iSSale Boom&Task_1h TTS NB POSITIVE iShowOff/Top-iUp",
    "iX000s iSSale Boom&Task_1h TTS TAHK Foundation POSITIVE iShowOff/Top-iUp",
]
def get_driver():
    options = uc.ChromeOptions()
    
    # 1. Cấu hình cơ bản cho môi trường Headless (GitHub Actions)
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    
    # 2. [TĂNG TỐC] Chiến lược load trang
    # 'eager' giúp trình duyệt không chờ đợi tải xong ảnh hay script bên thứ 3
    options.page_load_strategy = 'eager'
    
    # 3. [TĂNG TỐC] Chặn tải hình ảnh, CSS và Fonts để tiết kiệm băng thông và RAM
    # prefs = {
    #     "profile.managed_default_content_settings.images": 2,
    #     "profile.managed_default_content_settings.stylesheets": 2,
    #     "profile.managed_default_content_settings.fonts": 2
    # }
    # options.add_experimental_option("prefs", prefs)
    
    # 4. Ép trình duyệt dùng tiếng Anh
    options.add_argument('--lang=en-GB')
    
    # 5. [CHỐNG PHÁT HIỆN] Thêm Proxy dân cư (Khuyến nghị)
    # Trên GitHub Actions, hãy set secrets.PROXY_URL (ví dụ: http://user:pass@ip:port)
    proxy_url = os.getenv("PROXY_URL")
    if proxy_url:
        options.add_argument(f'--proxy-server={proxy_url}')
    
    # Khởi tạo undetected_chromedriver (Không dùng webdriver.Chrome thông thường)
    driver = uc.Chrome(options=options)
    
    # 6. [CHỐNG PHÁT HIỆN] Bơm thêm Stealth Script qua CDP
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Ẩn webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Fake runtime của Chrome (Bot thường không có cái này)
            window.navigator.chrome = { runtime: {} };
            
            // Bơm thêm plugins giả
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Ép ngôn ngữ
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-GB', 'en-US', 'en']
            });
        """
    })
    
    return driver

    
def login():
    driver = get_driver()
    # options = webdriver.ChromeOptions()
    # #options.add_argument("--headless")  
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--window-size=1920,1080")
    # # Giả lập User-Agent để tránh bị phát hiện là bot
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # temp_dir = tempfile.mkdtemp()
    # options.add_argument(f"--user-data-dir={temp_dir}")

    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Nếu tài khoản công ty, hãy đổi sang https://teams.microsoft.com/v2/
    driver.get("https://teams.live.com/v2/")
    
    wait = WebDriverWait(driver, 30)

    try:
        print("⏳ Đang tiến hành đăng nhập...")
        # Bước 1: Click Sign in
        sign_in_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Sign in")]')))
        sign_in_btn.click()
        
        # Bước 2: Nhập Email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "usernameEntry")))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Bước 3: Xử lý nút 'Use your password' nếu xuất hiện
        try:
            use_pass_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Use your password")]'))
            )
            use_pass_btn.click()
        except:
            pass

        # Bước 4: Nhập Password
        pass_input = wait.until(EC.presence_of_element_located((By.ID, "passwordEntry")))
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        
        # aria-describedby="signIn-title singIn-subtitle"
        # /html/body/div[1]/div/div/div/div[5]/div/div[3]/div/div[1]/div/div/div[1]/div/button[1]
        
        # Bước 5: Vượt qua màn hình 'Stay signed in'
        try:
            no_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="secondaryButton"]'))
            )
            no_btn.click()
        except:
            pass

        print("✅ Đăng nhập thành công!")
        # Đợi giao diện Teams tải xong hoàn toàn
        time.sleep(12) 
        try:
            print("Phát hiện trang bắt Sign in tiếp theo")
            driver.find_element(By.XPATH, '//button[contains(., "Sign in") or contains(@aria-describedby, "signIn-title singIn-subtitle")]').click()
            print("Đã ấn nút Sign in")
            time.sleep(10)
            print("Bắt đầu ấn nút Retry")
            actions = webdriver.ActionChains(driver)
            actions.move_by_offset(500, 500).click().perform()  # Click vào vị trí gần giữa
            actions.send_keys(Keys.TAB).perform()
            time.sleep(1)
            actions.send_keys(Keys.ENTER).perform()
            print("Đã ấn nút Retry")
            time.sleep(20)
        except Exception as e:
            print(f"Không tìm thấy nút đặc thù: {e}")
        return driver
    except Exception as e:
        driver.save_screenshot("error_login.png")
        print(f"❌ Lỗi đăng nhập: {e}")
        driver.quit()
        return None

def open_chat_by_search(driver, chat_name):
    """Sử dụng thanh tìm kiếm để tìm nhóm - Ổn định nhất cho Teams V2"""
    wait = WebDriverWait(driver, 20)
    try:
        # Tìm ô Search của Teams (Hỗ trợ nhiều loại selector)
        search_xpath = '//input[@placeholder="Search"] | //input[@aria-label="Search"] | //input[@id="ms-searchux-input"]'
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
        print("Tìm thấy nút searchbar")
        # Xóa và nhập tên nhóm
        search_input.click()
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(chat_name)
        print("Nhập thành công")
        time.sleep(3)
        #search_input.send_keys(Keys.ENTER)
        #time.sleep(4)

        # Click vào kết quả khớp tên nhóm trong danh sách kết quả
        # result_xpath = f"//span[contains(normalize-space(), '{chat_name}')]"
        # result_element = wait.until(EC.element_to_be_clickable((By.XPATH, result_xpath)))
        # result_element.click()
        action = webdriver.ActionChains(driver)
        action.send_keys(Keys.ARROW_DOWN).perform()
        time.sleep(1)
        action.send_keys(Keys.ENTER).perform()
        print(f"📂 Đã tìm thấy và mở nhóm: {chat_name}")
        time.sleep(5)
        return True
    except Exception as e:
        driver.save_screenshot(f"error_find_{chat_name[:10]}.png")
        print(f"⚠️ Không thể tìm thấy nhóm '{chat_name}': {e}")
        return False

def send_message(driver):
    """Gửi tin nhắn vào ô chat hiện tại"""
    wait = WebDriverWait(driver, 20)
    try:
        # Selector cho ô nhập liệu Teams V2 mới
        msg_box_xpath = '//div[@role="textbox"] | //div[@contenteditable="true"][@aria-label="Type a message"]'
        msg_box = wait.until(EC.presence_of_element_located((By.XPATH, msg_box_xpath)))
        
        msg_box.click()
        time.sleep(1)
        msg_box.send_keys(f"Testing: {message_content}")
        msg_box.send_keys(Keys.ENTER)
        
        print("🚀 Đã gửi tin nhắn thành công.")
        time.sleep(2)
    except Exception as e:
        driver.save_screenshot("error_send_msg.png")
        print(f"❌ Lỗi khi gửi tin nhắn: {e}")

def job_wrapper():
    driver = login()
    if not driver:
        print("🛑 Không thể khởi động trình duyệt hoặc đăng nhập thất bại.")
        return

    for group in groups:
        print(f"\n--- Đang xử lý nhóm: {group} ---")
        # Thay thế hàm scroll cũ bằng hàm search mới
        if open_chat_by_search(driver, group):
            send_message(driver)
        time.sleep(5)
            
    print("\n✨ Hoàn tất nhiệm vụ cho tất cả các nhóm!")
    driver.quit()

if __name__ == "__main__":
    # Tự động thực thi khi chạy script
    job_wrapper()
