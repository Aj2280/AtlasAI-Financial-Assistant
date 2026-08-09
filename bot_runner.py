import os
import sys
import logging

sys.path.insert(0, os.path.dirname(__file__))

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from backend.bot import handlers
from backend.scheduler.jobs import register_jobs
from backend.db import repo

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
log = logging.getLogger("atlas_bot_runner")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8834152991:AAH5aL2O-GhH18GOEjyPkLP_f7gySVkPFM0").strip()

def main():
    repo.init_db()
    log.info("Initializing Atlas Telegram Bot (@Atlas39bot)...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register Telegram handlers
    app.add_handler(CommandHandler("start", handlers.on_start))
    app.add_handler(CommandHandler("watchlist", handlers.on_watchlist))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.on_text))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handlers.on_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handlers.on_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handlers.on_document))
    app.add_error_handler(handlers.on_error)

    # Register Proactive Schedulers
    register_jobs(app)

    log.info("🚀 Atlas Telegram Bot LIVE & polling on @Atlas39bot...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
