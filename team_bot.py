# team_bot.py
# Stable Microsoft Teams Live Bot (2026)
# Designed for GitHub Actions / Linux Headless Chrome
# Search group by Search box instead of scrolling list

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
    "iX000s iSSale Boom&Task_1h TTS TAHK Foundation POSITIVE iShowOff/Top-iUp",
]


# =====================================================
# DRIVER
# =====================================================

def create_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    user_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_dir}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.set_page_load_timeout(60)
    return driver


# =====================================================
# HELPERS
# =====================================================

def screenshot(driver, name):
    try:
        driver.save_screenshot(name)
    except:
        pass


def safe_click(driver, element):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


# =====================================================
# LOGIN
# =====================================================

def login(driver):
    wait = WebDriverWait(driver, 30)

    try:
        print("🌐 Opening Teams Live...")
        driver.get("https://teams.live.com/v2/")

        # Sign in
        try:
            sign_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"Sign in")]')
                )
            )
            safe_click(driver, sign_btn)
        except:
            pass

        # Email
        email_box = wait.until(
            EC.presence_of_element_located((By.ID, "usernameEntry"))
        )
        email_box.clear()
        email_box.send_keys(EMAIL)
        email_box.send_keys(Keys.ENTER)

        time.sleep(3)

        # Use your password (if appears)
        try:
            use_pass = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[contains(text(),"Use your password")]')
                )
            )
            safe_click(driver, use_pass)
        except:
            pass

        # Password
        pass_box = wait.until(
            EC.presence_of_element_located((By.ID, "passwordEntry"))
        )
        pass_box.clear()
        pass_box.send_keys(PASSWORD)
        pass_box.send_keys(Keys.ENTER)

        time.sleep(5)

        # Stay signed in -> No
        try:
            no_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"No")]')
                )
            )
            safe_click(driver, no_btn)
        except:
            pass

        print("✅ Đăng nhập thành công")

        time.sleep(12)

        screenshot(driver, "01_after_login.png")
        return True

    except Exception as e:
        print("❌ Login failed:", e)
        traceback.print_exc()
        screenshot(driver, "login_error.png")
        return False


# =====================================================
# FIND SEARCH BOX
# =====================================================

def get_search_box(driver):
    wait = WebDriverWait(driver, 20)

    candidates = [
        '//input[contains(@placeholder,"Search")]',
        '//input[contains(@aria-label,"Search")]',
        '//input[@type="search"]',
        '//input[@type="text"]',
    ]

    for xp in candidates:
        try:
            return wait.until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
        except:
            continue

    raise Exception("Search box not found")


# =====================================================
# OPEN GROUP BY SEARCH
# =====================================================

def open_group(driver, group_name):
    try:
        print(f"🔎 Searching group: {group_name}")

        search = get_search_box(driver)

        search.click()
        time.sleep(1)

        # clear old text
        search.send_keys(Keys.CONTROL, "a")
        search.send_keys(Keys.DELETE)
        time.sleep(1)

        search.send_keys(group_name)
        time.sleep(4)

        # result selectors
        result_xpaths = [
            f'//*[contains(text(), "{group_name[:15]}")]',
            f'//*[contains(@title, "{group_name[:15]}")]',
            f'//*[contains(@aria-label, "{group_name[:15]}")]',
        ]

        clicked = False

        for xp in result_xpaths:
            try:
                result = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                safe_click(driver, result)
                clicked = True
                break
            except:
                continue

        if not clicked:
            raise Exception("No search result matched")

        print(f"📂 Opened group: {group_name}")
        time.sleep(5)
        screenshot(driver, "02_group_opened.png")
        return True

    except Exception as e:
        print(f"⚠️ Cannot open group '{group_name}': {e}")
        screenshot(driver, "search_fail.png")
        return False


# =====================================================
# SEND MESSAGE
# =====================================================

def send_message(driver):
    try:
        wait = WebDriverWait(driver, 20)

        msg_xpaths = [
            '//div[@contenteditable="true"]',
            '//textarea',
            '//*[@role="textbox"]',
        ]

        msg_box = None

        for xp in msg_xpaths:
            try:
                msg_box = wait.until(
                    EC.presence_of_element_located((By.XPATH, xp))
                )
                break
            except:
                continue

        if msg_box is None:
            raise Exception("Message box not found")

        msg_box.click()
        time.sleep(1)

        msg_box.send_keys(MESSAGE)
        time.sleep(1)
        msg_box.send_keys(Keys.ENTER)

        print("🚀 Message sent")
        time.sleep(3)

        screenshot(driver, "03_message_sent.png")
        return True

    except Exception as e:
        print("❌ Send failed:", e)
        screenshot(driver, "send_fail.png")
        return False


# =====================================================
# MAIN
# =====================================================

def main():
    if not EMAIL or not PASSWORD:
        print("❌ Missing TEAMS_EMAIL or TEAMS_PASSWORD secrets")
        return

    driver = create_driver()

    try:
        if not login(driver):
            return

        for group in GROUPS:
            print("\n================================")
            print("Processing:", group)

            if open_group(driver, group):
                send_message(driver)

        print("\n✅ Finished all groups")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
