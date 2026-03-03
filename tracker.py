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

# ✅ EXACT DELIVERY LOCATIONS
LOCATIONS = [
    "Sikanderpur Metro, Gurgaon 122002",
    "Sector 10A, Gurgaon 122001",
    "Roots Courtyard, Gurgaon 122018",
    "Sector 18, Gurgaon 122015",
]

CHAT_IDS = [
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2"),
]

BOT_TOKEN = os.getenv("BOT_TOKEN")

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


def set_location(driver, location_text):
    """Set exact delivery location"""
    try:
        driver.get("https://www.bigbasket.com/")
        time.sleep(5)

        # Click location button
        driver.find_element(
            "xpath",
            "//button[contains(@class,'AddressDropdown__ChangeLocation')]"
        ).click()
        time.sleep(3)

        # Enter address
        box = driver.find_element(
            "xpath",
            "//input[@placeholder='Search for area, street name…']"
        )
        box.clear()
        box.send_keys(location_text)
        time.sleep(4)

        # Click first suggestion
        driver.find_element("xpath", "(//li)[1]").click()
        time.sleep(6)

        print(f"📍 Location set: {location_text}")

    except Exception as e:
        print(f"❌ Location error ({location_text}):", e)


def check_stock(driver, url):
    try:
        driver.get(url)
        time.sleep(6)

        page_text = driver.page_source.lower()

        # ✅ robust stock detection
        in_stock = (
            "add to basket" in page_text
            and "out of stock" not in page_text
        )

        return in_stock

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("🚀 Exact-location multi-product tracker started...")

driver = setup_driver()

alerts = []

try:
    for location in LOCATIONS:
        print(f"\n🔍 Checking location: {location}")

        set_location(driver, location)

        for product in PRODUCTS:
            print(f"🛒 Checking product: {product['name']}")

            in_stock = check_stock(driver, product["url"])

            if in_stock:
                alerts.append(
                    f"🟢 {product['name']} IN STOCK at 📍 {location}"
                )

finally:
    driver.quit()

# ✅ SINGLE COMBINED ALERT
if alerts:
    final_message = "🚨 STOCK ALERT 🚨\n\n" + "\n".join(alerts)
    print(final_message)
    send_telegram(final_message)
else:
    print("❌ Nothing in stock anywhere.")
