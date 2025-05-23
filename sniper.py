from web3 import Web3
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
RPC_URL = os.getenv("BSC_RPC")

# Connexion à Binance Smart Chain
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    print("❌ Connexion échouée à BSC")
    exit()

print("✅ Connecté à Binance Smart Chain")

# Affiche le solde du wallet
balance = web3.eth.get_balance(PUBLIC_KEY)
bnb_balance = web3.from_wei(balance, 'ether')
print(f"💰 Ton wallet contient : {bnb_balance} BNB")
