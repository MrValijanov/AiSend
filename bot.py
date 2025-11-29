#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AISEND / AI EXCHANGE – PRO DEMO BOT

Funksiyalar:
- /rates, /convert
- /spread, /simulate
- /crypto, /stock
- /bills (Chegarasiz to'lovlar demo)
- /vip, /stats
"""

import logging
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from telegram.error import TimedOut

# ========== CONFIG ==========

# Token kod ichida emas, muhit o'zgaruvchisidan olinadi
TOKEN = os.getenv("AISEND_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "AISEND_BOT_TOKEN muhit o'zgaruvchisi topilmadi.\n"
        "Termux ~/.bashrc ichiga quyidagini qo'sh:\n"
        "export AISEND_BOT_TOKEN='123:ABC...SENING_TOKENING'"
    )

SITE_URL = "https://ai-send.vercel.app"
PROJECT_NAME = "AISEND / AI EXCHANGE"

ADMIN_IDS = [123456789]     # o'z ID'ingni qo'y
VIP_USER_IDS = [123456789]  # VIP userlar ID'lari

# ========== LOGGING ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== DEMO MA'LUMOTLAR (mock) ==========

BASE_RATES = {
    ("UZS", "KZT"): 0.038,
    ("KZT", "UZS"): 26.3,
    ("UZS", "KGS"): 0.0073,
    ("KGS", "UZS"): 137.0,
    ("KZT", "KGS"): 0.19,
    ("KGS", "KZT"): 5.2,
    ("USD", "KZT"): 480.0,
    ("USD", "UZS"): 13000.0,
    ("KZT", "USD"): 1 / 480.0,
    ("UZS", "USD"): 1 / 13000.0,
}

CRYPTO_RATES = {
    "USDT_KZT": 482.0,
    "USDT_UZS": 13200.0,
}

STOCK_DEMO = {
    "AAPL": 230.50,
    "TSLA": 210.10,
    "NVDA": 1180.35,
}

STATS = {
    "users": set(),
    "total_converts": 0,
    "total_simulations": 0,
    "total_requests": 0,
    "crypto_views": 0,
    "stock_views": 0,
    "bills_views": 0,
}

# ========== UTIL FUNKSIYALAR ==========


def register_request(update: Update):
    """Har bir so'rovda statistikani yangilaydi."""
    chat_id = update.effective_chat.id
    STATS["users"].add(chat_id)
    STATS["total_requests"] += 1


def get_rate(from_ccy: str, to_ccy: str):
    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()
    if from_ccy == to_ccy:
        return 1.0
    return BASE_RATES.get((from_ccy, to_ccy))


def convert_amount(amount: float, from_ccy: str, to_ccy: str):
    rate = get_rate(from_ccy, to_ccy)
    if rate is None:
        return None, None
    result = amount * rate
    return result, rate


def format_money(value: float, ccy: str) -> str:
    if value >= 1_000_000:
        return f"{value:,.0f} {ccy}"
    return f"{value:,.2f} {ccy}"


def build_rates_text() -> str:
    lines = [
        "📊 *Demo kurslar*",
        "",
        f"1 UZS → KZT ≈ {BASE_RATES.get(('UZS', 'KZT'))}",
        f"1 KZT → UZS ≈ {BASE_RATES.get(('KZT', 'UZS'))}",
        f"1 UZS → KGS ≈ {BASE_RATES.get(('UZS', 'KGS'))}",
        f"1 KGS → UZS ≈ {BASE_RATES.get(('KGS', 'UZS'))}",
        "",
        f"1 USD → KZT ≈ {BASE_RATES.get(('USD', 'KZT'))}",
        f"1 USD → UZS ≈ {BASE_RATES.get(('USD', 'UZS'))}",
        "",
        "_Eslatma: bu faqat demo kurslar. Real rejimda bu joyga bank yoki P2P API ulanadi._",
    ]
    return "\n".join(lines)


def build_spread_text() -> str:
    """Bank vs P2P vs AISEND taqqoslash (demo)."""
    bank_usd_kzt = 478.0
    p2p_usd_kzt = CRYPTO_RATES["USDT_KZT"]
    aisend_usd_kzt = 479.5

    amount_usd = 1000
    bank_kzt = amount_usd * bank_usd_kzt
    p2p_kzt = amount_usd * p2p_usd_kzt
    aisend_kzt = amount_usd * aisend_usd_kzt

    lines = [
        "📡 *Live Spread Monitor (DEMO)*",
        "",
        f"Bank USD/KZT: *{bank_usd_kzt}*",
        f"P2P  USD/KZT: *{p2p_usd_kzt}*",
        f"AISEND USD/KZT: *{aisend_usd_kzt}*",
        "",
        f"1000 USD misolida:",
        f"- Bank : {format_money(bank_kzt, 'KZT')}",
        f"- P2P  : {format_money(p2p_kzt, 'KZT')}",
        f"- AISEND: {format_money(aisend_kzt, 'KZT')}",
        "",
        f"AISEND vs Bank farq: *{aisend_kzt - bank_kzt:.0f} KZT* foyda",
        f"AISEND vs P2P  farq: *{aisend_kzt - p2p_kzt:.0f} KZT* foyda",
        "",
        "_Real rejimda bu yerga Binance P2P + bank API ulanadi._",
    ]
    return "\n".join(lines)


def simulate_transfer(amount: float, from_ccy: str, to_ccy: str) -> str:
    """Bank, crypto, AISEND uch xil yo'lni taqqoslaydi (demo)."""
    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()

    base_conv, base_rate = convert_amount(amount, from_ccy, to_ccy)
    if base_conv is None:
        return "Bu valyuta juftligi uchun demo kurs yo'q. Iltimos UZS, KZT, KGS, USD dan foydalaning."

    bank_fee = 0.015
    bank_result = base_conv * (1 - bank_fee)

    crypto_fee = 0.008
    crypto_result = base_conv * 1.003 * (1 - crypto_fee)

    aisend_fee = 0.007
    aisend_result = base_conv * 1.006 * (1 - aisend_fee)

    lines = [
        "🧮 *Pul o'tkazma simulyatori (DEMO)*",
        f"Asosiy yo'nalish: {format_money(amount, from_ccy)} → {to_ccy}",
        "",
        "Bank varianti (~1.5% fee):",
        f"- Natija: {format_money(bank_result, to_ccy)}",
        "",
        "Crypto varianti (~0.8% fee, kurs +0.3%):",
        f"- Natija: {format_money(crypto_result, to_ccy)}",
        "",
        "AISEND varianti (~0.7% fee, kurs +0.6%):",
        f"- Natija: {format_money(aisend_result, to_ccy)}",
        "",
        "👉 Faqat demo, lekin real hayotda ham maqsad shu: AISEND bo'yicha foyda maksimal bo'lishi.",
    ]
    return "\n".join(lines)


def build_crypto_demo_text() -> str:
    STATS["crypto_views"] += 1
    lines = [
        "⚡ *Crypto tezkor to'lovlar — DEMO*",
        "",
        "Hozircha demo rejimida quyidagi parametrlarga ega:",
        "- Tarmoq: *TRON (TRC20)*",
        "- Asosiy coin: *USDT*",
        "- Minimal summa: *10 USDT*",
        "- O'rtacha o'tkazma vaqti: *30–120 soniya*",
        "",
        "Demo kurslar:",
        f"- 1 USDT ≈ {CRYPTO_RATES['USDT_KZT']} KZT",
        f"- 1 USDT ≈ {CRYPTO_RATES['USDT_UZS']} UZS",
        "",
        "_Real ishga tushganda bu bo'limga wallet monitoring, tx status va avto-hisoblash funksiyalarini ulash mumkin._",
    ]
    return "\n".join(lines)


def build_stock_demo_text() -> str:
    STATS["stock_views"] += 1
    lines = [
        "📈 *Stock bo'limi — DEMO*",
        "",
        "Mashhur kompaniyalar bo'yicha demo narxlar:",
    ]
    for ticker, price in STOCK_DEMO.items():
        lines.append(f"- {ticker}: ~{price} USD")
    lines += [
        "",
        "_Keyin bu yerga real-time market API ulash mumkin._",
    ]
    return "\n".join(lines)


def build_bills_demo_text() -> str:
    """Chegarasiz to'lovlar konseptini tushuntiradi."""
    STATS["bills_views"] += 1
    lines = [
        "💡 *Chegarasiz to'lovlar (DEMO)*",
        "",
        "G'oya: chet elda yurgan foydalanuvchi AISEND ichidagi USZ balansidan foydalanib,",
        "O'zbekistondagi uy-ro'zg'or hisoblarini to'laydi:",
        "- Gaz",
        "- Suv",
        "- Svet",
        "- Mobil operatorlar",
        "- Internet",
        "",
        "Demo rejimi: hozircha bu yerda faqat konsept va tushuntirish bor.",
        "Real loyihada:",
        "- billing provayderlar API'lari",
        "- limitlar va tariflar",
        "- KYC/KYB talablari paydo bo'ladi.",
        "",
        "🔜 Kelajakda /bills bo'limida to'lov oqimi, kvitansiya va status ham chiqadi.",
    ]
    return "\n".join(lines)
# ========== TELEGRAM HANDLERLAR – 1-qism ==========


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["/rates", "/convert"],
        ["/spread", "/simulate"],
        ["/crypto", "/stock"],
        ["/bills", "/stats"],
        ["/help"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext):
    register_request(update)
    user = update.effective_user
    name = user.first_name or "do'stim"

    text = (
        f"Salom, {name}! 👋\n\n"
        f"Bu yerda *{PROJECT_NAME}* demo bot ishlayapti.\n"
        f"🌐 Web mini-app: {SITE_URL}\n\n"
        "Asosiy bo'limlar:\n"
        "• /rates – demo valyuta kurslari\n"
        "• /convert – konvertor (USD, UZS, KZT, KGS)\n"
        "• /spread – Live Spread Monitor\n"
        "• /simulate – pul o'tkazma simulyatori\n"
        "• /crypto – crypto tezkor to'lovlar (demo)\n"
        "• /stock – stock bo'limi (demo)\n"
        "• /bills – Chegarasiz to'lovlar (demo)\n"
        "• /stats – statistika\n"
        "• /help – qo'llanma\n\n"
        f"Web versiyani ko'rish: {SITE_URL}"
    )
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def help_command(update: Update, context: CallbackContext):
    register_request(update)
    text = (
        "ℹ️ *Qo'llanma*\n\n"
        f"Web mini-app: {SITE_URL}\n\n"
        "/rates – kurslar\n"
        "/convert amount FROM TO – konvertor\n"
        "   Masalan: `/convert 1000000 UZS KZT`\n\n"
        "/spread – Live Spread Monitor\n\n"
        "/simulate amount FROM TO – o'tkazma simulyatori\n"
        "   Masalan: `/simulate 2000000 KZT UZS`\n\n"
        "/crypto – crypto bo'limi (demo)\n"
        "/stock – stock bo'limi (demo)\n"
        "/bills – Chegarasiz to'lovlar bo'limi (demo)\n"
        "/vip – VIP panel (faqat maxsus ID lar)\n"
        "/stats – umumiy statistika\n"
    )
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def rates_command(update: Update, context: CallbackContext):
    register_request(update)
    text = build_rates_text()
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def convert_command(update: Update, context: CallbackContext):
    register_request(update)
    args = context.args

    if len(args) != 3:
        usage = (
            "🧮 Konvertor ishlatish uchun format:\n"
            "`/convert amount FROM TO`\n"
            "Masalan:\n"
            "`/convert 1000000 UZS KZT`"
        )
        update.message.reply_text(usage, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

    amount_str, from_ccy, to_ccy = args
    try:
        amount = float(amount_str.replace(",", ""))
    except ValueError:
        update.message.reply_text("Summani to'g'ri kiriting. Masalan: `1000000`", parse_mode="Markdown")
        return

    result, rate = convert_amount(amount, from_ccy, to_ccy)
    if result is None:
        update.message.reply_text(
            "Bu juftlik bo'yicha demo kurs topilmadi. Iltimos UZS, KZT, KGS, USD dan foydalaning.",
            reply_markup=get_main_keyboard(),
        )
        return

    STATS["total_converts"] += 1
    text = (
        "✅ *Konvertatsiya natijasi:*\n\n"
        f"{format_money(amount, from_ccy.upper())} → {format_money(result, to_ccy.upper())}\n"
        f"Kurs: 1 {from_ccy.upper()} = {rate:.6f} {to_ccy.upper()}\n\n"
        "_Eslatma: bu demo kurs. Real versiyada bu yerga API ulanadi._"
    )
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def spread_command(update: Update, context: CallbackContext):
    register_request(update)
    text = build_spread_text()
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def simulate_command(update: Update, context: CallbackContext):
    register_request(update)
    args = context.args

    if len(args) != 3:
        usage = (
            "🧮 Simulyator uchun format:\n"
            "`/simulate amount FROM TO`\n"
            "Masalan:\n"
            "`/simulate 2000000 KZT UZS`"
        )
        update.message.reply_text(usage, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return

    amount_str, from_ccy, to_ccy = args
    try:
        amount = float(amount_str.replace(",", ""))
    except ValueError:
        update.message.reply_text("Summani to'g'ri kiriting. Masalan: `2000000`", parse_mode="Markdown")
        return

    STATS["total_simulations"] += 1
    text = simulate_transfer(amount, from_ccy, to_ccy)
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
# ========== TELEGRAM HANDLERLAR – 2-qism ==========


def crypto_command(update: Update, context: CallbackContext):
    register_request(update)
    text = build_crypto_demo_text()
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def stock_command(update: Update, context: CallbackContext):
    register_request(update)
    text = build_stock_demo_text()
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def bills_command(update: Update, context: CallbackContext):
    register_request(update)
    text = build_bills_demo_text()
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def vip_command(update: Update, context: CallbackContext):
    register_request(update)
    user_id = update.effective_user.id

    if user_id not in VIP_USER_IDS and user_id not in ADMIN_IDS:
        update.message.reply_text(
            "🚫 VIP panel faqat tasdiqlangan foydalanuvchilar uchun.\n"
            "Agar qo'shilmoqchi bo'lsang, admin bilan bog'lan.",
            reply_markup=get_main_keyboard(),
        )
        return

    text = (
        "👑 *AISEND VIP PANEL (DEMO)*\n\n"
        "Kelajakdagi imkoniyatlar:\n"
        "• Maxsus (yaxshiroq) kurslar\n"
        "• Yirik summalar uchun alohida limitlar\n"
        "• Tezkor tasdiqlash (priority queue)\n"
        "• Shaxsiy menedjer\n\n"
        f"Web versiya uchun: {SITE_URL}/vip (rejalashtirilgan)"
    )
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def stats_command(update: Update, context: CallbackContext):
    register_request(update)
    users_count = len(STATS["users"])
    text = (
        "📊 *Bot statistikasi (RAM ichida, demo):*\n\n"
        f"• Unikal foydalanuvchilar: *{users_count}*\n"
        f"• Jami requestlar: *{STATS['total_requests']}*\n"
        f"• Konvertor: *{STATS['total_converts']}* marta\n"
        f"• Simulyator: *{STATS['total_simulations']}* marta\n"
        f"• Crypto bo'limi: *{STATS['crypto_views']}* marta\n"
        f"• Stock bo'limi: *{STATS['stock_views']}* marta\n"
        f"• Chegarasiz to'lovlar: *{STATS['bills_views']}* marta\n\n"
        "_Eslatma: bu statistika bot qayta ishga tushirilganda o'chib ketadi. "
        "Keyinchalik bu yerga database ulash mumkin._"
    )
    update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())


def fallback_message(update: Update, context: CallbackContext):
    """Noma'lum matnlar uchun default javob."""
    register_request(update)
    text = (
        "Menyudan biror komandani tanla yoki /help buyrug'ini kiriting 😊\n\n"
        "Masalan:\n"
        "• /rates\n"
        "• /convert 1000000 UZS KZT\n"
        "• /spread\n"
        "• /simulate 2000000 KZT UZS\n"
    )
    update.message.reply_text(text, reply_markup=get_main_keyboard())


def main():
    # sekin tarmoq uchun timeoutsni kattaroq qilamiz
    request_kwargs = {
        "read_timeout": 30,
        "connect_timeout": 30,
    }

    updater = Updater(TOKEN, use_context=True, request_kwargs=request_kwargs)
    dp = updater.dispatcher

    # Komanda handlerlar
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("rates", rates_command))
    dp.add_handler(CommandHandler("convert", convert_command))
    dp.add_handler(CommandHandler("spread", spread_command))
    dp.add_handler(CommandHandler("simulate", simulate_command))
    dp.add_handler(CommandHandler("crypto", crypto_command))
    dp.add_handler(CommandHandler("stock", stock_command))
    dp.add_handler(CommandHandler("bills", bills_command))
    dp.add_handler(CommandHandler("vip", vip_command))
    dp.add_handler(CommandHandler("stats", stats_command))

    # Oddiy matnlar
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, fallback_message))

    logger.info("AISEND demo bot ishga tushmoqda...")

    while True:
        try:
            updater.start_polling(clean=True)
            logger.info("Polling boshlandi.")
            updater.idle()
            break  # hammasi joyida bo'lsa, while'dan chiqamiz
        except TimedOut:
            logger.warning("Telegramga ulanishda timeout bo'ldi. Qaytadan urinaman...")
            continue
        except Exception as e:
            logger.exception("Kutilmagan xato: %s", e)
            break


if __name__ == "__main__":
    main()
