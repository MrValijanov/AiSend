#!/usr/bin/env python3
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

# 🔐 Token faqat environmentdan olinadi
BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "AISEND_BOT_TOKEN topilmadi. Termux’da export AISEND_BOT_TOKEN=... qilib qo‘yganingni tekshir."
    )

WEB_APP_BASE_URL = "https://ai-send.vercel.app"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    first = (user.first_name or "").strip()
    last = (user.last_name or "").strip()
    full_name = (first + " " + last).strip() or "foydalanuvchi"
    username = user.username or ""
    tg_id = user.id

    params = {
        "tg_id": str(tg_id),
        "tg_name": full_name,
        "tg_username": username,
    }
    full_url = f"{WEB_APP_BASE_URL}?{urlencode(params)}"

    text = (
        f"Salom, {full_name}! 👋\n\n"
        "AiSend mini appni ochish uchun tugmani bosing 👇"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "AiSend mini app ni ochish",
                web_app=WebAppInfo(url=full_url),
            )
        ]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    logger.info("Start yubordi: id=%s, name=%s, username=%s", tg_id, full_name, username)


def main() -> None:
    logger.info("AiSend bot ishga tushmoqda...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("AiSend bot ishga tushdi. /start kutyapmiz...")
    app.run_polling()


if __name__ == "__main__":
    main()
