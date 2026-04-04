from flask import Flask, request, jsonify
from flask_cors import CORS
from model import get_prediction
import yfinance as yf
import os

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({"message": "Stock Predictor API running 🚀"})


# 🔮 Prediction Route
@app.route("/predict")
def predict():
    try:
        symbol = request.args.get("symbol")
        date = request.args.get("date")
        mode = request.args.get("mode", "daily")

        if not symbol:
            return jsonify({"error": "Symbol required"}), 400

        result = get_prediction(symbol.upper(), date, mode)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📊 History (for graph)
@app.route("/history")
def history():
    try:
        symbol = request.args.get("symbol")
        mode = request.args.get("mode", "daily")

        stock = yf.Ticker(symbol)

        if mode == "intraday":
            df = stock.history(period="5d", interval="5m")
        else:
            df = stock.history(period="3mo")

        df.index = df.index.tz_localize(None)

        data = {
            "dates": df.index.strftime("%Y-%m-%d %H:%M").tolist(),
            "prices": df["Close"].tolist()
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)