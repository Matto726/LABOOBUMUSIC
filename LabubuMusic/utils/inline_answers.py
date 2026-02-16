from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

answer = [
    InlineQueryResultArticle(
        title="Pᴀᴜsᴇ",
        description="Pᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴀᴄᴛɪᴠᴇ sᴛʀᴇᴀᴍ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/pause"),
    ),
    InlineQueryResultArticle(
        title="Rᴇsᴜᴍᴇ",
        description="Rᴇsᴜᴍᴇ ᴛʜᴇ ᴘᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/resume"),
    ),
    InlineQueryResultArticle(
        title="Sᴋɪᴘ",
        description="Sᴋɪᴘ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ ᴀɴᴅ ᴘʟᴀʏ ᴛʜᴇ ɴᴇxᴛ ᴏɴᴇ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/skip"),
    ),
    InlineQueryResultArticle(
        title="Eɴᴅ",
        description="Sᴛᴏᴘ ᴀɴᴅ ᴄʟᴇᴀʀ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/end"),
    ),
    InlineQueryResultArticle(
        title="Sʜᴜғғʟᴇ",
        description="Rᴀɴᴅᴏᴍɪᴢᴇ ᴛʜᴇ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏʟɪsᴛ/ǫᴜᴇᴜᴇ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/shuffle"),
    ),
    InlineQueryResultArticle(
        title="Lᴏᴏᴘ",
        description="Lᴏᴏᴘ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
        thumb_url="https://telegra.ph/file/c5952790fa8235f499749.jpg",
        input_message_content=InputTextMessageContent("/loop 3"),
    ),
]