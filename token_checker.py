import aiohttp
import asyncio

async def check_token(token_address):
    url = f"https://api.honeypot.is/v1/IsHoneypot?address={token_address}&chain=bsc"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {"status": "error", "reason": f"API {response.status}"}
                data = await response.json()
                return data
    except Exception as e:
        return {"status": "error", "reason": str(e)}
