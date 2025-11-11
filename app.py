from flask import Flask, request
import requests, time, os

app = Flask(__name__)

# Variables d’environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FB_PIXEL_ID = os.getenv("FB_PIXEL_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Vérifie qu'un nouvel utilisateur a rejoint
    if "message" in data:
        message = data["message"]
        if "new_chat_member" in message:
            user = message["new_chat_member"]
            user_id = user.get("id")
            first_name = user.get("first_name", "")
            send_lead_to_facebook(user_id, first_name)
    return "ok", 200

def send_lead_to_facebook(user_id, first_name):
    url = f"https://graph.facebook.com/v18.0/{FB_PIXEL_ID}/events"
    payload = {
        "data": [{
            "event_name": "Lead",
            "event_time": int(time.time()),
            "action_source": "system_generated",
            "event_source_url": "https://t.me/ton_canal",  # remplace par ton vrai lien
            "user_data": {
                "external_id": str(user_id)
            },
            "custom_data": {
                "telegram_first_name": first_name
            }
        }],
        "access_token": FB_ACCESS_TOKEN
    }
    requests.post(url, json=payload)
    print(f"✅ Lead envoyé à Facebook pour {first_name} ({user_id})")

@app.route('/')
def home():
    return "Elio's Bot Tracking API est en ligne ✅"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
