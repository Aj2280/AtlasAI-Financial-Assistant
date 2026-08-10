import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"healthy","service":"Atlas AI Financial Analyst","bot":"@Atlas39bot"}')

    def log_message(self, format, *args):
        # Suppress noisy HTTP health log entries
        pass

def start_health_server():
    """Starts background HTTP server so Render Web Service health checks succeed immediately."""
    port = int(os.environ.get("PORT", 8000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        log.info(f"Render health server active on 0.0.0.0:{port}...")
        server.serve_forever()
    except Exception as e:
        log.warning(f"Could not bind health server on port {port}: {e}")

def main():
    repo.init_db()
    
    # Start health check server in background thread for Render
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

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

    # Register Schedulers
    register_jobs(app)

    log.info("🚀 Atlas Telegram Bot LIVE & polling on @Atlas39bot...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
