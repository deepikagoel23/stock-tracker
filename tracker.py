import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
URL = "https://www.bigbasket.com/pd/40356301/apple-iphone-17-256gb-white-1-unit/"
BOT_TOKEN = "8711989091:AAGYuhXt2eLt6k_-De__-DcvtDyJYAw6RDA"
CHAT_ID = "6809727939"

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
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    return driver


def set_location(driver, pincode):
    """Robust location setter"""
    try:
        driver.get("https://www.bigbasket.com/")
        time.sleep(6)

        inputs = driver.find_elements("xpath", "//input")

        target = None
        for inp in inputs:
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            if "pincode" in placeholder:
                target = inp
                break

        if not target:
            print(f"⚠️ Pincode box not found for {pincode}")
            return

        target.clear()
        target.send_keys(pincode)
        time.sleep(3)

        # click first suggestion safely
        suggestions = driver.find_elements("xpath", "//li")
        if suggestions:
            suggestions[0].click()
            time.sleep(5)

        print(f"📍 Location set: {pincode}")

    except Exception as e:
        print(f"Location error ({pincode}):", e)


def check_stock_for_pincode(pincode):
    driver = setup_driver()

    try:
        set_location(driver, pincode)

        driver.get(URL)
        time.sleep(10)

        page_text = driver.page_source.lower()

        # stronger detection
        if any(word in page_text for word in ["out of stock", "sold out"]):
            return False

        if any(word in page_text for word in ["add to basket", "add to cart", ">add<"]):
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
