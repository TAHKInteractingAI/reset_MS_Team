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

# ====== Thông tin đăng nhập và cấu hình ======
email = "tech.qtdata@gmail.com"
password = "passnotE@1234"
message = "Thông báo: Reset 15min (Giải lao)"
local_tz = pytz.timezone("Asia/Ho_Chi_Minh")

groups = [
    "BoomWTF..AiLàmViệcRiêng*ThựcNÃO*ProofFileNGAY",
    "iX000s iSSale Boom&Task_1h TTS AA POSITIVE iShowOff/Top-iUp",
    "iX000s iSSale Boom CMT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AU GlobalGroup.NỆN*iHugeNewRev*TiUp",
    "iX000s iSSale Boom QT*iHugeNewRev*Top-iUp",
    "iX000s iSSale AH GlobalGroup.NỆN*iHugeNewRev*TiUp"
]

import pickle
import os

# Thêm 2 hàm quản lý cookie
def save_cookies(driver, path="cookies.pkl"):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, path="cookies.pkl"):
    if os.path.exists(path):
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                # Selenium yêu cầu loại bỏ thuộc tính 'sameSite' nếu có giá trị None
                if "sameSite" in cookie and cookie["sameSite"] is None:
                    del cookie["sameSite"]
                driver.add_cookie(cookie)
        return True
    return False

def login():
    import tempfile
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_dir}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://teams.live.com/v2/")
    time.sleep(8)

    # Nếu chưa có cookie, login thủ công
    sign_in_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="button" and contains(., "Sign in")]'))
    )
    sign_in_btn.click()
    time.sleep(3)

    email_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "usernameEntry")))
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    time.sleep(8)

    # Lưu toàn bộ HTML của trang sau khi nhập email
    # with open("after_email.html", "w", encoding="utf-8") as f:
    #     f.write(driver.page_source)
    # print("Đã lưu HTML sau khi nhập email.")

    # Chọn 'Use your password' nếu xuất hiện
    try:
        use_pass_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@role="button" and contains(text(), "Use your password")]'))
        )
        use_pass_btn.click()
        time.sleep(3)
    except Exception as e:
        print("Không tìm thấy nút 'Use your password'.")

    # Tiếp tục nhập mật khẩu như cũ
    password_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "passwordEntry")))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(8)

    # driver.save_screenshot("after_email.png")
    # print("Đã chụp màn hình sau khi nhập email.")

    try:
        no_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="secondaryButton"]'))
        )
        no_button.click()
        time.sleep(5)
    except Exception as e:
        print("Không tìm thấy nút 'No'.")

    time.sleep(20)

    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="primaryButton"]'))
        )
        button.click()
        time.sleep(10)
    except:
        pass
    
    return driver


def open_chat(driver, chat_name):
    chat_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{chat_name}')]"))
    )
    driver.execute_script("arguments[0].click();", chat_element)
    time.sleep(5)

def send_message(driver):
    message_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
    )
    message_box.send_keys(message)
    message_box.send_keys(Keys.ENTER)
    time.sleep(2)

def job_wrapper():
    driver = login()
    for group in groups:
        open_chat(driver, group)
        send_message(driver)
    driver.quit()

# ====== Chạy nếu đúng giờ ======
if __name__ == "__main__":
    # now = datetime.now(local_tz)
    # if (now.hour, now.minute) in [(9, 45), (15, 15)]:
    job_wrapper()
