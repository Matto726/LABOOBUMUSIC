from typing import List, Union
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.types import ChatPrivileges, Message

from MattoMusic import app
from MattoMusic.utils.database import get_assistant, set_loop

def generate_command(cmd_list: Union[str, List[str]]):
    return filters.command(cmd_list, "")

@app.on_message(filters.video_chat_started & filters.group)
async def handle_vc_start(client, message: Message):
    chat_id = message.chat.id
    try:
        await message.reply("<b>😍 Vɪᴅᴇᴏ Cʜᴀᴛ sᴛᴀʀᴛᴇᴅ! 🥳</b>")
        await set_loop(chat_id, 0)
    except Exception as err:
        await message.reply(f"<b>Eʀʀᴏʀ:</b> <code>{err}</code>")

async def extract_group_call(client: Client, message: Message, fallback_msg: str = ""):
    chat_peer = await client.resolve_peer(message.chat.id)
    chat_type = type(chat_peer).__name__
    
    try:
        if chat_type == "InputPeerChannel":
            full_data = (await client.invoke(pyrogram.raw.functions.channels.GetFullChannel(channel=chat_peer))).full_chat
        elif chat_type == "InputPeerChat":
            full_data = (await client.invoke(pyrogram.raw.functions.messages.GetFullChat(chat_id=chat_peer.chat_id))).full_chat
        else:
            return None
            
        if full_data.call:
            return full_data.call
            
    except Exception:
        pass
        
    await message.edit_text(f"<b>❌ Nᴏ ᴀᴄᴛɪᴠᴇ Vᴏɪᴄᴇ Cʜᴀᴛ ғᴏᴜɴᴅ</b> {fallback_msg}")
    return None

@app.on_message(filters.command("vcon") & filters.group)
async def activate_vc(client, message: Message):
    status_msg = await message.reply_text("<b>⏳ Iɴɪᴛɪᴀᴛɪɴɢ Vᴏɪᴄᴇ Cʜᴀᴛ...</b>")
    chat_id = message.chat.id
    
    try:
        ass_client = await get_assistant(chat_id)
        ass_details = await ass_client.get_me()
        ass_id = ass_details.id
        
        await app.promote_chat_member(
            chat_id, ass_id,
            privileges=ChatPrivileges(can_manage_video_chats=True, can_manage_chat=True)
        )
        
        chat_peer = await ass_client.resolve_peer(chat_id)
        await ass_client.invoke(CreateGroupCall(peer=chat_peer, random_id=ass_client.rnd_id() // 9000000000))
        
        await app.promote_chat_member(
            chat_id, ass_id,
            privileges=ChatPrivileges(can_manage_video_chats=False, can_manage_chat=False)
        )
        
        await status_msg.edit_text("<b>✅ Vᴏɪᴄᴇ Cʜᴀᴛ Oᴘᴇɴᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ! 🎧</b>")
    except ChatAdminRequired:
        await status_msg.edit_text("<b>❌ Bᴏᴛ ɴᴇᴇᴅs Pʀᴏᴍᴏᴛᴇ/Mᴀɴᴀɢᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴅᴏ ᴛʜɪs.</b>")
    except Exception as err:
        await status_msg.edit_text(f"<b>❌ Eʀʀᴏʀ:</b> <code>{err}</code>")


@app.on_message(filters.command("vcoff") & filters.group)
async def deactivate_vc(client, message: Message):
    status_msg = await message.reply_text("<b>⏳ Cʟᴏsɪɴɢ Vᴏɪᴄᴇ Cʜᴀᴛ...</b>")
    chat_id = message.chat.id
    
    try:
        ass_client = await get_assistant(chat_id)
        ass_details = await ass_client.get_me()
        ass_id = ass_details.id
        
        await app.promote_chat_member(
            chat_id, ass_id,
            privileges=ChatPrivileges(can_manage_video_chats=True, can_manage_chat=True)
        )
        
        active_call = await extract_group_call(ass_client, status_msg, fallback_msg=", Mɪɢʜᴛ ᴀʟʀᴇᴀᴅʏ ʙᴇ ᴄʟᴏsᴇᴅ.")
        if not active_call:
            await status_msg.delete()
            return
            
        await ass_client.invoke(DiscardGroupCall(call=active_call))
        
        await app.promote_chat_member(
            chat_id, ass_id,
            privileges=ChatPrivileges(can_manage_video_chats=False, can_manage_chat=False)
        )
        
        await status_msg.edit_text("<b>🚫 Vᴏɪᴄᴇ Cʜᴀᴛ Cʟᴏsᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ! ⚡</b>")
        await set_loop(chat_id, 0)
    except ChatAdminRequired:
        await status_msg.edit_text("<b>❌ Bᴏᴛ ɴᴇᴇᴅs Pʀᴏᴍᴏᴛᴇ/Mᴀɴᴀɢᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴅᴏ ᴛʜɪs.</b>")
    except Exception as err:
        await status_msg.edit_text(f"<b>❌ Eʀʀᴏʀ:</b> <code>{err}</code>")