from web3 import Web3
import time

def detect_snipers(web3: Web3, pair_address: str, max_blocks=2):
    try:
        block_number = web3.eth.block_number
        pair = Web3.to_checksum_address(pair_address)
        threshold_gas = 100  # Gwei
        high_value_tx = 0

        for b in range(block_number - max_blocks, block_number + 1):
            block = web3.eth.get_block(b, full_transactions=True)
            for tx in block.transactions:
                if tx.to and tx.to.lower() == pair.lower():
                    gas_price_gwei = tx.gasPrice / 1e9
                    if gas_price_gwei >= threshold_gas:
                        high_value_tx += 1
        return high_value_tx >= 3
    except Exception as e:
        print(f"Erreur détection sniper : {e}")
        return False
