import os
import logging
from telegram import Update, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token from environment
BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("❌ AISEND_BOT_TOKEN topilmadi! Termuxga token qo‘yilmadi.")

# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_html(
        f"Salom, <b>{user.first_name}</b>! 👋\n\n"
        f"AiSend mini appni ochish uchun tugmani bosing 👇",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "AiSend mini app ni ochish",
                    web_app=WebAppInfo(url="https://example.com")  # <-- SENING URLING
                )
            ]
        ])
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👀 Stats: Hozircha demo rejim.")

# --- RUN BOT ---

def main():
    logger.info("🚀 AiSend bot ishga tushdi...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    app.run_polling()

if __name__ == "__main__":
    main()
