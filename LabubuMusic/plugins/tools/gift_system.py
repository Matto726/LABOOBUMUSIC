from pyrogram import filters
from MattoMusic import app
from MattoMusic.core.db_setup import mongodb
from config import MONGO_DB_URI

gift_sys_db = mongodb.lovebirds
u_collection = gift_sys_db.users
g_collection = gift_sys_db.gifts

GIFT_INVENTORY = {
    "🌹": {"name": "Rose", "cost": 10, "emoji": "🌹"},
    "🍫": {"name": "Chocolate", "cost": 20, "emoji": "🍫"},
    "🧸": {"name": "Teddy Bear", "cost": 30, "emoji": "🧸"},
    "💍": {"name": "Ring", "cost": 50, "emoji": "💍"},
    "❤️": {"name": "Heart", "cost": 5, "emoji": "❤️"},
    "💎": {"name": "Diamond", "cost": 100, "emoji": "💎"},
}

def extract_member_details(msg):
    if msg.from_user:
        return msg.from_user.id, msg.from_user.first_name
    return None, None

async def init_member_db(u_id):
    if not await u_collection.find_one({"user_id": u_id}):
        await u_collection.insert_one({"user_id": u_id, "coins": 100, "gifts": {}})

async def execute_gift_claim(u_id, u_name):
    unclaimed = await g_collection.find({"receiver_id": u_id}).to_list(length=None)
    g_count = len(unclaimed)
    bonus_yield = 0
    
    for g_item in unclaimed:
        g_data = GIFT_INVENTORY.get(g_item["gift_emoji"])
        if g_data:
            b_val = g_data["cost"] // 2
            bonus_yield += b_val
            
            await u_collection.update_one(
                {"user_id": u_id},
                {"$inc": {f"gifts.{g_item['gift_emoji']}": 1, "coins": b_val}}
            )
            
        await g_collection.delete_one({"_id": g_item["_id"]})
        
    return g_count, bonus_yield

@app.on_message(filters.command(["top", "leaderboard"], prefixes=["/", "!", "."]))
async def show_top_users(client, message):
    try:
        top_list = await u_collection.find().sort("coins", -1).limit(10).to_list(length=10)
        if not top_list:
            return await message.reply_text("📊 Nᴏ ᴜsᴇʀs ғᴏᴜɴᴅ ɪɴ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ!")
            
        lb_text = "🏆 <b>Tᴏᴘ 10 Rɪᴄʜᴇsᴛ Usᴇʀs</b>\n\n"
        icons = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for idx, u in enumerate(top_list):
            badge = icons[idx] if idx < len(icons) else "🏅"
            lb_text += f"{badge} <b>Usᴇʀ {u['user_id']}</b> - {u['coins']} ᴄᴏɪɴs\n"
            
        await message.reply_text(lb_text)
    except Exception:
        pass

@app.on_message(filters.text & ~filters.regex(r"^[/!.\-]"))
async def reward_and_claim(client, message):
    try:
        u_id, u_name = extract_member_details(message)
        if not u_id: return
        
        await init_member_db(u_id)
        claimed_amt, yield_val = await execute_gift_claim(u_id, u_name)
        
        if claimed_amt > 0:
            c_msg = f"🎁 <b>Gɪғᴛs Cʟᴀɪᴍᴇᴅ!</b>\n\n<b>{u_name}</b>, ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ <b>{claimed_amt}</b> ᴘᴇɴᴅɪɴɢ ɢɪғᴛs!\n💰 <b>Bᴏɴᴜs:</b> +{yield_val} ᴄᴏɪɴs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ."
            await message.reply_text(c_msg)
            
        # Give passive chat coins
        await u_collection.update_one({"user_id": u_id}, {"$inc": {"coins": 1}})
    except Exception:
        pass