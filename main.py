import os
import sys
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

# Validate required environment variables
if not TELEGRAM_TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN не установлен в переменных очережения")
    sys.exit(1)

# Initialize Supabase (optional)
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Supabase успешно инициализирован")
    except Exception as e:
        logging.error(f"Ошибка инициализации Supabase: {e}")
        logging.warning("Функциональность Supabase будет недоступна")
else:
    logging.warning("SUPABASE_URL или SUPABASE_KEY не установлены. Функциональность Supabase будет недоступна.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Log user to Supabase and send welcome message.\"\"\"
    user = update.effective_user

    # Register user in Supabase (if available)
    if supabase:
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
    else:
        logging.warning("Supabase не настроен, пропуск логирования пользователя")

    await update.message.reply_text(f"Привет, {user.first_name}! Я бот 'Понг-Пинг'. Напиши мне 'понг', и я отвечу 'пинг'!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Respond 'пинг' to 'понг'.\"\"\"
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
    
    MODE = os.getenv("MODE", "polling")
    
    if MODE == "webhook":
        PORT = int(os.environ.get("PORT", 8080))
        logging.info(f"Starting in WEBHOOK mode on port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=os.getenv("WEBHOOK_URL")
        )
    else:
        logging.info("Starting in POLLING mode")
        print("Bot is starting (polling mode)...")
        application.run_polling()
