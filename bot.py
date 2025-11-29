import os

from telegram import (
    Update,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)


# ⚠️ Bu yerga O'ZINGNING mini-app URL'ingni qo'y
WEBAPP_URL = "https://example.com"  # masalan: https://aisend-demo.vercel.app/


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat

    keyboard = [
        [
            KeyboardButton(
                text="AiSend mini app ni ochish",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=chat.id,
        text=f"Salom, {chat.first_name or 'foydalanuvchi'}! 👋\n\n"
             f"AiSend mini appni ochish uchun pastdagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
        ),
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Hozircha oddiy demo
    await update.message.reply_text("Hozircha demo stats: 0 ta foydalanuvchi 🙂")


def main() -> None:
    token = os.environ.get("AISEND_BOT_TOKEN")
    if not token:
        raise RuntimeError("AISEND_BOT_TOKEN env topilmadi. Termuxda token o'rnatilmagan.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    print("🚀 AiSend bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
