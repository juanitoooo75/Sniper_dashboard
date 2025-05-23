from flask import Flask, render_template_string, send_file
import json
import os
from web3 import Web3
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io

load_dotenv()

app = Flask(__name__)
web3 = Web3(Web3.HTTPProvider(os.getenv("BSC_RPC")))
wallet_address = os.getenv("PUBLIC_KEY")
TRACKER_FILE = "wallet_tracker.json"
MEMORY_FILE = "sniper_memory.json"

@app.route('/')
def dashboard():
    try:
        bnb_balance = web3.from_wei(web3.eth.get_balance(wallet_address), 'ether')
    except:
        bnb_balance = "Erreur"

    try:
        with open(TRACKER_FILE, "r") as f:
            open_positions = json.load(f)
    except:
        open_positions = []

    try:
        with open(MEMORY_FILE, "r") as f:
            closed_trades = json.load(f)
    except:
        closed_trades = []

    return render_template_string("""
    <html>
    <head>
        <title>Dashboard Sniper</title>
        <meta http-equiv="refresh" content="15">
        <style>
            body { font-family: Arial; background: #111; color: #eee; padding: 20px; }
            h1 { color: #00ffcc; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            td, th { padding: 8px; border: 1px solid #333; text-align: left; }
            th { background-color: #222; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard Sniper</h1>
        <p><b>Solde BNB :</b> {{ bnb_balance }}</p>

        <h2>📌 Positions ouvertes</h2>
        <table>
            <tr><th>Token</th><th>Montant</th><th>Prix achat</th></tr>
            {% for p in open_positions %}
            <tr>
                <td>{{ p.token }}</td>
                <td>{{ p.amount }}</td>
                <td>{{ p.buy_price }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>✅ Trades clôturés</h2>
        <table>
            <tr><th>Token</th><th>Gain %</th><th>Prix achat</th><th>Prix vente</th></tr>
            {% for t in closed_trades %}
            <tr>
                <td>{{ t.token }}</td>
                <td>{{ (t.gain * 100) | round(2) }}%</td>
                <td>{{ t.buy_price }}</td>
                <td>{{ t.sell_price }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>📈 Historique des gains</h2>
        <img src="/plot.png" width="100%">
    </body>
    </html>
    """, bnb_balance=bnb_balance, open_positions=open_positions, closed_trades=closed_trades)

@app.route('/plot.png')
def plot_png():
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    x = list(range(1, len(data) + 1))
    y = [float(d["gain"]) * 100 for d in data]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 3))  # 📏 taille réduite

    ax.plot(x, y, marker='o', linestyle='-', linewidth=2, markersize=6, color='#00ffcc')
    ax.fill_between(x, y, 0, where=[v >= 0 for v in y], color='#00ffcc', alpha=0.1)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1)

    ax.set_title("Performance des trades", fontsize=14, color='white')
    ax.set_xlabel("Trade #", fontsize=10)
    ax.set_ylabel("Gain (%)", fontsize=10)
    ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.5)

    plt.tight_layout()

    output = io.BytesIO()
    plt.savefig(output, format='png', dpi=100)
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

