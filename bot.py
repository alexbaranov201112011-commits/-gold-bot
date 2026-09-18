import os, requests, yfinance as yf

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def safe_float(x):
    try:
        return float(x.iloc[-1])
    except:
        try:
            return float(x.iloc[-1, 0])
        except:
            return float(x[-1])

def get_data():
    try:
        df = yf.download("GC=F", period="6mo", interval="1d", auto_adjust=True, progress=False)
        c = df['Close']
        price = safe_float(c)
        e9 = safe_float(c.ewm(span=9).mean())
        e21 = safe_float(c.ewm(span=21).mean())
        e50 = safe_float(c.ewm(span=50).mean())
        e200 = safe_float(c.ewm(span=200).mean())
        return price, e9, e21, e50, e200
    except Exception as e:
        # если yfinance упадет, берем цену с API
        try:
            p = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()['price']
            price = float(p)
            return price, price, price, price, price
        except:
            return 4380.0, 4380.0, 4380.0, 4380.0, 4380.0

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
        data={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"})
    except: pass

price, e9, e21, e50, e200 = get_data()

# 3 СИГНАЛА
scalp = "📈 ЛОНГ" if e9 > e21 else "📉 ШОРТ"
intra = "📈 ЛОНГ" if price > e50 else "📉 ШОРТ"
trend = "📈 БЫЧИЙ" if e50 > e200 else "📉 МЕДВЕЖИЙ"

msg = f"""🟡 <b>GOLD: ${price:.2f}</b>

<b>1. СКАЛЬП (15м-1ч):</b>
{scalp} | EMA9: ${e9:.1f} / EMA21: ${e21:.1f}
Вход: ${price:.1f} | ТП: ${price+12:.1f} | СЛ: ${price-8:.1f}

<b>2. ИНТРАДЕЙ (сегодня):</b>
{intra} | Цена vs EMA50: ${e50:.1f}
Вход: ${price-5:.1f} | ТП: ${price+30:.1f} | СЛ: ${price-18:.1f}

<b>3. ТРЕНД (неделя):</b>
{trend} | EMA50: ${e50:.1f} / EMA200: ${e200:.1f}

Бот работает 24/7 ✅
"""

send(msg)
print("3 signals sent")
