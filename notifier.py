import requests

BOT_TOKEN = "8189834771:AAFQXjbYiedd7_6hAEGl2HkCZmh8PfV_8w4"
CHAT_ID = "660538450"

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Erreur envoi Telegram : {e}")
