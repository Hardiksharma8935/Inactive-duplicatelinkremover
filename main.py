import datetime
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from config import BOT_TOKEN, DATABASE_PATH
from database.db_manager import db
from handlers.message_handler import process_message
from scheduler.jobs import check_inactivity
from utils.logger import logger

async def on_startup(app):
    db.db_path = DATABASE_PATH
    await db.initialize()

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()
    
    # Message Routing
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    
    # Scheduling Inactivity Job (Runs daily at midnight UTC)
    app.job_queue.run_daily(check_inactivity, time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
