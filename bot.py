from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# =========================
# SOZLAMALAR
# =========================

TOKEN = "8896646163:AAGcPP1zyZnMRzKM3Tn7zTSj53NIxcglTQ0"

ADMIN_ID = 6913817625


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["💰 Pul solish"],
        ["💸 Pul yechish"],
        ["📱 Ilova haqida"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "Xush kelibsiz!\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=markup
    )


# =========================
# PUL SOLISH
# =========================

async def pul_solish(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💰 Pul solish\n\n"
        "To‘lov usulini tanlang 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Click", callback_data="click")],
            [InlineKeyboardButton("💳 Payme", callback_data="payme")],
            [InlineKeyboardButton("💳 Uzcard", callback_data="uzcard")],
            [InlineKeyboardButton("💳 HUMO", callback_data="humo")]
        ])
    )


# =========================
# PUL YECHISH
# =========================

async def pul_yechish(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💸 Pul yechish\n\n"
        "Yechmoqchi bo‘lgan summangizni yozing."
    )


# =========================
# ILOVA HAQIDA
# =========================

async def ilova_haqida(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📱 Ilova haqida\n\n"
        "Xizmatimizdan foydalanish uchun "
        "kerakli bo‘limni tanlang."
    )


# =========================
# TO‘LOV TUGMALARI
# =========================

async def payment_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    method = query.data

    names = {
        "click": "💳 Click",
        "payme": "💳 Payme",
        "uzcard": "💳 Uzcard",
        "humo": "💳 HUMO"
    }

    method_name = names.get(method, method)

    user = update.effective_user

    await query.message.reply_text(
        f"Siz {method_name} ni tanladingiz. ✅"
    )

    # Adminga xabar
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 Yangi to‘lov so‘rovi!\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"💳 To‘lov usuli: {method_name}"
        )
    )


# =========================
# FOYDALANUVCHI XABARI
# =========================

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    text = update.message.text

    # Menyu tugmalari
    if text == "💰 Pul solish":
        await pul_solish(update, context)
        return

    if text == "💸 Pul yechish":
        await pul_yechish(update, context)
        return

    if text == "📱 Ilova haqida":
        await ilova_haqida(update, context)
        return

    # Oddiy xabarni adminga yuborish
    reply_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💬 Javob berish",
                callback_data=f"reply_{user.id}"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 Yangi xabar!\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n\n"
            f"💬 Xabar:\n{text}"
        ),
        reply_markup=reply_button
    )

    await update.message.reply_text(
        "✅ Xabaringiz qabul qilindi."
    )


# =========================
# FOYDALANUVCHI RASMI
# =========================

async def user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    caption = update.message.caption or "Izoh yo‘q"

    reply_button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💬 Javob berish",
                callback_data=f"reply_{user.id}"
            )
        ]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=(
            "📷 Yangi rasm!\n\n"
            f"👤 Ism: {user.full_name}\n"
            f"🆔 ID: {user.id}\n\n"
            f"💬 Izoh:\n{caption}"
        ),
        reply_markup=reply_button
    )

    await update.message.reply_text(
        "✅ Rasm qabul qilindi."
    )


# =========================
# ADMIN "JAVOB BERISH" TUGMASI
# =========================

async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    # Faqat admin ishlata oladi
    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "❌ Sizda ruxsat yo‘q.",
            show_alert=True
        )
        return

    # Foydalanuvchi ID sini olish
    user_id = int(query.data.split("_")[1])

    # Kimga javob berilishini saqlash
    context.user_data["reply_to_user"] = user_id

    await query.message.reply_text(
        "✍️ Javobingizni yozing.\n\n"
        "Men uni avtomatik ravishda "
        "foydalanuvchiga yuboraman."
    )


# =========================
# ADMIN JAVOBINI YUBORISH
# =========================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Faqat admin
    if update.effective_user.id != ADMIN_ID:
        return

    # Javob beriladigan foydalanuvchi
    user_id = context.user_data.get("reply_to_user")

    # Agar javob rejimi yo‘q bo‘lsa
    if not user_id:
        return

    text = update.message.text

    try:

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "📩 Admin javobi:\n\n"
                f"{text}"
            )
        )

        await update.message.reply_text(
            "✅ Javob foydalanuvchiga yuborildi."
        )

        # Javob rejimini tugatish
        del context.user_data["reply_to_user"]

    except Exception:

        await update.message.reply_text(
            "❌ Javob yuborilmadi.\n\n"
            "Foydalanuvchi botni bloklagan "
            "yoki bot bilan hali /start qilmagan."
        )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

app = Application.builder().token(TOKEN).build()


# /start
app.add_handler(
    CommandHandler("start", start)
)


# Adminning "Javob berish" tugmasi
app.add_handler(
    CallbackQueryHandler(
        reply_button,
        pattern=r"^reply_\d+$"
    )
)


# Rasmlar
app.add_handler(
    MessageHandler(
        filters.PHOTO,
        user_photo
    )
)


# Admin yozgan javoblar
app.add_handler(
    MessageHandler(
        filters.User(ADMIN_ID)
        & filters.TEXT
        & ~filters.COMMAND,
        admin_reply
    )
)


# Foydalanuvchi matnlari
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        user_message
    )
)


print("Bot ishga tushdi...")

app.run_polling()