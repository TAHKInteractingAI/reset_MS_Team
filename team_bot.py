# team_bot.py
# Version 2.1 (GitHub Actions Stable / Syntax Checked)
# Microsoft Teams Live Auto Sender

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

def shot(driver, filename):
    try:
        driver.save_screenshot(filename)
    except:
        pass


def safe_click(driver, element):
    try:
        element.click()
    except:
        try:
            driver.execute_script("arguments[0].click();", element)
        except:
            pass


# =====================================================
# LOGIN
# =====================================================

def login(driver):
    wait = WebDriverWait(driver, 30)

    try:
        print("🌐 Opening Teams Live...")
        driver.get("https://teams.live.com/v2/")

        # Sign in button
        try:
            btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"Sign in")]')
                )
            )
            safe_click(driver, btn)
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

        # Use password if appears
        try:
            use_pass = WebDriverWait(driver, 6).until(
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

        # Stay signed in => No
        try:
            no_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(.,"No")]')
                )
            )
            safe_click(driver, no_btn)
        except:
            pass

        print("✅ Login success")
        time.sleep(10)

        shot(driver, "01_login_success.png")
        return True

    except Exception as e:
        print("❌ Login failed:", e)
        traceback.print_exc()
        shot(driver, "login_failed.png")
        return False


# =====================================================
# GO TO CHAT PAGE
# =====================================================

def goto_chat_page(driver):
    try:
        print("📨 Opening conversations page...")
        driver.get("https://teams.live.com/v2/#/conversations")
        time.sleep(10)
        shot(driver, "02_chat_page.png")
        return True
    except Exception as e:
        print("❌ Cannot open chat page:", e)
        return False


# =====================================================
# FIND SEARCH BOX
# =====================================================

def get_search_box(driver):
    wait = WebDriverWait(driver, 20)

    xpaths = [
        '//input[contains(@placeholder,"Search")]',
        '//input[contains(@aria-label,"Search")]',
        '//input[contains(@placeholder,"Find")]',
        '//input[@type="search"]',
        '//input[@type="text"]',
        '//textarea'
    ]

    for xp in xpaths:
        try:
            el = wait.until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
            if el.is_displayed():
                return el
        except:
            pass

    raise Exception("Search box not found")


# =====================================================
# OPEN GROUP
# =====================================================

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
        time.sleep(5)

        key = group_name[:12]

        result_xpaths = [
            f'//*[contains(text(), "{key}")]',
            f'//*[contains(@title, "{key}")]',
            f'//*[contains(@aria-label, "{key}")]'
        ]

        for xp in result_xpaths:
            try:
                result = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                safe_click(driver, result)
                print("📂 Group opened")
                time.sleep(5)
                shot(driver, "03_group_opened.png")
                return True
            except:
                pass

        raise Exception("No matching search result")

    except Exception as e:
        print(f"⚠️ Cannot open group '{group_name}': {e}")
        shot(driver, "group_failed.png")
        return False


# =====================================================
# SEND MESSAGE
# =====================================================

def send_message(driver):
    wait = WebDriverWait(driver, 20)

    try:
        selectors = [
            '//div[@contenteditable="true"]',
            '//*[@role="textbox"]',
            '//textarea'
        ]

        msg_box = None

        for xp in selectors:
            try:
                msg_box = wait.until(
                    EC.presence_of_element_located((By.XPATH, xp))
                )
                break
            except:
                pass

        if msg_box is None:
            raise Exception("Message box not found")

        msg_box.click()
        time.sleep(1)

        msg_box.send_keys(MESSAGE)
        time.sleep(1)
        msg_box.send_keys(Keys.ENTER)

        print("🚀 Message sent")
        shot(driver, "04_sent.png")
        time.sleep(3)

        return True

    except Exception as e:
        print("❌ Send failed:", e)
        shot(driver, "send_failed.png")
        return False


# =====================================================
# MAIN
# =====================================================

def main():
    if not EMAIL or not PASSWORD:
        print("❌ Missing TEAMS_EMAIL or TEAMS_PASSWORD")
        return

    driver = create_driver()

    try:
        if not login(driver):
            return

        if not goto_chat_page(driver):
            return

        for group in GROUPS:
            print("\n================================")

            if open_group(driver, group):
                send_message(driver)

        print("\n✅ Finished all groups")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
