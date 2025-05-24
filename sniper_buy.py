from web3 import Web3
import os
from dotenv import load_dotenv
import time
from notifier import send_alert
import json

# Charger les variables d'environnement
load_dotenv()
RPC = os.getenv("BSC_RPC")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

# Connexion BSC
web3 = Web3(Web3.HTTPProvider(RPC))
assert web3.is_connected(), "❌ Connexion échouée à BSC"

# Adresse du router PancakeSwap V2
ROUTER_ADDRESS = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")

# ABI minimal du router
ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def buy_token(token_address, amount_bnb=0.01, slippage=15):
    try:
        token_address = Web3.to_checksum_address(token_address)
        path = [
            Web3.to_checksum_address("0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"),  # WBNB
            token_address
        ]
        deadline = int(time.time()) + 60

        tx = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            0, path, PUBLIC_KEY, deadline
        ).build_transaction({
            'from': PUBLIC_KEY,
            'value': web3.to_wei(amount_bnb, 'ether'),
            'gas': 250000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(PUBLIC_KEY)
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_link = f"https://bscscan.com/tx/{web3.to_hex(tx_hash)}"
        print(f"✅ Transaction envoyée : {tx_link}")

        # ✅ Notification Telegram
        send_alert(f"""
💥 <b>Achat exécuté</b> par ton bot sniper
🔗 <b>Token</b> : {token_address}
💰 <b>Montant</b> : {amount_bnb} BNB
🔎 <a href="{tx_link}">Voir la transaction</a>
""")

        # 🔐 Enregistrement du trade
        try:
            with open("wallet_tracker.json", "r") as f:
                old = json.load(f)
        except:
            old = []

        old.append({
            "token": token_address,
            "buy_price": amount_bnb,  # simple pour commencer
            "amount": web3.to_wei(amount_bnb, 'ether')
        })

        with open("wallet_tracker.json", "w") as f:
            json.dump(old, f, indent=2)

    except Exception as e:
        print(f"❌ Erreur d'achat : {str(e)}")
        send_alert(f"❌ <b>Erreur d'achat</b> : {str(e)}")

