# bot.py
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import settings
from handlers.start import start, cb_router

def main():
    if not settings.TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is not set in .env")

    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb_router))

    print("Bot started ✓")
    # Блочний запуск — сам керує лупом всередині
    app.run_polling()

if __name__ == "__main__":
    main()
