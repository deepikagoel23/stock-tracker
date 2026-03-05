import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

PRODUCTS = [
    {
        "name": "iPhone 17 White",
        "url": "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/",
    },
    {
        "name": "iPhone 16 Black",
        "url": "https://www.bigbasket.com/pd/40330602/apple-iphone-16-128gb-black-1-n/",
    },
    {
        "name": "iPhone 17 Black",
        "url": "https://www.bigbasket.com/pd/40356300/apple-iphone-17-256gb-black-1-unit/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
    {
        "name": "iPhone 17 mist blue",
        "url": "https://www.bigbasket.com/pd/40356302/apple-iphone-17-256gb-mist-blue-1-unit/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10"
    },
    {
        "name": "iPhone 16 ultramarine",
        "url": "https://www.bigbasket.com/pd/40330605/apple-iphone-16-128gb-ultramarine-1-n/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
    {
        "name": "iPhone 16 Teal",
        "url": "https://www.bigbasket.com/pd/40330606/apple-iphone-16-128gb-teal-1-n/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
]

CHAT_IDS = [
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2"),
]

BOT_TOKEN = os.getenv("BOT_TOKEN")

PINCODE_LIST = ["122001", "122002", "122018", "122015"]

# ===========================================


def send_telegram(message):
    """Send ONE combined message to all users"""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in CHAT_IDS:
        if not chat_id:
            continue
        try:
            requests.post(
                api_url,
                data={"chat_id": chat_id, "text": message},
                timeout=10,
            )
        except Exception as e:
            print("Telegram error:", e)


def setup_driver():
    """Fast headless Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.set_page_load_timeout(60)
    return driver


def set_location(driver, pincode):
    """Accurate BigBasket location setter"""
    try:
        driver.get("https://www.bigbasket.com/")

        wait = WebDriverWait(driver, 15)

        # 🔥 open location box
        location_box = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@placeholder='Enter your pincode']")
            )
        )

        location_box.clear()
        location_box.send_keys(pincode)

        # 🔥 wait for suggestion and click FIRST REAL match
        suggestion = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[contains(@class,'flex items-center')]")
            )
        )
        suggestion.click()

        # 🔥 wait until location applied
        time.sleep(4)

        print(f"📍 Location set correctly: {pincode}")
        return True

    except Exception as e:
        print(f"❌ Location failed ({pincode}):", e)
        return False


def check_stock(driver, url):
    """Accurate stock detection"""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # wait for page to stabilize
        time.sleep(4)

        page_text = driver.page_source.lower()

        # ✅ STRICT checks (prevents false positives)
        if "add to basket" in page_text:
            return True

        if "currently unavailable" in page_text:
            return False

        if "out of stock" in page_text:
            return False

        return False

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("🚀 FAST & ACCURATE TRACKER STARTED")

driver = setup_driver()
alerts = []

try:
    for pin in PINCODE_LIST:
        print(f"\n📍 Checking pincode: {pin}")

        if not set_location(driver, pin):
            continue

        for product in PRODUCTS:
            print(f"🔍 Checking {product['name']}")

            in_stock = check_stock(driver, product["url"])

            if in_stock:
                alerts.append(f"🟢 {product['name']} → {pin}")

finally:
    driver.quit()

# ================= ALERT =================

if alerts:
    message = "🔥 STOCK ALERT 🔥\n\n" + "\n".join(alerts)
    send_telegram(message)
    print("✅ Alert sent")
else:
    print("❌ Nothing in stock")
