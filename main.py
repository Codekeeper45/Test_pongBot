import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log user to Supabase and send welcome message."""
    user = update.effective_user
    
    # Register user in Supabase
    try:
        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        # Use upsert to handle returning users
        supabase.table("users").upsert(data).execute()
        logging.info(f"User {user.id} logged to Supabase.")
    except Exception as e:
        logging.error(f"Error logging user to Supabase: {e}")

    await update.message.reply_text(f"Привет, {user.first_name}! Я бот 'Понг-Пинг'. Напиши мне 'понг', и я отвечу 'пинг'!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond 'пинг' to 'понг'."""
    text = update.message.text.lower().strip()
    if text == "понг":
        await update.message.reply_text("пинг")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        exit(1)
        
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    print("Bot is starting...")
    application.run_polling()
