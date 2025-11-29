import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# 🚫 Hardcode yo‘q, faqat muhitdan o‘qiyapmiz
BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "AISEND_BOT_TOKEN muhit o'zgaruvchisi topilmadi. "
        "Termuxdagi ~/.bashrc ichiga export AISEND_BOT_TOKEN=... qo'shganingni tekshir."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    webapp_button = KeyboardButton(
        text="AiSend mini appni ochish",
        web_app=WebAppInfo(url="https://mrvalijanov.github.io/AiSend/"),
    )
    contact_button = KeyboardButton(
        text="Biz bilan aloqa",
        web_app=WebAppInfo(url="https://t.me/your_support_channel_here"),
    )

    keyboard = [[webapp_button], [contact_button]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await update.message.reply_text(
        text=f"Salom, {user.first_name or 'foydalanuvchi'}! 👋\n\n"
             "AiSend mini appni ochish uchun tugmani bosing 👇",
        reply_markup=reply_markup,
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
