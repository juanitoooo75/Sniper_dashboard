from web3 import Web3
import json
import asyncio
import os
import time

from token_checker import check_token
from token_security import get_token_security
from sniper_buy import buy_token
from ai_filter import is_similar_to_bad_token
from ai_model import train_model, predict_token
from sniper_detector import detect_snipers

# Connexion BSC
BSC_RPC = os.getenv("BSC_RPC") or "https://bsc.publicnode.com"
web3 = Web3(Web3.HTTPProvider(BSC_RPC))
print("✅ Connecté à BSC :", web3.is_connected())

# Adresse de la Factory PancakeSwap V2
FACTORY_ADDRESS = Web3.to_checksum_address("0xca143ce32fe78f1f7019d7d551a6402fc5350c73")

# ABI PairCreated
FACTORY_ABI = json.loads("""[
  {
    "anonymous": false,
    "inputs": [
      { "indexed": true, "name": "token0", "type": "address" },
      { "indexed": true, "name": "token1", "type": "address" },
      { "indexed": false, "name": "pair", "type": "address" },
      { "indexed": false, "name": "", "type": "uint256" }
    ],
    "name": "PairCreated",
    "type": "event"
  }
]""")

factory = web3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)

print("🔎 Sniffer en écoute active...")

last_block = web3.eth.block_number
train_model()

while True:
    try:
        current_block = web3.eth.block_number
        if current_block <= last_block:
            time.sleep(5)
            continue

        events = factory.events.PairCreated().get_logs(from_block=last_block + 1, to_block=current_block)

        for event in events:
            token0 = event["args"]["token0"]
            token1 = event["args"]["token1"]
            pair = event["args"]["pair"]

            print("\n🆕 Nouvelle paire détectée !")
            print(f"🔹 Token0 : {token0}")
            print(f"🔹 Token1 : {token1}")
            print(f"🔗 Pair   : {pair}")

            print("🔍 Analyse Honeypot du token0...")
            result0 = asyncio.run(check_token(token0))
            print(result0)

            print("🔍 Analyse Honeypot du token1...")
            result1 = asyncio.run(check_token(token1))
            print(result1)

            print("🧠 Analyse GoPlus...")
            sec = get_token_security(token0)

            if sec.get("is_open_source") != "1":
                print("❌ Contrat non vérifié, skip.")
                continue
            if sec.get("is_proxy") == "1":
                print("❌ Proxy détecté, skip.")
                continue
            if sec.get("slippage_modifiable") == "1":
                print("❌ Slippage modifiable, skip.")
                continue
            if float(sec.get("buy_tax", "0")) > 15 or float(sec.get("sell_tax", "0")) > 15:
                print("❌ Taxe trop élevée, skip.")
                continue
            if sec.get("is_blacklisted") == "1":
                print("❌ Blacklist détectée, skip.")
                continue

            if is_similar_to_bad_token(token0):
                print("🛑 Token déjà vu ou similaire à une perte passée — SKIP")
                continue

            if not result0.get("honeypotResult", {}).get("isHoneypot", True):
                # Détection des snipers pro
                snipers_detected = detect_snipers(web3, pair)
                if snipers_detected:
                    print("🚨 Snipers pro détectés dans les 2 premiers blocs ! Score IA impacté.")
                else:
                    print("✅ Aucun sniper pro détecté.")

                # Préparation features IA
                features = {
                    "buy_tax": float(sec.get("buy_tax", "0")),
                    "sell_tax": float(sec.get("sell_tax", "0")),
                    "is_open_source": 1 if sec.get("is_open_source") == "1" else 0,
                    "is_proxy": 1 if sec.get("is_proxy") == "1" else 0
                }

                score = predict_token(features, token0)

                if snipers_detected:
                    score *= 0.6  # Pénalité sur le score

                print(f"🧠 Score IA cheatée : {round(score * 100)}%")

                if score >= 0.6 and features["buy_tax"] == 0 and features["sell_tax"] == 0:
                    print("💥 Mode cheaté : 0% tax + bon score — ACHAT forcé")
                    buy_token(token0)
                    continue

                if score < 0.7:
                    print("🛑 Score IA trop faible — skip.")
                    continue

                print("💰 Achat validé par l’IA V2")
                buy_token(token0)
            else:
                print("❌ Token0 identifié comme honeypot")

            print("-" * 60)

        last_block = current_block
        time.sleep(5)

    except Exception as e:
        print(f"❌ Erreur dans la boucle sniffer : {e}")
        time.sleep(5)

