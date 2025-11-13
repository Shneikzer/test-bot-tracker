from flask import Flask, request
import os, time, json, requests, sys

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FB_PIXEL_ID = os.getenv("FB_PIXEL_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    print("📥 Requête reçue sur /webhook")
    try:
        print("Headers:", dict(request.headers))
        raw_body = request.data.decode('utf-8', errors='ignore')
        print("Body brut:", raw_body)

        try:
            data = request.get_json(silent=True) or {}
            print("JSON parsé :", json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print("❌ Erreur parsing JSON :", e)

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

