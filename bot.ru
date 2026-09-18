
import os, requests
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID") or "6832635346"
print(f"TOKEN ends with: ...{BOT_TOKEN[-5:] if BOT_TOKEN else 'NONE'}")
print(f"CHAT_ID is: {CHAT_ID}")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "✅ ТЕСТ СВЯЗИ - бот работает!"}
r = requests.post(url, json=data, timeout=15)
print(f"Telegram answer: {r.status_code} {r.text}")
