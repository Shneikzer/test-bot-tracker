from flask import Flask, request
import requests, time, os, json

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


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    print("📥 Update reçu de Telegram :")
    print(json.dumps(data, ensure_ascii=False))

    # 1) Cas "message" (groupes / supergroups)
    if "message" in data:
        msg = data["message"]
        chat_title = msg.get("chat", {}).get("title", "unknown")

        # Plusieurs nouveaux membres
        if "new_chat_members" in msg:
            for user in msg["new_chat_members"]:
                user_id = user.get("id")
                first_name = user.get("first_name", "")
                send_lead_to_facebook(user_id, first_name, chat_title)

        # Ancienne forme possible
        elif "new_chat_member" in msg:
            user = msg["new_chat_member"]
            user_id = user.get("id")
            first_name = user.get("first_name", "")
            send_lead_to_facebook(user_id, first_name, chat_title)

    # 2) Cas "my_chat_member" (typique pour canaux & approbations)
    if "my_chat_member" in data:
        mc = data["my_chat_member"]
        chat_title = mc.get("chat", {}).get("title", "unknown")
        old_status = mc.get("old_chat_member", {}).get("status")
        new_member = mc.get("new_chat_member", {})
        new_status = new_member.get("status")
        user = new_member.get("user", {})

        # On considère que c'est un "join" si status passe de left/kicked à member/admin/creator
        if old_status in ("left", "kicked") and new_status in ("member", "administrator", "creator"):
            user_id = user.get("id")
            first_name = user.get("first_name", "")
            send_lead_to_facebook(user_id, first_name, chat_title)

    return "ok", 200


@app.route('/')
def home():
    return "Elio's Bot Tracking API est en ligne ✅"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
