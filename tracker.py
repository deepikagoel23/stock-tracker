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

CHAT_IDS = list(set([
    os.getenv("CHAT_ID_1"),
    os.getenv("CHAT_ID_2"),
]))

BOT_TOKEN = os.getenv("BOT_TOKEN")

PINCODE_LIST = ["122001", "122002", "122018", "122015"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

# ===========================================


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


def check_stock(url, pincode):
    """Fast stock check"""
    try:
        session = requests.Session()
        session.cookies.set("bb-location", pincode)

        r = session.get(url, headers=HEADERS, timeout=15)
        text = r.text.lower()

        return "add to basket" in text

    except Exception as e:
        print("Stock check error:", e)
        return False


# ================= MAIN =================

print("⚡ Combined tracker started...")

stock_found = {}

for product in PRODUCTS:
    available_pins = []

    for pin in PINCODE_LIST:
        print(f"🔍 {product['name']} → {pin}")

        if check_stock(product["url"], pin):
            available_pins.append(pin)

        time.sleep(2)

    if available_pins:
        stock_found[product["name"]] = available_pins


# ===== SEND ONLY ONE MESSAGE =====

if stock_found:
    message = "🟢 STOCK AVAILABLE:\n\n"

    for name, pins in stock_found.items():
        pin_list = ", ".join(pins)
        message += f"• {name} → {pin_list}\n"

    print(message)
    send_telegram(message)

else:
    print("❌ Nothing in stock")
