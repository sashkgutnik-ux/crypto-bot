import requests
import json
import re

DEEPSEEK_API_KEY = "sk-260fada1063646fdaf5bb5103ae225d3"


def choose_best_strategy(market_data):

    prompt = f"""
You are a crypto trading expert.

Rate the following strategies from 0 to 100 based on the market data.

Market data:
{market_data}

Strategies:
EMA
RSI
Breakout
Bollinger
Grid

Return ONLY JSON.
"""

    try:

        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=20
        )

        data = response.json()

        content = data["choices"][0]["message"]["content"]

        print("AI RAW RESPONSE:", content)

        # удаляем ```json
        content = re.sub(r"```json|```", "", content).strip()

        scores = json.loads(content)

        best_strategy = max(scores, key=scores.get)

        return scores, best_strategy

    except Exception as e:

        print("AI ERROR:", e)

        # fallback если AI сломался
        scores = {
            "EMA": 60,
            "RSI": 50,
            "Breakout": 55,
            "Bollinger": 52,
            "Grid": 45
        }

        best_strategy = max(scores, key=scores.get)

        return scores, best_strategy
