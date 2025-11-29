import os
import logging

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# --- Logging (info loglarni ko‘rish uchun) ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Token faqat environment’dan olinadi ---
BOT_TOKEN = os.getenv("AISEND_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "AISEND_BOT_TOKEN environment o'zgaruvchisi topilmadi. "
        "Termux'da tokenni ~/.bashrc ichida export qilganingga ishonch hosil qil."
    )


# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /start komandasi uchun handler """
    user = update.effective_user

    greeting = (
        f"Salom, {user.first_name or 'AiSend foydalanuvchisi'}! 👋\n\n"
        "AiSend mini appni ochish uchun tugmani bosing 👇"
    )

    # Pastdagi KATTA reply keyboard (bitta qator, bitta tugma)
    keyboard = [
        [
            KeyboardButton(
                text="AiSend mini appni ochish",
                web_app={"url": "https://mrvalijanov.github.io/AiSend/"}
            )
        ]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await update.message.reply_text(
        greeting,
        reply_markup=reply_markup,
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /stats – hozircha oddiy demo """
    user = update.effective_user
    text = (
        "AiSend demo statistikasi (fake):\n"
        f"- Foydalanuvchi: {user.id}\n"
        "- Bugun qilingan operatsiyalar: 0\n"
        "- Bu faqat demo komandasi 😊"
    )
    await update.message.reply_text(text)


# --- Asosiy app ---

def main() -> None:
    """Botni ishga tushirish"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Komandalar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    logger.info("AiSend bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
