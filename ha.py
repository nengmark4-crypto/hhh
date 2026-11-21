from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
import urllib.request
import urllib.parse

# ===== الإعدادات =====
BOT_TOKEN = "8248984044:AAFJvizVHKO9NzsFMvuHd84cxbPKZ17RMvw"
PORT = 5000
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== إرسال رسالة =====
def send_message(chat_id, text):
    url = f"{API}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode()
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

# ===== استقبال الرسائل =====
def poll_updates():
    last_update_id = 0
    print("🤖 البوت بدأ يستقبل الرسائل...")
    while True:
        try:
            url = f"{API}/getUpdates?offset={last_update_id + 1}&timeout=30"
            with urllib.request.urlopen(url, timeout=40) as resp:
                data = json.loads(resp.read().decode())

            if data.get("ok"):
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    message = update.get("message")
                    if not message:
                        continue

                    text = message.get("text", "")
                    chat_id = message["chat"]["id"]
                    user_name = message["from"].get("first_name", "صديقي")

                    print(f"📩 رسالة من {user_name}: {text}")

                    if text == "/start":
                        send_message(chat_id,
                            f"👋 أهلاً {user_name}!\n"
                            f"✅ البوت شغال تمام.\n"
                            f"🆔 الـ ID بتاعك: {chat_id}")
                    elif text == "/ping":
                        send_message(chat_id, "🏓 Pong!")
                    elif text == "/help":
                        send_message(chat_id, "📋 الأوامر:\n/start\n/ping\n/help")
                    else:
                        send_message(chat_id, f"استلمت رسالتك: {text}")

        except Exception as e:
            print(f"⚠️ خطأ: {e}")
            time.sleep(3)

# ===== سيرفر ويب للاستضافة =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>🤖 Bot is running!</h1>".encode("utf-8"))

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    threading.Thread(target=poll_updates, daemon=True).start()
    print(f"🚀 Server running on port {PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
