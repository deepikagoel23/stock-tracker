import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

PRODUCTS = [
    {
        "name": "iPhone 17 White",
        "url": "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/",
    },
    {
        "name": "iPhone 17 Black",
        "url": "https://www.bigbasket.com/pd/40356300/apple-iphone-17-256gb-black-1-unit/",
    },
    {
        "name": "iPhone 17 Mist Blue",
        "url": "https://www.bigbasket.com/pd/40356302/apple-iphone-17-256gb-mist-blue-1-unit/",
    },
    {
        "name": "iPhone 16 Black",
        "url": "https://www.bigbasket.com/pd/40330602/apple-iphone-16-128gb-black-1-n/",
    },
    {
        "name": "iPhone 16 Ultramarine",
        "url": "https://www.bigbasket.com/pd/40330605/apple-iphone-16-128gb-ultramarine-1-n/",
    },
    {
        "name": "iPhone 16 Teal",
        "url": "https://www.bigbasket.com/pd/40330606/apple-iphone-16-128gb-teal-1-n/",
    },
]

PINCODES = [
    "Sector 10A,122001",
    "Sikander pur metro,122002",
    "Roots Courtyard,122018",
    "Sector 18,122015",
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

    chrome_options.page_load_strategy = "eager"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")

    # disable images for speed
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )

    return driver


def set_location(driver, pincode):
    """
    Set BigBasket location using cookies (stable method)
    """

    try:
        driver.get("https://www.bigbasket.com/")

        driver.add_cookie({
            "name": "bb-location",
            "value": pincode,
            "domain": ".bigbasket.com",
            "path": "/"
        })

        driver.refresh()

        time.sleep(2)

        print(f"📍 Location set: {pincode}")
        return True

    except Exception as e:
        print(f"❌ Location failed ({pincode}):", e)
        return False


def check_stock(driver, url):
    wait = WebDriverWait(driver, WAIT_TIME)

    try:
        driver.get(url)

        # wait for product page
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # look for ADD button
        buttons = driver.find_elements(By.XPATH, "//button")

        for btn in buttons:
            text = btn.text.lower()

            if "add" in text and ("basket" in text or "cart" in text):
                return True

            if "notify" in text or "out of stock" in text:
                return False

        return False

    except Exception as e:
        print("Stock check error:", e)
        return False

# ================= MAIN =================

print("🚀 BigBasket tracker started")

driver = setup_driver()

found_items = {}

try:

    for pincode in PINCODES:

        print(f"\n📍 Checking pincode: {pincode}")

        if not set_location(driver, pincode):
            continue

        for product in PRODUCTS:

            print(f"🛒 Checking: {product['name']}")

            in_stock = check_stock(driver, product["url"])

            if in_stock:

                found_items.setdefault(product["name"], []).append(
                    (pincode, product["url"])
                )

finally:
    driver.quit()


# ================= TELEGRAM ALERT =================

if found_items:

    timestamp = datetime.now().strftime("%d %b %Y %I:%M %p")

    lines = [
        "🚨 BIGBASKET STOCK ALERT 🚨",
        f"🕒 {timestamp}",
        ""
    ]

    for product_name, entries in found_items.items():

        lines.append(f"📦 {product_name}")

        for pin, url in entries:
            lines.append(f"   📍 Pincode: {pin}")
            lines.append(f"   🔗 {url}")

        lines.append("")

    message = "\n".join(lines)

    print(message)

    send_telegram(message)

else:
    print("❌ Nothing in stock anywhere")
