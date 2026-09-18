def get_data():
    df = yf.download("GC=F", period="6mo", interval="1d")
    c = df['Close']
    h = df['High']
    l = df['Low']
    
    # ADR 14
    daily_range = (h - l).rolling(14).mean()
    adr = safe_float(daily_range)
    
    price = safe_float(c)
    e9 = safe_float(c.ewm(span=9).mean())
    e21 = safe_float(c.ewm(span=21).mean())
    e50 = safe_float(c.ewm(span=50).mean())
    e200 = safe_float(c.ewm(span=200).mean())
    return price, e9, e21, e50, e200, adr

def levels(price, adr):
    # Все от ADR - динамические
    tp1 = adr * 0.25
    tp2 = adr * 0.50
    tp3 = adr * 0.80
    tp4 = adr * 1.20
    sl1 = adr * 0.30
    
    # Сигнал
    if e9 > e21:
        entry = price - 3
        return {
            "side": "BUY",
            "entry": entry,
            "tp1": entry + tp1,
            "tp2": entry + tp2,
            "tp3": entry + tp3,
            "tp4": entry + tp4,
            "sl": entry - sl1,
            "adr": adr
        }
    else:
        entry = price + 3
        return {
            "side": "SELL",
            "entry": entry,
            "tp1": entry - tp1,
            "tp2": entry - tp2,
            "tp3": entry - tp3,
            "tp4": entry - tp4,
            "sl": entry + sl1,
            "adr": adr
        }

# В сообщение добавь:
# f"ADR сегодня: ${adr:.1f}"
