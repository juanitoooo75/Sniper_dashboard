import json
import time
import requests
from sniper_sell import sell_token
from export_excel import export_trade

TRACKER_FILE = "wallet_tracker.json"
MEMORY_FILE = "sniper_memory.json"

def get_token_price_bnb(token_address):
    url = f"https://api.honeypot.is/v1/GetPairs?address={token_address}&chain=bsc"
    try:
        r = requests.get(url)
        data = r.json()
        return data['pairs'][0]['priceBNB']
    except:
        return None

def track_wallet():
    try:
        with open(TRACKER_FILE, "r") as f:
            tokens = json.load(f)
    except:
        tokens = []

    updated = []

    for t in tokens:
        current_price = get_token_price_bnb(t["token"])
        if current_price is None:
            continue

        buy_price = t["buy_price"]
        gain = (current_price - buy_price) / buy_price

        print(f"💹 {t['token']} | achat : {buy_price:.8f} | actuel : {current_price:.8f} | gain : {gain*100:.2f}%")

        if gain >= 1.0:
            print("🚀 x2 atteint — VENTE")
            sell_token(t["token"], int(t["amount"]))

            # Enregistrer comme succès
            try:
                with open(MEMORY_FILE, "r") as mem:
                    memory = json.load(mem)
            except:
                memory = []

            trade_data = {
                "token": t["token"],
                "buy_price": buy_price,
                "sell_price": current_price,
                "gain": gain,
                "timestamp": time.time()
            }

            memory.append(trade_data)

            with open(MEMORY_FILE, "w") as mem:
                json.dump(memory, mem, indent=2)

            # Export CSV
            export_trade({
                "token": t["token"],
                "buy_price": buy_price,
                "sell_price": current_price,
                "gain_%": round(gain * 100, 2)
            })

        elif gain <= -0.3:
            print("🛑 Stop Loss atteint — VENTE")
            sell_token(t["token"], int(t["amount"]))
        else:
            updated.append(t)

    with open(TRACKER_FILE, "w") as f:
        json.dump(updated, f, indent=2)

if __name__ == "__main__":
    while True:
        print("🔄 Vérification des tokens en portefeuille...")
        track_wallet()
        time.sleep(300)  # Toutes les 5 minutes
