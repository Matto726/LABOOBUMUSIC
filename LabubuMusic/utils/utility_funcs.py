from datetime import datetime, timedelta
from re import findall, sub
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

DevID = 7574330905

MARKDOWN = """
**Markdown Formatting Guide!**

Supported variables:
{GROUPNAME} - Group's Title
{NAME} - User's First Name
{ID} - User's ID
{FIRSTNAME} - User's First Name
{SURNAME} - User's Last Name
{USERNAME} - User's Username
{DATE} - Current Date
{WEEKDAY} - Current Weekday
{TIME} - Current Time
{MENTION} - Mention User
"""

def get_urls_from_text(msg_text: str) -> bool:
    url_pattern = r"(?:(?:https?|ftp)://)?[\w/\-?=%.]+\.[\w/\-?=%.]+"
    return bool(findall(url_pattern, msg_text))

async def extract_user_and_reason(msg: Message, sender_chat=False):
    t_user = None
    t_reason = None
    
    if msg.reply_to_message:
        r_msg = msg.reply_to_message
        if r_msg.from_user:
            t_user = r_msg.from_user.id
        elif r_msg.sender_chat and sender_chat:
            t_user = r_msg.sender_chat.id
        t_reason = msg.text.split(None, 1)[1] if len(msg.command) > 1 else None
    else:
        if len(msg.command) > 1:
            raw_user = msg.text.split(None, 2)[1]
            t_reason = msg.text.split(None, 2)[2] if len(msg.command) > 2 else None
            
            if msg.entities:
                m_ent = msg.entities[1] if msg.text.startswith("/") else msg.entities[0]
                if m_ent.type == MessageEntityType.TEXT_MENTION:
                    t_user = m_ent.user.id
                elif raw_user.isnumeric():
                    t_user = int(raw_user)
                else:
                    t_user = raw_user
            elif raw_user.isnumeric():
                t_user = int(raw_user)
            else:
                t_user = raw_user

    return t_user, t_reason

async def time_converter(msg: Message, t_val: str) -> datetime:
    unit_types = ["m", "h", "d"]
    detected_unit = "".join(list(filter(t_val[-1].lower().endswith, unit_types)))
    now_time = datetime.now()
    num_val = t_val[:-1]
    
    if not num_val.isdigit():
        return await msg.reply_text("Incorrect time format specified.")
        
    if detected_unit == "m":
        res_time = now_time + timedelta(minutes=int(num_val))
    elif detected_unit == "h":
        res_time = now_time + timedelta(hours=int(num_val))
    elif detected_unit == "d":
        res_time = now_time + timedelta(days=int(num_val))
    else:
        return await msg.reply_text("Incorrect unit specified.")
    return res_time