import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

PRODUCTS = [
    {
        "name": "iPhone 17 White",
        "url": "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
    },
    {
        "name": "iPhone 16 Black",
        "url": "https://www.bigbasket.com/pd/40330602/apple-iphone-16-128gb-black-1-n/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10",
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
    try:
        driver.get("https://www.bigbasket.com/")
        time.sleep(5)

        box = driver.find_element(
            "xpath", "//input[@placeholder='Enter your pincode']"
        )
        box.clear()
        box.send_keys(pincode)
        time.sleep(2)

        driver.find_element("xpath", "(//li)[1]").click()
        time.sleep(4)

        print(f"📍 Location set: {pincode}")

    except Exception as e:
        print(f"Location error ({pincode}):", e)


def check_stock(driver, url):
    try:
        driver.get(url)
        time.sleep(5)

        page_text = driver.page_source.lower()
        return "add to basket" in page_text

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("🚀 Optimized multi-product tracker started...")

for pin in PINCODE_LIST:
    print(f"\n🔍 Checking pincode: {pin}")

    driver = setup_driver()  # ✅ ONE driver per pincode
    in_stock_items = []

    try:
        set_location(driver, pin)

        for product in PRODUCTS:
            print(f"🛒 Checking product: {product['name']}")

            if check_stock(driver, product["url"]):
                in_stock_items.append(product["name"])

        # ✅ SEND ONE COMBINED ALERT PER PINCODE
        if in_stock_items:
            product_list = "\n".join([f"• {p}" for p in in_stock_items])
            msg = f"🟢 STOCK FOUND at pincode {pin}:\n{product_list}"
            print(msg)
            send_telegram(msg)
        else:
            print(f"❌ No stock at {pin}")

    finally:
        driver.quit()

print("\n✅ Run completed.")
