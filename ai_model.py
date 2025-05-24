import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

model = None
recent_tokens = []

def train_model():
    global model, recent_tokens
    try:
        with open("sniper_memory.json", "r") as f:
            data = json.load(f)
    except:
        return

    rows = []
    recent_tokens = []

    for trade in data:
        try:
            rows.append({
                "buy_tax": float(trade.get("buy_tax", 0)),
                "sell_tax": float(trade.get("sell_tax", 0)),
                "is_open_source": 1 if trade.get("is_open_source") == "1" else 0,
                "is_proxy": 1 if trade.get("is_proxy") == "1" else 0,
                "gain": 1 if trade["gain"] > 0 else 0
            })

            if trade["gain"] > 0:
                recent_tokens.append(trade.get("token", ""))
        except:
            continue

    if len(rows) < 5:
        return

    df = pd.DataFrame(rows)
    X = df.drop("gain", axis=1)
    y = df["gain"]

    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X, y)

def predict_token(features: dict, token_address: str) -> float:
    global recent_tokens
    if model is None:
        return 0

    # boost score si similaire à gagnant précédent
    if token_address.lower() in [t.lower() for t in recent_tokens]:
        return 0.99

    x = pd.DataFrame([features])
    return model.predict_proba(x)[0][1]

