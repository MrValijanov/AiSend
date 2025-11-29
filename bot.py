import os
import logging

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# 🔗 Bu yerga o'z web-app URL'ingni qo'y (https bo'lishi shart)
WEBAPP_URL = "https://example.com/aisend-demo"

# --- Logging sozlamalari ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    greeting = (
        f"Salom, {user.full_name or 'foydalanuvchi'}! 👋\n\n"
        "AiSend mini appni ochish uchun tugmani bosing 👇"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="AiSend mini app ni ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )

    # reply_markup = InlineKeyboardMarkup → knopka xabar tagida bo'ladi
    await update.message.reply_text(greeting, reply_markup=keyboard)


# --- /stats komandasi (hozircha demo) ---
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📊 Demo /stats: haqiqiy statistika hali ulanmagan.\n"
        "Hozircha faqat bot ishlayotganini tekshirayotganmiz. 🙂"
    )


def main() -> None:
    # Tokenni faqat env'dan olamiz
    token = os.getenv("AISEND_BOT_TOKEN")

    if not token:
        # Ataylab qattiq xato: token yo'q bo'lsa, darrov bilinadi
        raise RuntimeError(
            "AISEND_BOT_TOKEN env o'rnatilmagan.\n"
            "Termux'da quyidagi qatorni tekshiring:\n"
            "  echo \"export AISEND_BOT_TOKEN='YANGI_TOKEN'\" >> ~/.bashrc\n"
            "keyin: source ~/.bashrc"
        )

    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    logger.info("AiSend bot ishga tushdi...")
    application.run_polling()


if __name__ == "__main__":
    main()
