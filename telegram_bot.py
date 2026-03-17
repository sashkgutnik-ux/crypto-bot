from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8691332194:AAHFRkiNxpWMW9FSNuZbjt35BvV7EqkJKFQ"


bot_running = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🚀 Start Bot"],
        ["🛑 Stop Bot"],
        ["📊 Status"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🤖 Crypto Trading Bot\n\nChoose action:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global bot_running

    text = update.message.text

    if text == "🚀 Start Bot":

        bot_running = True
        await update.message.reply_text("🚀 Bot started")

    elif text == "🛑 Stop Bot":

        bot_running = False
        await update.message.reply_text("🛑 Bot stopped")

    elif text == "📊 Status":

        status = "Running" if bot_running else "Stopped"

        await update.message.reply_text(
            f"📊 Bot status: {status}"
        )


def run_telegram_bot():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Telegram bot started")

    app.run_polling()
