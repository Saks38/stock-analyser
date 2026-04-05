import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

def get_prediction(symbol, date=None, mode="daily"):
    try:
        if mode == "intraday":
            df = yf.download(symbol, period="1d", interval="5m")
        else:
            df = yf.download(symbol, period="3mo")

        if df.empty:
            return {"error": "No data found"}

        prices = df['Close'].dropna()

        # Convert to numpy
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices.values

        model = LinearRegression()
        model.fit(X, y)

        # Predict next value
        next_index = np.array([[len(prices)]])
        predicted_price = model.predict(next_index)[0]

        current_price = y[-1]

        direction = "UP 📈" if predicted_price > current_price else "DOWN 📉"

        return {
            "current_price": round(float(current_price), 2),
            "predicted_price": round(float(predicted_price), 2),
            "direction": direction,
            "used_date": str(df.index[-1].date()),
            "mode": mode
        }

    except Exception as e:
        return {"error": str(e)}
