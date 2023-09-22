import asyncio
import logging
from http import HTTPStatus

import os
from dotenv import load_dotenv

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from telegram import Update
from telegram.ext import (
    Application, 
    ContextTypes,
    CommandHandler,
    TypeHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from message_handlers import(
    CustomContext,
    WebhookUpdate,
    start,
    cat_pic,
    send_cat_to_check,
    button,
    get_full_archive_link,
    webhook_update,
)


load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
SERVER_URL = os.getenv('SERVER_URL')
# CHECKER_CHAT_ID = int(os.getenv('CHECKER_CHAT_ID'))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main() -> None:
    
    port = 8000

    context_types = ContextTypes(context=CustomContext)
    
    application = (Application.builder().token(TOKEN).context_types(context_types).build())

    application.bot_data["url"] = SERVER_URL
    application.bot_data["admin_chat_id"] = ADMIN_CHAT_ID

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catpic", cat_pic))
    application.add_handler(CommandHandler("getcatarchive", get_full_archive_link))
    application.add_handler(MessageHandler(filters.PHOTO, send_cat_to_check))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))
    await application.bot.set_webhook(url=f"{SERVER_URL}/telegram")

    async def telegram(request: Request) -> Response:
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    async def custom_updates(request: Request) -> PlainTextResponse:
        try:
            user_id = int(request.query_params["user_id"])
            payload = request.query_params["payload"]
        except KeyError:
            return PlainTextResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content="Please pass both `user_id` and `payload` as query parameters.",
            )
        except ValueError:
            return PlainTextResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content="The `user_id` must be a string!",
            )

        await application.update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
        return PlainTextResponse("Thank you for the submission! It's being forwarded.")

    async def health(_: Request) -> PlainTextResponse:
        """For the health endpoint, reply with a simple plain text message."""
        return PlainTextResponse(content="The bot is still running fine :)")

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
            Route("/healthcheck", health, methods=["GET"]),
            Route("/submitpayload", custom_updates, methods=["POST", "GET"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=port,
            use_colors=False,
            host="0.0.0.0"
        )
    )

    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())