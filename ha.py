import subprocess
import sys
import os
import asyncio

# ===== تنزيل المكتبات تلقائياً =====
def install_packages():
    packages = ["flask", "python-telegram-bot==21.6", "requests"]
    for package in packages:
        pkg_name = package.split("==")[0].replace("-", "_")
        try:
            __import__(pkg_name)
        except ImportError:
            print(f"📦 جاري تثبيت {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== الإعدادات =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ لازم تحط BOT_TOKEN في Environment Variables")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثال: https://your-app.onrender.com
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 أهلاً {user.first_name}!\n"
        f"✅ البوت شغال تمام.\n"
        f"🆔 الـ ID بتاعك: `{user.id}`",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n"
        "/ping - اختبار السرعة"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")

# ===== تهيئة البوت =====
telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_cmd))
telegram_app.add_handler(CommandHandler("ping", ping))

# ===== مسارات Flask =====
@app.route("/")
def home():
    return "<h1>🤖 Bot is running!</h1>"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok", 200

# ===== تشغيل السيرفر =====
def setup_webhook():
    if WEBHOOK_URL:
        url = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        import requests
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}")
        print(f"🔗 Webhook setup: {r.json()}")

if __name__ == "__main__":
    setup_webhook()
    print(f"🚀 Server running on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
