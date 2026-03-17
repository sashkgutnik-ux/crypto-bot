from flask import Flask, request, jsonify

app = Flask(__name__)

# сюда мы будем передавать сигнал в бот
execution_engine = None


def set_execution_engine(engine):
    global execution_engine
    execution_engine = engine


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if not data:
        return jsonify({"error": "No data"}), 400

    signal = data.get("signal")
    symbol = data.get("symbol")
    price = data.get("price")

    print("📡 TradingView signal received:", data)

    if execution_engine:

        if signal == "BUY":
            execution_engine.execute("BUY", price)

        elif signal == "SELL":
            execution_engine.execute("SELL", price)

    return jsonify({"status": "ok"})


def start_server():

    print("🚀 TradingView webhook server started")

    app.run(host="0.0.0.0", port=5000)
