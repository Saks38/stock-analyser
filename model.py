import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression


def get_prediction(symbol, date=None, mode="daily"):
    try:
        # ✅ Auto-fix symbol (if user types SBIN instead of SBIN.NS)
        if "." not in symbol:
            symbol += ".NS"

        # 📊 Fetch data
        if mode == "intraday":
            df = yf.download(symbol, period="1d", interval="5m")
        else:
            df = yf.download(symbol, period="3mo")

        if df.empty:
            return {"error": "No data found for this stock"}

        prices = df["Close"].dropna()

        # 🔢 Prepare data for ML
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices.values

        # 🤖 Train model
        model = LinearRegression()
        model.fit(X, y)

        # 🔮 Predict next value
        next_index = np.array([[len(prices)]])
        predicted_price = model.predict(next_index)[0]   # ✅ FIX HERE

        # 💰 Current price
        current_price = y[-1]

        # ✅ Convert to normal Python float (IMPORTANT FIX)
        current_price = float(current_price)
        predicted_price = float(predicted_price)

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
