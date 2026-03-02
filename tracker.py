import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ===== CONFIG =====
URL = "https://www.bigbasket.com/pd/40330602/apple-iphone-16-128gb-black-1-n/"
BOT_TOKEN = "8711989091:AAHVL-8-273rEIRl6j4q9KP-iNkvkhaaXr4"
CHAT_ID = "6809727939"
# ==================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def check_stock():
    return True


print("🔍 Checking stock...")

try:
    if check_stock():
        send_telegram("🟢 iPhone 16 is IN STOCK on BigBasket!")
        print("✅ In stock!")
    else:
        print("❌ Still out of stock")
except Exception as e:
    print("Error:", e)
