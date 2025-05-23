from web3 import Web3
import os
import json
import time
from dotenv import load_dotenv
from notifier import send_alert

load_dotenv()

RPC = os.getenv("BSC_RPC")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")

web3 = Web3(Web3.HTTPProvider(RPC))
assert web3.is_connected(), "❌ Connexion BSC échouée"

ROUTER_ADDRESS = Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")
ROUTER_ABI = json.loads("""[
  {
    "name": "swapExactTokensForETHSupportingFeeOnTransferTokens",
    "type": "function",
    "inputs": [
      {"name": "amountIn", "type": "uint256"},
      {"name": "amountOutMin", "type": "uint256"},
      {"name": "path", "type": "address[]"},
      {"name": "to", "type": "address"},
      {"name": "deadline", "type": "uint256"}
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  }
]""")

router = web3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def sell_token(token_address, amount_token):
    try:
        token_address = Web3.to_checksum_address(token_address)
        path = [token_address, Web3.to_checksum_address("0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")]  # token -> WBNB

        deadline = int(time.time()) + 60

        # Approve le token pour swap
        token_abi = [{"name": "approve", "type": "function", "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "outputs": [{"name": "success", "type": "bool"}], "stateMutability": "nonpayable"}]
        token_contract = web3.eth.contract(address=token_address, abi=token_abi)
        approve_tx = token_contract.functions.approve(ROUTER_ADDRESS, amount_token).build_transaction({
            'from': PUBLIC_KEY,
            'gas': 100000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(PUBLIC_KEY)
        })
        signed_approve = web3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
        web3.eth.send_raw_transaction(signed_approve.rawTransaction)

        # Transaction de vente
        sell_tx = router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amount_token,
            0,
            path,
            PUBLIC_KEY,
            deadline
        ).build_transaction({
            'from': PUBLIC_KEY,
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(PUBLIC_KEY)
        })
        signed_sell = web3.eth.account.sign_transaction(sell_tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_sell.rawTransaction)

        tx_link = f"https://bscscan.com/tx/{web3.to_hex(tx_hash)}"
        print(f"✅ Vente envoyée : {tx_link}")
        send_alert(f"💸 Vente auto déclenchée\n🔗 Token : {token_address}\n🔎 {tx_link}")
    except Exception as e:
        print(f"❌ Erreur de vente : {e}")
        send_alert(f"❌ Erreur de vente : {e}")
