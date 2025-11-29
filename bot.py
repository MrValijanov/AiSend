import os
import logging
from urllib.parse import urlencode

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Tokenni faqat Termux environment’dan olamiz
BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("❌ BOT TOKEN TOPILMADI. Termuxga export qilmagansiz.")

WEB_APP_URL = "https://ai-send.vercel.app"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    params = urlencode({
        "tg_id": user.id,
        "tg_name": user.first_name or "",
        "tg_username": user.username or ""
    })

    open_url = f"{WEB_APP_URL}?{params}"

    keyboard = [
        [
            InlineKeyboardButton(
                "AiSend mini app ni ochish",
                web_app=WebAppInfo(url=open_url)
            )
        ]
    ]

    await update.message.reply_text(
        f"Salom, {user.first_name}! AiSend mini appni oching 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == "__main__":
    main()
