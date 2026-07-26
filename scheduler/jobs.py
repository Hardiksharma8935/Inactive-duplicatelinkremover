import datetime
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database.db_manager import db
from utils.logger import logger

async def check_inactivity(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Running daily inactivity check...")
    users = await db.get_inactive_users()
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for user_id, chat_id, username, last_link_date in users:
        last_date = datetime.datetime.fromisoformat(last_link_date)
        days_inactive = (now - last_date).days
        
        try:
            if days_inactive == 4:
                await context.bot.send_message(chat_id, f"⚠️ @{username}, Day 4 Warning: You have been inactive. Post at least one Telegram group link. Otherwise you will be removed in 3 days.")
            elif days_inactive == 5:
                await context.bot.send_message(chat_id, f"⚠️ @{username}, Day 5 Warning: You will be removed in 2 days.")
            elif days_inactive == 6:
                await context.bot.send_message(chat_id, f"⚠️ @{username}, Final Warning: You will be removed tomorrow.")
            elif days_inactive >= 7:
                await context.bot.ban_chat_member(chat_id, user_id)
                await db.remove_user(user_id, chat_id)
                logger.info(f"Removed inactive user {user_id} from {chat_id}")
        except TelegramError as e:
            logger.error(f"Could not send reminder/ban for {user_id} in {chat_id}: {e}")
          
