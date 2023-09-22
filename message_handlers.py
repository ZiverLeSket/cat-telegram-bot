from dataclasses import dataclass
from typing import List
from random import choice

from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, 
    CallbackContext, 
    ExtBot,
)

from imgur_lib import ImgurClient
from db_lib import  DataBase


@dataclass
class WebhookUpdate:
    user_id: int
    payload: str

class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def start(update: Update, context: CustomContext) -> None:
    text = (
        f'Чтобы получить случайного кота из архива - "/catpic"\n\n'
        f'Чтобы загрузить своего кота просто скинь его фотку\n\n'
        f'Чтобы получить доступ ко всему архиву котов - "/getcatarchive"\n\n'
    )
    await update.message.reply_html(text=text)


async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads: List[str] = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(
        chat_id=context.bot_data["admin_chat_id"], text=text, parse_mode=ParseMode.HTML
    )


async def cat_pic(update: Update, context: CustomContext) -> None:
    client: ImgurClient= context.bot_data["client"]
    photo_list = client.get_image_links(context.bot_data["album_id"])
    photo = choice(photo_list)
    keyboard = [
        [
            InlineKeyboardButton("👍Like", callback_data="Like"),
            InlineKeyboardButton("👎Dislike", callback_data="Dislike"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.sendPhoto(
        chat_id=update.effective_chat.id, photo=photo, caption="TurboMegaSuperCat", reply_markup=reply_markup
    )

async def send_cat_to_check(update: Update, context: CustomContext):
    file_id = update.message.photo[-1].file_id
    text = (
        "Посылаем кота на проверку."
    )
    keyboard = [
        [
            InlineKeyboardButton("👍Сохранить Кота", callback_data="Accept"),
            InlineKeyboardButton("👎Не кот", callback_data="Decline"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(text=text)
    await context.bot.send_photo(
        chat_id=context.bot_data["checker_chat_id"], photo = str(file_id), caption="Кот на проверку", reply_markup=reply_markup 
    )

async def button(update: Update, context: CustomContext) -> None:
    client: ImgurClient= context.bot_data["client"]
    query = update.callback_query

    await query.answer()
    await query.edit_message_caption(caption = query.data)
    if query.data == "Accept":
        file_id = query.message.photo[-1].file_id
        new_file = await context.bot.get_file(file_id)
        buffered_file = BytesIO()
        await new_file.download_to_memory(out=buffered_file)    
        client.upload_image_to_album(buffered_file.getvalue(), context.bot_data["album_id"])
        cat_id = client.parse_file_link(context.bot_data["album_id"], -1)
        author = query.from_user.username
        table_line = [[f"'{cat_id}'", '0', '0', '0', f"'{author}'"]]
        print(table_line)
        db = DataBase(context.bot_data["db_connect"])
        db.insert_data_to_table(tabletag='catrating', data=table_line)
    if query.data == "Like":
        pass
    if query.data == "Dislike":
        pass

async def get_full_archive_link(update: Update, context: CustomContext) -> None:
    album_id = context.bot_data["album_id"]
    url = f"imgur.com/a/{album_id}"
    await update.message.reply_html(text=url)