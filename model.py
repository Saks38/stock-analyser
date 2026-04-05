import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression


def get_prediction(symbol, date=None, mode="daily"):
    try:
        # ✅ Fix symbol automatically
        symbol = symbol.upper()
        if "." not in symbol:
            symbol += ".NS"

        # 📊 Fetch data
        if mode == "intraday":
            df = yf.download(symbol, period="1d", interval="5m")
        else:
            df = yf.download(symbol, period="3mo")

        if df.empty:
            return {"error": "No data found"}

        # 🔢 Clean price data (IMPORTANT FIX)
        prices = df["Close"].dropna().values.flatten()

        # 🧠 ML prep
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices.astype(float)

        # 🤖 Train
        model = LinearRegression()
        model.fit(X, y)

        # 🔮 Predict next
        next_index = np.array([[len(prices)]])
        predicted_price = model.predict(next_index)

        # ✅ FORCE SCALAR (FINAL FIX)
        predicted_price = float(predicted_price.item())
        current_price = float(y[-1])

        # 📈 Direction
        direction = "UP 📈" if predicted_price > current_price else "DOWN 📉"

        return {
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "direction": direction,
            "used_date": str(df.index[-1].date()),
            "mode": mode
        }

    except Exception as e:
        return {"error": str(e)}
