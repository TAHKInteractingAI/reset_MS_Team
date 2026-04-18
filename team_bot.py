# team_bot.py
# Version 2.2 - Anti-Detection & Teams V2 UI Updated
import os
import time
import tempfile
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager

# =====================================================
# CONFIG
# =====================================================

EMAIL = os.environ.get("TEAMS_EMAIL", "tech.qtdata@gmail.com")
PASSWORD = os.environ.get("TEAMS_PASSWORD", "passnotE@1234")

MESSAGE = os.environ.get(
    "TEAMS_MESSAGE",
    "Thông báo: Reset 15min (Giải lao)"
)

GROUPS = [
    "BoomWTF..AiLàmViệcRiêng*ThựcNÃO*ProofFileNGAY",
    "iX000s iSSale Boom&Task_1h TTS AA POSITIVE iShowOff/Top-iUp",
    "iX000s iSSale Boom CMT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AU GlobalGroup.NỆN*iHugeNewRev*TiUp",
    "iX000s iSSale Boom QT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AH GlobalGroup.NỆN*iHugeNewRev*TiUp",
    "SAM Foundation TTSVol",
    "iX000s iSSale Boom&Task_1h TTS NB POSITIVE iShowOff/Top-iUp",
    "iX000s iSSale Boom&Task_1h TTS TAHK Foundation POSITIVE iShowOff/Top-iUp"
]

# =====================================================
# DRIVER SETUP
# =====================================================

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Giả lập User-Agent để tránh bị nhận diện là Bot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    user_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_dir}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(90)
    return driver

# =====================================================
# HELPERS
# =====================================================

def shot(driver, filename):
    try:
        driver.save_screenshot(filename)
    except:
        pass

def safe_click(driver, element):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)

# =====================================================
# LOGIN LOGIC
# =====================================================

def login(driver):
    wait = WebDriverWait(driver, 30)
    try:
        print("🌐 Opening Teams Live...")
        driver.get("https://teams.live.com/v2/")

        # Email
        email_box = wait.until(EC.presence_of_element_located((By.ID, "usernameEntry")))
        email_box.send_keys(EMAIL)
        email_box.send_keys(Keys.ENTER)
        time.sleep(3)

        # Password
        pass_box = wait.until(EC.presence_of_element_located((By.ID, "passwordEntry")))
        pass_box.send_keys(PASSWORD)
        pass_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # Skip "Stay signed in?"
        try:
            no_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(.,"No") or contains(.,"Không")]'))
            )
            safe_click(driver, no_btn)
        except:
            pass

        print("✅ Login process completed")
        return True
    except Exception as e:
        print("❌ Login failed:", e)
        shot(driver, "login_failed.png")
        return False

# =====================================================
# CORE ACTIONS
# =====================================================

def goto_chat_page(driver):
    try:
        print("📨 Navigating to Conversations...")
        driver.get("https://teams.live.com/v2/#/conversations")
        time.sleep(15) # Teams cần thời gian rất lâu để khởi tạo app v2
        
        # Dọn dẹp các popup hướng dẫn (Coachmarks) che màn hình
        try:
            popups = driver.find_elements(By.XPATH, '//button[contains(.,"Got it") or contains(.,"Dismiss") or contains(.,"Đã hiểu")]')
            for btn in popups:
                safe_click(driver, btn)
        except:
            pass
            
        shot(driver, "02_chat_page.png")
        return True
    except Exception as e:
        print("❌ Navigation error:", e)
        return False

def get_search_box(driver):
    wait = WebDriverWait(driver, 20)
    # Danh sách các Selector cập nhật cho Teams V2
    xpaths = [
        '//input[@data-tid="search-input-field"]',
        '//input[@id="search-query"]',
        '//input[contains(@placeholder, "Search") or contains(@placeholder, "Tìm kiếm")]',
        '//button[@aria-label="Search" or @aria-label="Tìm kiếm"]'
    ]

    for xp in xpaths:
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
            if el.is_displayed():
                # Nếu tìm thấy nút Search thay vì ô Input, bấm vào nút đó trước
                if el.tag_name == "button":
                    safe_click(driver, el)
                    time.sleep(2)
                    return get_search_box(driver) # Đệ quy lại để lấy ô input thực sự
                return el
        except:
            continue
    raise Exception("Search box UI not found")

def open_group(driver, group_name):
    try:
        print(f"🔎 Searching: {group_name}")
        search = get_search_box(driver)
        
        search.click()
        time.sleep(1)
        search.send_keys(Keys.CONTROL, "a")
        search.send_keys(Keys.DELETE)
        time.sleep(1)
        search.send_keys(group_name)
        time.sleep(6) # Đợi kết quả tìm kiếm render

        # Lấy từ khóa ngắn để tìm trong danh sách kết quả (Tránh lỗi ký tự đặc biệt)
        key_short = group_name[:10]
        result_xpaths = [
            f'//div[contains(@aria-label, "{key_short}")]',
            f'//span[contains(text(), "{key_short}")]',
            f'//div[@role="listitem"]//span[contains(., "{key_short}")]'
        ]

        for xp in result_xpaths:
            try:
                results = driver.find_elements(By.XPATH, xp)
                for res in results:
                    if res.is_displayed():
                        safe_click(driver, res)
                        print(f"📂 Group '{group_name}' selected")
                        time.sleep(4)
                        return True
            except:
                continue

        raise Exception("Result not found in list")
    except Exception as e:
        print(f"⚠️ Skip '{group_name}': {e}")
        shot(driver, f"failed_{group_name[:5]}.png")
        return False

def send_message(driver):
    wait = WebDriverWait(driver, 15)
    try:
        # Selector cho ô nhập liệu Teams V2 (thường là div contenteditable)
        selectors = [
            '//div[@contenteditable="true" and @role="textbox"]',
            '//div[@aria-label="Type a message" or @aria-label="Nhập tin nhắn"]',
            '//*[@role="textbox"]'
        ]

        msg_box = None
        for xp in selectors:
            try:
                msg_box = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
                if msg_box.is_displayed(): break
            except:
                pass

        if not msg_box: raise Exception("Input box not found")

        msg_box.click()
        time.sleep(1)
        msg_box.send_keys(MESSAGE)
        time.sleep(1)
        msg_box.send_keys(Keys.ENTER)

        print("🚀 Message sent successfully")
        time.sleep(2)
        return True
    except Exception as e:
        print("❌ Send error:", e)
        return False

# =====================================================
# MAIN EXECUTION
# =====================================================

def main():
    if not EMAIL or not PASSWORD:
        print("❌ Credentials missing in Environment Variables")
        return

    driver = create_driver()
    try:
        if not login(driver): return
        if not goto_chat_page(driver): return

        for group in GROUPS:
            print(f"\n--- Processing: {group} ---")
            if open_group(driver, group):
                send_message(driver)
            
            # Quay lại trang chủ chat để reset trạng thái tìm kiếm cho group sau
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

        print("\n✅ Task completed.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
