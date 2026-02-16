from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, User
from MattoMusic import app

async def extract_user(msg: Message) -> User:
    if msg.reply_to_message:
        return msg.reply_to_message.from_user
        
    m_entity = msg.entities[1] if msg.text.startswith("/") else msg.entities[0]
    
    if m_entity.type == MessageEntityType.TEXT_MENTION:
        target_u = m_entity.user.id
    elif msg.command[1].isdecimal():
        target_u = int(msg.command[1])
    else:
        target_u = msg.command[1]
        
    return await app.get_users(target_u)