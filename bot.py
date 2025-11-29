import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("AISEND_BOT_TOKEN")

WEBAPP_URL = "https://ai-send.vercel.app"   # <-- FAQAT SHU!!! 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("AiSend mini app ni ochish", web_app=WebAppInfo(WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=f"Salom, {update.effective_user.first_name}! 👋\n\n"
             f"AiSend mini appni ochish uchun tugmani bosing 👇",
        reply_markup=reply_markup
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Statistika hozircha mavjud emas.")

def main():
    print("🚀 AiSend bot ishga tushdi...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.run_polling()

if __name__ == "__main__":
    main()
