from flask import Flask
import threading, os, requests, time
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        return float(r.json()["price"])
    except:
        return None

def send(text):
    if TOKEN and CHAT:
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT}&text={text}", timeout=10)
        except:
            pass

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running OK!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_web, daemon=True).start()

print("Bot started...")
while True:
    price = get_price()
    if price:
        print(f"Gold: {price}")
    time.sleep(60)
