import json
import os
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if not BOT_TOKEN or not WEBAPP_URL:
    print("Set TELEGRAM_BOT_TOKEN and WEBAPP_URL environment variables.", file=sys.stderr)
    sys.exit(1)

if not WEBAPP_URL.startswith("https://"):
    print("WEBAPP_URL must be HTTPS for Telegram Mini Apps.", file=sys.stderr)
    sys.exit(1)

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def api(method, payload=None, timeout=60):
    data = json.dumps(payload or {}).encode("utf-8")
    req = Request(
        f"{API}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(result)
    return result.get("result")


def setup_menu_button():
    api(
        "setChatMenuButton",
        {
            "menu_button": {
                "type": "web_app",
                "text": "Открыть планер",
                "web_app": {"url": WEBAPP_URL},
            }
        },
    )


def send_start(chat_id):
    api(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": (
                "Привет! Это Джон Кремль - Ваш AI-помощник. "
                "Открой планер кнопкой ниже и задай вопрос в AI-чате."
            ),
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "🚀 Открыть Web App",
                            "web_app": {"url": WEBAPP_URL},
                        }
                    ]
                ]
            },
        },
    )


def main():
    me = api("getMe")
    print(f"Bot: @{me.get('username')} ({me.get('id')})")
    print(f"Web App: {WEBAPP_URL}")
    setup_menu_button()
    print("Menu button configured. Polling started.")

    offset = None
    while True:
        try:
            payload = {"timeout": 50, "allowed_updates": ["message"]}
            if offset is not None:
                payload["offset"] = offset
            updates = api("getUpdates", payload, timeout=60)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                text = (message.get("text") or "").strip()
                if chat.get("type") == "private" and text.startswith("/start"):
                    send_start(chat["id"])
        except KeyboardInterrupt:
            print("\nStopped.")
            return
        except Exception as exc:
            print(f"Bot error: {exc}", file=sys.stderr)
            time.sleep(3)


if __name__ == "__main__":
    main()
