import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")

MAIN_APP_URL = "https://mrvalijanov.github.io/AiSend/"  # <-- SENING MINI APP URLING

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f"Salom, {user.full_name}! 👋\n\n"
        "AiSend mini appni ochish uchun tugmani bosing 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("AiSend mini app ni ochish", url=MAIN_APP_URL)]
        ])
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Hozircha statistik ma’lumot yo‘q.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    logging.info("🚀 AiSend bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
