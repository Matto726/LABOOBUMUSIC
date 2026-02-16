lovers_cache = {}

async def _get_lovers(chat_id: int):
    c_data = lovers_cache.get(chat_id, {})
    return c_data.get("couple", {})

async def get_image(chat_id: int):
    c_data = lovers_cache.get(chat_id, {})
    return c_data.get("img", "")

async def get_couple(chat_id: int, target_date: str):
    c_lovers = await _get_lovers(chat_id)
    return c_lovers.get(target_date, False)

async def save_couple(chat_id: int, target_date: str, couple_data: dict, img_url: str):
    if chat_id not in lovers_cache:
        lovers_cache[chat_id] = {"couple": {}, "img": ""}
    lovers_cache[chat_id]["couple"][target_date] = couple_data
    lovers_cache[chat_id]["img"] = img_url