import os
import requests
import time

# ================= CONFIG =================

PRODUCTS = [
    {
        "name": "iPhone 17 White",
        "url": "https://www.bigbasket.com/pd/40356301/",
    },
    {
        "name": "iPhone 16 Black",
        "url": "https://www.bigbasket.com/pd/40330602/",
    },
]

CHAT_IDS = [
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2"),
]

BOT_TOKEN = os.getenv("BOT_TOKEN")

PINCODE_LIST = ["122001", "122002", "122018", "122015"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

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


def check_stock(url, pincode):
    """Fast stock check using requests"""

    try:
        session = requests.Session()

        # Set location cookie (important)
        session.cookies.set("bb-location", pincode)

        r = session.get(url, headers=HEADERS, timeout=15)

        text = r.text.lower()

        return "add to basket" in text

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("⚡ Ultra-fast tracker started...")

for pin in PINCODE_LIST:
    print(f"\n📍 Checking pincode: {pin}")

    for product in PRODUCTS:
        print(f"🛒 Checking: {product['name']}")

        in_stock = check_stock(product["url"], pin)

        if in_stock:
            msg = f"🟢 {product['name']} is IN STOCK at pincode {pin}!"
            print(msg)
            send_telegram(msg)

        time.sleep(2)  # small polite delay
