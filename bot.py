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
    df = yf.download("GC=F", period="6mo", interval="1d", auto_adjust=True, progress=False)
    c = df['Close']
    price = safe_float(c)
    e9 = safe_float(c.ewm(span=9).mean())
    e21 = safe_float(c.ewm(span=21).mean())
    e50 = safe_float(c.ewm(span=50).mean())
    e200 = safe_float(c.ewm(span=200).mean())
    return price, e9, e21, e50, e200

def send(t):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
    data={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"})

price, e9, e21, e50, e200 = get_data()

# Логика
is_scalp_long = e9 > e21
is_intra_long = price > e50
is_trend_bull = e50 > e200

# Правильные ТП/СЛ для ЛОНГ и ШОРТ
def levels(p, is_long, tp1, sl1):
    if is_long:
        entry = p - 3
        tp = entry + tp1
        sl = entry - sl1
    else:
        entry = p + 3
        tp = entry - tp1
        sl = entry + sl1
    return entry, tp, sl

s_entry, s_tp, s_sl = levels(price, is_scalp_long, 12, 8)
i_entry, i_tp, i_sl = levels(price, is_intra_long, 30, 18)

scalp_txt = "📈 ЛОНГ" if is_scalp_long else "📉 ШОРТ"
intra_txt = "📈 ЛОНГ" if is_intra_long else "📉 ШОРТ"
trend_txt = "📈 БЫЧИЙ" if is_trend_bull else "📉 МЕДВЕЖИЙ"

msg = f"""🟡 <b>GOLD: ${price:.2f}</b>

<b>1. СКАЛЬП (15м-1ч):</b>
{scalp_txt} | EMA9: ${e9:.1f} / EMA21: ${e21:.1f}
Вход: ${s_entry:.1f} | ТП: ${s_tp:.1f} | СЛ: ${s_sl:.1f}

<b>2. ИНТРАДЕЙ (сегодня):</b>
{intra_txt} | Цена vs EMA50: ${e50:.1f}
Вход: ${i_entry:.1f} | ТП: ${i_tp:.1f} | СЛ: ${i_sl:.1f}

<b>3. ТРЕНД (неделя):</b>
{trend_txt} | EMA50: ${e50:.1f} / EMA200: ${e200:.1f}

Бот работает 24/7 ✅
"""

send(msg)
