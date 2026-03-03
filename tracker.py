import os
import requests
from datetime import datetime
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

WAIT_TIME = 12  # tuned for speed

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

    # ⚡ SPEED BOOSTERS
    chrome_options.page_load_strategy = "eager"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")

    # 🚀 Block images for speed
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )

    driver.set_page_load_timeout(40)
    return driver


def set_location(driver, location_text):
    wait = WebDriverWait(driver, WAIT_TIME)

    try:
        driver.get("https://www.bigbasket.com/")

        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class,'AddressDropdown__ChangeLocation')]"
        ))).click()

        box = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//input[contains(@placeholder,'Search')]"
        )))
        box.clear()
        box.send_keys(location_text)

        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "(//li)[1]"
        ))).click()

        print(f"📍 Location set: {location_text}")

    except Exception as e:
        print(f"❌ Location error ({location_text}):", e)


def check_stock(driver, url):
    try:
        driver.get(url)
        page_text = driver.page_source.lower()

        return (
            "add to basket" in page_text
            and "out of stock" not in page_text
            and "currently unavailable" not in page_text
        )

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("⚡ Lightning-fast tracker started...")

driver = setup_driver()
found_items = {}

try:
    for location in LOCATIONS:
        print(f"\n🔍 Checking location: {location}")
        set_location(driver, location)

        for product in PRODUCTS:
            print(f"🛒 Checking product: {product['name']}")

            if check_stock(driver, product["url"]):
                found_items.setdefault(product["name"], []).append(
                    (location, product["url"])
                )

finally:
    driver.quit()

# ✅ PREMIUM COMBINED ALERT
if found_items:
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    lines = [
        "🚨 BIGBASKET STOCK ALERT 🚨",
        f"🕒 {timestamp}",
        ""
    ]

    for product_name, entries in found_items.items():
        lines.append(f"📦 {product_name}")
        for location, url in entries:
            lines.append(f"   📍 {location}")
            lines.append(f"   🔗 {url}")
        lines.append("")

    final_message = "\n".join(lines)
    print(final_message)
    send_telegram(final_message)

else:
    print("❌ Nothing in stock anywhere.")
