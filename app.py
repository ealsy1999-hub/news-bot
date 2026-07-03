import threading
import os
import sys
import time
import requests
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "News Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def self_ping():
    url = os.environ.get("RENDER_EXTERNAL_URL", "https://news-bot-vhvt.onrender.com")
    while True:
        time.sleep(600)
        try:
            requests.get(url, timeout=10)
            print(f"✓ Self-ping OK")
        except Exception as e:
            print(f"✗ Ping failed: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    from bot import main
    main()
