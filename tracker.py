import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

# 🛒 PRODUCTS TO TRACK
PRODUCTS = [
    {
        "name": "iPhone 17 White",
        "url": "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
    {
        "name": "iPhone 16 Black",
        "url": "https://www.bigbasket.com/pd/40330602/apple-iphone-16-128gb-black-1-n/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
]

# 👥 TELEGRAM USERS
CHAT_IDS = [
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2"),
]

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 📍 PINCODES
PINCODE_LIST = ["122001", "122002", "122018", "122015"]

# ===========================================

# Anti-spam memory (per product + per pincode)
last_stock_state = {
    product["name"]: {pin: False for pin in PINCODE_LIST}
    for product in PRODUCTS
}


def send_telegram(message):
    """Send message to all users"""
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
    """Setup headless Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    return driver


def set_location(driver, pincode):
    """Set BigBasket pincode"""
    try:
        driver.get("https://www.bigbasket.com/")
        time.sleep(5)

        box = driver.find_element(
            "xpath", "//input[@placeholder='Enter your pincode']"
        )
        box.clear()
        box.send_keys(pincode)
        time.sleep(3)

        driver.find_element("xpath", "(//li)[1]").click()
        time.sleep(5)

        print(f"📍 Location set: {pincode}")

    except Exception as e:
        print(f"Location error ({pincode}):", e)


def check_stock_for_pincode(url, pincode):
    """Check stock for one product + one pincode"""
    driver = setup_driver()

    try:
        set_location(driver, pincode)
        driver.get(url)
        time.sleep(8)

        page_text = driver.page_source.lower()
        return "add to basket" in page_text

    finally:
        driver.quit()


# ================= MAIN =================

print("🚀 Multi-product tracker started...")

for product in PRODUCTS:
    print(f"\n🛒 Checking product: {product['name']}")

    for pin in PINCODE_LIST:
        print(f"🔍 Checking pincode: {pin}")

        try:
            in_stock = check_stock_for_pincode(product["url"], pin)

            # ✅ Anti-spam (within this run)
            if in_stock and not last_stock_state[product["name"]][pin]:
                msg = f"🟢 {product['name']} is IN STOCK at pincode {pin}!"
                print(msg)
                send_telegram(msg)

            last_stock_state[product["name"]][pin] = in_stock

        except Exception as e:
            print(f"Error checking {pin}:", e)
