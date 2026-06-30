import threading
import os
import sys
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "News Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    from bot import main
    main()
