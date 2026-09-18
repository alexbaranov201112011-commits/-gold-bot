def get_data():
    df = yf.download("GC=F", period="1mo", interval="1h") # H1
    c = df['Close']
    h = df['High']
    l = df['Low']
    
    daily_range = (h - l).rolling(14).mean()
    adr = safe_float(daily_range) * 6  # *6 потому что мы на H1, приводим к дневному ADR
    
    price = safe_float(c)
    e9 = safe_float(c.ewm(span=9).mean())
    e21 = safe_float(c.ewm(span=21).mean())
    e50 = safe_float(c.ewm(span=50).mean())
    e200 = safe_float(c.ewm(span=200).mean())
    return price, e9, e21, e50, e200, adr
