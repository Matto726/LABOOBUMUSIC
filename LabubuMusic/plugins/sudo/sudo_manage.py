from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import add_sudo, remove_sudo
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.extraction import extract_user
from MattoMusic.utils.inline import close_markup
from MattoMusic.utils.functions import DevID
from config import BANNED_USERS, OWNER_ID

def verify_owner_access(target_id):
    return target_id == OWNER_ID or target_id == DevID

@app.on_message(filters.command(["addsudo"]) & filters.user([OWNER_ID, DevID]))
@language
async def add_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    if target_user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(target_user.mention))
        
    is_added = await add_sudo(target_user.id)
    if is_added:
        SUDOERS.add(target_user.id)
        await message.reply_text(_["sudo_2"].format(target_user.mention))
    else:
        await message.reply_text(_["sudo_8"])

@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user([OWNER_ID, DevID]))
@language
async def remove_sudo_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    
    if target_user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(target_user.mention))
    
    is_removed = await remove_sudo(target_user.id)
    if is_removed:
        SUDOERS.remove(target_user.id)
        await message.reply_text(_["sudo_4"].format(target_user.mention))
    else:
        await message.reply_text(_["sudo_8"])

@app.on_message(filters.command(["deleteallsudo", "clearallsudo", "removeallsudo"]) & filters.user([OWNER_ID, DevID]))
@language
async def clear_all_sudoers(client, message: Message, _):
    btn_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_delete_all_sudo"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete_all_sudo")
        ]
    ])
    
    total_sudoers = len([u_id for u_id in SUDOERS if u_id != OWNER_ID])
    
    if total_sudoers == 0:
        return await message.reply_text("❌ <b>No sudoers found to delete!</b>")
    
    await message.reply_text(
        f"⚠️ <b>Warning!</b>\n\nAre you sure you want to delete all <code>{total_sudoers}</code> sudoers?\n\n<i>This action cannot be undone!</i>",
        reply_markup=btn_markup
    )

@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def list_sudoers(client, message: Message, _):
    if not verify_owner_access(message.from_user.id) and message.from_user.id not in SUDOERS:
        btn_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 View Sudolist", callback_data="view_sudolist_unauthorized")]])
        return await message.reply_text("🔒 <b>Access Restricted</b>\n\nOnly Owner and Sudoers can check the sudolist.", reply_markup=btn_markup)
    
    display_text = _["sudo_5"]
    try:
        owner_data = await app.get_users(OWNER_ID)
        owner_mention = owner_data.first_name if not owner_data.mention else owner_data.mention
        display_text += f"1➤ {owner_mention} <code>{OWNER_ID}</code>\n"
    except Exception:
        display_text += f"1➤ Owner <code>{OWNER_ID}</code>\n"
    
    tracker = 0
    sudo_block = ""
    
    for u_id in SUDOERS:
        if u_id != OWNER_ID:
            try:
                u_data = await app.get_users(u_id)
                u_mention = u_data.first_name if not u_data.mention else u_data.mention
                tracker += 1
                sudo_block += f"{tracker + 1}➤ {u_mention} <code>{u_id}</code>\n"
            except Exception:
                tracker += 1
                sudo_block += f"{tracker + 1}➤ Unknown User <code>{u_id}</code>\n"
                continue
    
    if tracker > 0:
        display_text += _["sudo_6"]
        display_text += sudo_block
    else:
        display_text += "\n<b>No sudoers found.</b>"
    
    await message.reply_text(display_text, reply_markup=close_markup(_))

@app.on_callback_query(filters.regex("confirm_delete_all_sudo"))
async def execute_clear_sudoers(client, query: CallbackQuery):
    if not verify_owner_access(query.from_user.id):
        return await query.answer("❌ Only owner can do this!", show_alert=True)
    
    deleted_tally = 0
    targets = [u_id for u_id in SUDOERS.copy() if u_id != OWNER_ID]
    
    for u_id in targets:
        try:
            is_removed = await remove_sudo(u_id)
            if is_removed:
                SUDOERS.discard(u_id)
                deleted_tally += 1
        except Exception: continue
    
    if deleted_tally > 0:
        await query.edit_message_text(f"✅ <b>Successfully deleted all sudoers!</b>\n\n📊 <b>Deleted:</b> <code>{deleted_tally}</code> users\n🛡️ <b>Protected:</b> Owner remains safe")
    else:
        await query.edit_message_text("❌ <b>Failed to delete sudoers!</b>\n\nTry again later.")

@app.on_callback_query(filters.regex("cancel_delete_all_sudo"))
async def abort_clear_sudoers(client, query: CallbackQuery):
    await query.edit_message_text("❌ <b>Cancelled!</b>\n\nNo sudoers were deleted.")

@app.on_callback_query(filters.regex("view_sudolist_unauthorized"))
async def display_unauthorized_sudolist(client, query: CallbackQuery):
    await query.answer("🚫 Access Denied!\n\nOnly Owner and Sudoers can check sudolist.", show_alert=True)