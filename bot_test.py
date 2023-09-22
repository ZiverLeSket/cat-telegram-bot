import logging
import mysql.connector
import os

from telegram.ext import (
    Application, 
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from message_handlers import(
    CustomContext,
    start,
    cat_pic,
    send_cat_to_check,
    button,
    get_full_archive_link
)

from imgur_lib import ImgurClient

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
SERVER_URL = os.getenv('SERVER_URL')
CHECKER_CHAT_ID = int(os.getenv('CHECKER_CHAT_ID'))
CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")
ALBUM_ID = os.getenv("ALBUM_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    client = ImgurClient(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)

    context_types = ContextTypes(context=CustomContext)

    application = (Application.builder().token(TOKEN).context_types(context_types).build())

    application.bot_data["url"] = SERVER_URL
    application.bot_data["admin_chat_id"] = ADMIN_CHAT_ID
    application.bot_data["checker_chat_id"] = CHECKER_CHAT_ID
    application.bot_data["client"] = client
    application.bot_data["album_id"] = ALBUM_ID
    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql124e45test",
        database="catrating",
    )

    application.bot_data["db_connect"] = mydb

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catpic", cat_pic))
    application.add_handler(CommandHandler("getcatarchive", get_full_archive_link))
    application.add_handler(MessageHandler(filters.PHOTO, send_cat_to_check))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()