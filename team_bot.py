from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import pytz
import os

# ====== Thông tin đăng nhập và cấu hình ======
# Khuyên dùng os.environ.get để bảo mật, hoặc điền trực tiếp nếu chạy local
email = os.environ.get('TEAMS_EMAIL') or "tech.qtdata@gmail.com"
password = os.environ.get('TEAMS_PASSWORD') or "passnotE@1234"
message_content = "Thông báo: Reset 15min (Giải lao)"
local_tz = pytz.timezone("Asia/Ho_Chi_Minh")

# Danh sách nhóm (Đã cập nhật các nhóm mới)
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

def login():
    import tempfile
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Chạy ẩn danh trên GitHub Actions
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_dir}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://teams.live.com/v2/")
    wait = WebDriverWait(driver, 25)

    try:
        # Bước 1: Click Sign in
        sign_in_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Sign in")]')))
        sign_in_btn.click()
        
        # Bước 2: Nhập Email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "usernameEntry")))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Bước 3: Xử lý nút 'Use your password' nếu có
        try:
            use_pass_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Use your password")]'))
            )
            use_pass_btn.click()
        except:
            pass

        # Bước 4: Nhập Password
        pass_input = wait.until(EC.presence_of_element_located((By.ID, "passwordEntry")))
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.RETURN)
        
        # Bước 5: Vượt qua các màn hình phụ (Stay signed in / No)
        try:
            no_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="secondaryButton"]'))
            )
            no_btn.click()
        except:
            pass

        print("✅ Đăng nhập thành công!")
        time.sleep(15) # Chờ danh sách chat tải hoàn toàn
        return driver
    except Exception as e:
        print(f"❌ Lỗi đăng nhập: {e}")
        driver.quit()
        return None

def open_chat_with_scroll(driver, chat_name):
    """Hàm tìm chat có hỗ trợ cuộn chuột nếu không thấy tên nhóm"""
    wait = WebDriverWait(driver, 15)
    try:
        # Thử tìm trực tiếp xem nhóm có hiện sẵn không
        try:
            xpath = f"//span[contains(normalize-space(), '{chat_name}')]"
            chat_element = driver.find_element(By.XPATH, xpath)
        except:
            print(f"🔄 Đang cuộn danh sách để tìm nhóm: {chat_name}")
            # Tìm vùng chứa danh sách chat để thực hiện scroll
            container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-tid="message-pane-list-runway"]')))
            
            found = False
            for _ in range(10): # Cuộn tối đa 10 lần
                driver.execute_script("arguments[0].scrollTop += 600;", container)
                time.sleep(1.5)
                try:
                    chat_element = driver.find_element(By.XPATH, xpath)
                    if chat_element.is_displayed():
                        found = True
                        break
                except:
                    continue
            
            if not found:
                raise Exception("Không tìm thấy tên nhóm sau khi cuộn")

        # Click vào nhóm
        driver.execute_script("arguments[0].scrollIntoView(true);", chat_element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", chat_element)
        print(f"📂 Đã mở nhóm: {chat_name}")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"⚠️ Không thể tìm thấy nhóm '{chat_name}': {e}")
        return False

def send_message(driver):
    try:
        # Tìm ô nhập tin nhắn
        msg_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
        )
        msg_box.send_keys(message_content)
        msg_box.send_keys(Keys.ENTER)
        print("🚀 Đã gửi tin nhắn thành công.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Lỗi khi gửi tin nhắn: {e}")

def job_wrapper():
    driver = login()
    if not driver:
        return

    for group in groups:
        print(f"\n--- Xử lý nhóm: {group} ---")
        if open_chat_with_scroll(driver, group):
            send_message(driver)
        
    print("\n✅ Hoàn tất tất cả các nhóm!")
    driver.quit()

if __name__ == "__main__":
    # Bạn có thể thêm logic kiểm tra giờ ở đây nếu chạy Cron 24/7
    # now = datetime.now(local_tz)
    # if (now.hour, now.minute) in [(9, 45), (15, 15)]:
    job_wrapper()
