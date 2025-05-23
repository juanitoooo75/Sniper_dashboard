import requests

def get_token_security(token_address):
    url = f"https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses={token_address}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] != 1:
            return {"status": "error", "reason": "API error"}
        return data["result"][token_address.lower()]
    except Exception as e:
        return {"status": "error", "reason": str(e)}
