import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from ..logging import LOGGER

class SamarClient(Client):
    def __init__(self):
        LOGGER(__name__).info("Initializing MattoMusic Bot...")
        super().__init__(
            name="MattoMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        bot_info = await self.get_me()
        
        self.username = bot_info.username
        self.id = bot_info.id
        self.name = bot_info.first_name + " " + (bot_info.last_name or "")
        self.mention = bot_info.mention

        btn_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Add Me To Your Group", url=f"https://t.me/{self.username}?startgroup=true")]]
        )

        if config.LOG_GROUP_ID:
            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=(
                        f"<b>🎵 Bot Deployed Successfully</b>\n\n"
                        f"<b>Name:</b> {self.name}\n"
                        f"<b>Username:</b> @{self.username}\n"
                        f"<b>ID:</b> <code>{self.id}</code>\n\n"
                        f"<i>I'm now ready to stream music!</i>"
                    ),
                    reply_markup=btn_markup,
                )
            except pyrogram.errors.ChatWriteForbidden:
                LOGGER(__name__).error("Cannot send messages to the log group (Write Forbidden).")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        f"<b>🎵 Bot Deployed Successfully</b>\n\n"
                        f"<b>Name:</b> {self.name}\n"
                        f"<b>Username:</b> @{self.username}\n"
                        f"<b>ID:</b> <code>{self.id}</code>\n\n"
                        f"<i>I'm now ready to stream music!</i>",
                        reply_markup=btn_markup,
                    )
                except Exception as ex:
                    LOGGER(__name__).error(f"Failed to send fallback message in log group: {ex}")
            except Exception as ex:
                LOGGER(__name__).error(f"Unexpected error in log group dispatch: {ex}")
        else:
            LOGGER(__name__).warning("LOG_GROUP_ID variable is missing.")

        if config.LOG_GROUP_ID:
            try:
                member_status = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if member_status.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("Bot needs Administrator privileges in the Logger Group.")
            except Exception as ex:
                LOGGER(__name__).error(f"Failed to verify bot admin status: {ex}")

        LOGGER(__name__).info(f"MattoMusic Bot active as {self.name}")

    async def stop(self):
        await super().stop()