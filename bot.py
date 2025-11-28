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

# ⬇️ Bu yerga o'zingning bot tokeningni qo'y
BOT_TOKEN = "8209682714:AAGugkQ5V9XMch4FENouU4zj6ekwjQN4npU"

# Web app manzili (Vercel)
WEB_APP_BASE_URL = "https://ai-send.vercel.app"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Foydalanuvchi ma'lumotlarini URL query qilib yuboramiz
    params = urlencode(
        {
            "tg_id": user.id,
            "tg_name": (user.first_name or "").strip(),
            "tg_username": (user.username or "").strip(),
        }
    )

    full_url = f"{WEB_APP_BASE_URL}?{params}"

    keyboard = [
        [
            InlineKeyboardButton(
                "AiSend mini app ni ochish",
                web_app=WebAppInfo(url=full_url),
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Salom, {user.first_name or 'foydalanuvchi'}! 👋\n\n" \
           "AiSend mini appni ochish uchun tugmani bosing 👇"

    # Muhim qism: /start ga aniq javob berish
    await update.message.reply_text(text, reply_markup=reply_markup)


def main():
    print("Aisend bot ishga tushdi...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start komandasi uchun handler
    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == "__main__":
    main()
