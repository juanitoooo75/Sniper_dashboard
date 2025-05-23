import json

def is_similar_to_bad_token(token_address):
    try:
        with open("sniper_memory.json", "r") as f:
            memory = json.load(f)
    except:
        return False

    bad_tokens = [t for t in memory if t.get("gain", 0) < 0]

    for bad in bad_tokens:
        if bad["token"] == token_address:
            return True  # même token qu'un ancien perdant
    return False

