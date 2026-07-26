import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from utils.logger import logger
from utils.link_extractor import extract_telegram_links
from database.db_manager import db
from config import IGNORE_ADMINS

async def is_user_exempt(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    chat_id = update.effective_chat.id
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status == "creator":
            return True
        if IGNORE_ADMINS and member.status == "administrator":
            return True
    except TelegramError:
        pass
    return False

async def delete_and_warn(update: Update, context: ContextTypes.DEFAULT_TYPE, warning_text: str, delay: int = 5):
    try:
        await update.message.delete()
        warning_msg = await update.message.reply_text(warning_text)
        await asyncio.sleep(delay)
        await warning_msg.delete()
    except TelegramError as e:
        logger.error(f"Failed to delete/warn: {e}")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat
    text = update.message.text

    if await is_user_exempt(update, context, user.id):
        return

    links = extract_telegram_links(text)
    
    # Feature 2: Bulk Link Protection
    if len(links) > 1:
        logger.info(f"Bulk links detected from {user.id}")
        await delete_and_warn(
            update, context, 
            "⚠️ Please send one Telegram link per message.\nOnly one group per message is allowed.\nDo not send multiple links together.", 
            delay=7
        )
        return

    # Feature 1: Duplicate Link Detection
    if len(links) == 1:
        link_id = links[0]
        if await db.link_exists(link_id):
            logger.info(f"Duplicate link removed: {link_id}")
            await delete_and_warn(update, context, "❌ Duplicate link removed.", delay=3)
        else:
            await db.store_link(link_id)
            await db.update_user_activity(user.id, chat.id, user.username or user.first_name)
            logger.info(f"New link stored from {user.id}")
          
