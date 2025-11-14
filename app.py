from flask import Flask, request
import os, time, json, requests, sys

app = Flask(__name__)

# 🟢 MAP CANAUX → PIXELS
# Mets ici tes vrais chat_id de canaux Telegram, et les pixels associés.
# Pour chaque canal (clé = chat_id), tu peux mettre 1 ou plusieurs pixels.
PIXEL_MAP = {
    # EXEMPLES – À REMPLACER PAR TES VRAIES VALEURS

    # Canal Test : un seul pixel
    -1003349861305: [
        {
            "pixel_id": "1515557479720413",
            "token": "EAASWQPXDKG0BP8qQfIodKpPd3WPJVZCbkPdkv6BMoLmZCXj3tnZBawTOhuddMnqZBBN30eCRgeTCDHhwHaaZAx4xQds7JwRgYUq5gW67uF1QeTccCkGhAhNWtCljn5ZCuMY7z05rKwrBCjgghsMZAmF7cVKxfg9gB6C2gpicPoWvIIeKAvIQAZATOIt4NU7EPQZDZD"
        }
    ],

     # Canal The Elio's : un seul pixel
    -1002308862086: [
        {
            "pixel_id": "1808434190556585",
            "token": "EAAYixVMVkbgBP7qEQOEMgmdSVfw6EdBdkyGe76LLVqBfKbFXOJkqP8Rju5o2lZBLwFk9Sz3JvwS6Q9zoNPjWjBi74PvWP6Qy4IEHRZAlywoxuS6R0Iv88jFfDIzLWaGcSN0WjpmF4E8LUluT54VFjweFvLS2n5R1irAlfZAKghI0ZAGGXUOBZCNZBaosKWlAZDZD"
        }
    ],

    # Canal Elio It : un seul pixel
    -1002658549927: [
        {
            "pixel_id": "1025214086229391",
            "token": "EAAYixVMVkbgBP5M7BrzXGCrc4sDxuygifNMrooR9iti2f42qqhyftuio5HSYzCgnPhATkA8qG50IDZAqYOgF9mNUqBOIX3vLFoNk5HJvHs0QFFszE0ueBkhtkKMON9VZCGdEDXTfaMCV70ZACMIrxEzhUWlKlVizVpiGRDvuBS4ZCh8u1uHWwjgOgGGDMwZDZD"
        }
    ],

     # Canal Anto UK : un seul pixel
    -1002797992543: [
        {
            "pixel_id": "2937051599829997",
            "token": "EAATHiAwgz70BP14c2RzcAtDf1GgVDsYxcdrkTrzvb58FOplxfUKFRJTIPCAOBZB5H9StwSIZCvzoto6LeECuFljuXG1V4s4KqL498NbEPKJZApLuR13spFfVYL3oZCGnoiYYZAt9YrNpizmdMUZAGG1hobqZCJCwTog0EDGTLtkkValQARUqwpIZBsxQsrpidwZDZD"
        }
    ],
}

# 🔐 On garde uniquement le token Telegram dans les variables d'env Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # utile juste pour vérifier plus tard si besoin


def send_lead_to_one_pixel(user_id, first_name, channel_title, pixel_id, access_token):
    """Envoie un event Lead à UN pixel Meta."""
    url = f"https://graph.facebook.com/v18.0/{pixel_id}/events"

     payload = {
        "data": [{
            "event_name": "Lead",
            "event_time": int(time.time()),
            "action_source": "system_generated",
            "event_source_url": "https://t.me/" + (channel_title or "unknown"),
            "event_id": "join_telegram",  # synchronisation navigateur <-> serveur
            "user_data": {
                "external_id": str(user_id)
            },
            "custom_data": {
                "telegram_first_name": first_name,
                "telegram_channel": channel_title
            }
        }],
        "access_token": access_token
    }



    resp = requests.post(url, json=payload)
    print(f"✅ Lead envoyé à Facebook pour {first_name} ({user_id}) sur pixel {pixel_id}")
    print(f"➡️ Réponse Meta: {resp.status_code} {resp.text}")
    sys.stdout.flush()


def send_lead_to_all_pixels(user_id, first_name, channel_title, chat_id):
    """Récupère tous les pixels liés à ce canal et envoie le Lead à chacun."""
    pixels = PIXEL_MAP.get(chat_id, [])

    if not pixels:
        print(f"⚠️ Aucun pixel configuré pour ce canal (chat_id={chat_id}, title={channel_title})")
        sys.stdout.flush()
        return

    for p in pixels:
        pixel_id = p.get("pixel_id")
        token = p.get("token")
        if not pixel_id or not token:
            print(f"❌ pixel_id ou token manquant pour chat_id={chat_id}")
            continue
        send_lead_to_one_pixel(user_id, first_name, channel_title, pixel_id, token)


@app.route('/webhook', methods=['POST'])
def webhook():
    print("📥 Requête reçue sur /webhook")
    try:
        raw_body = request.data.decode('utf-8', errors='ignore')
        print("Body brut:", raw_body)

        data = request.get_json(silent=True) or {}
        print("JSON parsé :", json.dumps(data, ensure_ascii=False))

        # 🔹 Cas : chat_join_request (canal privé avec approbation)
        if "chat_join_request" in data:
            cjr = data["chat_join_request"]
            chat = cjr.get("chat", {})
            user = cjr.get("from", {})

            channel_title = chat.get("title", "unknown")
            chat_id = chat.get("id")
            user_id = user.get("id")
            first_name = user.get("first_name", "")

            print(f"👉 Nouvelle demande de join sur {channel_title} ({chat_id}) par {first_name} ({user_id})")
            send_lead_to_all_pixels(user_id, first_name, channel_title, chat_id)

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
