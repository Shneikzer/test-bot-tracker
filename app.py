from flask import Flask, request
import os, time, json, requests, sys

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FB_PIXEL_ID = os.getenv("FB_PIXEL_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

def send_lead_to_facebook(user_id, first_name, channel_title):
    if not FB_PIXEL_ID or not FB_ACCESS_TOKEN:
        print("❌ FB_PIXEL_ID ou FB_ACCESS_TOKEN manquant. Vérifie tes variables d'environnement sur Render.")
        return

    url = f"https://graph.facebook.com/v18.0/{FB_PIXEL_ID}/events"

    payload = {
        "data": [{
            "event_name": "Lead",
            "event_time": int(time.time()),
            "action_source": "system_generated",
            "event_source_url": "https://t.me/" + (channel_title or "unknown"),
            "user_data": {
                # Identifiant Telegram anonymisé côté Meta
                "external_id": str(user_id)
            },
            "custom_data": {
                "telegram_first_name": first_name,
                "telegram_channel": channel_title
            }
        }],
        "access_token": FB_ACCESS_TOKEN
    }

    resp = requests.post(url, json=payload)
    print(f"✅ Lead envoyé à Facebook pour {first_name} ({user_id}) depuis {channel_title}")
    print(f"➡️ Réponse Meta: {resp.status_code} {resp.text}")
    sys.stdout.flush()


@app.route('/webhook', methods=['POST'])
def webhook():
    print("📥 Requête reçue sur /webhook")
    try:
        raw_body = request.data.decode('utf-8', errors='ignore')
        print("Body brut:", raw_body)

        data = request.get_json(silent=True) or {}
        print("JSON parsé :", json.dumps(data, ensure_ascii=False))

        # 🔹 Cas 1 : chat_join_request (canal privé avec approbation)
        if "chat_join_request" in data:
            cjr = data["chat_join_request"]
            chat = cjr.get("chat", {})
            user = cjr.get("from", {})

            channel_title = chat.get("title", "unknown")
            user_id = user.get("id")
            first_name = user.get("first_name", "")

            print(f"👉 Nouvelle demande de join sur {channel_title} par {first_name} ({user_id})")
            send_lead_to_facebook(user_id, first_name, channel_title)

        sys.stdout.flush()
    except Exception as e:
        print("❌ Erreur dans /webhook :", e)
        sys.stdout.flush()

    return "ok", 200


@app.route('/')
def home():
    return "Elio's Bot Tracking API est en ligne ✅"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


