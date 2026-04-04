import os
from dotenv import load_dotenv
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
import yfinance as yf

load_dotenv()
API_KEY = os.getenv("API_KEY")


# 🔁 YFINANCE (DAILY)
def fetch_daily(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(start="2025-01-01")

    if df.empty:
        raise Exception("No daily data")

    df = df.rename(columns={"Close": "4. close"})
    df = df.dropna()
    df = df.sort_index()

    # remove timezone
    df.index = df.index.tz_localize(None)

    return df[["4. close"]]


# ⏱️ YFINANCE (INTRADAY)
def fetch_intraday(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="5d", interval="5m")

    if df.empty:
        raise Exception("No intraday data")

    df = df.rename(columns={"Close": "4. close"})
    df = df.dropna()
    df = df.sort_index()

    df.index = df.index.tz_localize(None)

    return df[["4. close"]]


def get_prediction(symbol, selected_date=None, mode="daily"):

    # 🔥 SELECT DATA MODE
    if mode == "intraday":
        df = fetch_intraday(symbol)
    else:
        df = fetch_daily(symbol)

    # 🗓️ DATE FILTER (ONLY FOR DAILY)
    if selected_date and mode == "daily":
        selected_date = pd.to_datetime(selected_date)
        df = df[df.index.date <= selected_date.date()]

        if df.empty:
            raise Exception("No data before selected date.")

    # ❗ MIN DATA CHECK
    if len(df) < 60:
        raise Exception("Not enough data.")

    # 📊 FEATURES
    df["MA10"] = df["4. close"].rolling(10).mean()
    df["MA50"] = df["4. close"].rolling(50).mean()
    df = df.dropna()

    feature_df = df[["MA10", "MA50", "4. close"]]

    # 🎯 TARGET
    X_all = feature_df[["MA10", "MA50"]]
    y_next = feature_df["4. close"].shift(-1)

    X_train = X_all.iloc[:-1]
    y_train = y_next.iloc[:-1]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # 🔮 PREDICTION
    latest_features = X_all.iloc[-1].values.reshape(1, -1)
    predicted_price = float(model.predict(latest_features)[0])
    current_price = float(feature_df["4. close"].iloc[-1])

    direction = "UP 📈" if predicted_price > current_price else "DOWN 📉"

    return {
        "symbol": symbol,
        "mode": mode,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "direction": direction,
        "used_date": str(df.index[-1])
    }