import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
URL = "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/?utm_source=bigbasket&utm_medium=share_product&utm_campaign=share_product&ec_id=10"
BOT_TOKEN = "8711989091:AAHVL-8-273rEIRl6j4q9KP-iNkvkhaaXr"
CHAT_ID = "6809727939"

# ⭐ PUT YOUR 4 PINCODES HERE
PINCODE_LIST = ["122001", "122002", "122018", "122015"]
# ==================


def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(api_url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
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


def check_stock_for_pincode(pincode):
    driver = setup_driver()

    try:
        set_location(driver, pincode)

        driver.get(URL)
        time.sleep(8)

        page_text = driver.page_source.lower()

        if "add to basket" in page_text:
            return True
        return False

    finally:
        driver.quit()


# ===== MAIN =====
print("🔍 Checking BigBasket stock for multiple pincodes...")

try:
    found_any = False

    for pin in PINCODE_LIST:
        print(f"\nChecking pincode: {pin}")

        try:
            in_stock = check_stock_for_pincode(pin)

            if in_stock:
                found_any = True
                msg = f"🟢 iPhone 17 is IN STOCK at pincode {pin}!"
                print(msg)
                send_telegram(msg)

        except Exception as e:
            print(f"Error checking {pin}:", e)

    if not found_any:
        print("❌ Out of stock in all pincodes")

except Exception as err:
    print("❌ Script error:", err)
