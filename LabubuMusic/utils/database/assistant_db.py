import random
from MattoMusic.core.db_setup import mongodb
from MattoMusic import assistant_bot

ass_collection = mongodb.assistants
active_assistants_cache = {}

async def fetch_ass_client(ass_number: int):
    ass_map = {
        1: assistant_bot.one,
        2: assistant_bot.two,
        3: assistant_bot.three,
        4: assistant_bot.four,
        5: assistant_bot.five,
    }
    return ass_map.get(int(ass_number))

async def update_assistant_record(chat_id, ass_number):
    num_val = int(ass_number)
    await ass_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": num_val}},
        upsert=True,
    )

async def configure_new_assistant(chat_id):
    from MattoMusic.core.assistant_bot import assistants
    
    random_ass = random.choice(assistants)
    active_assistants_cache[chat_id] = random_ass
    
    await ass_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": random_ass}},
        upsert=True,
    )
    return random_ass

async def retrieve_assistant(chat_id: int) -> str:
    from MattoMusic.core.assistant_bot import assistants
    
    cached_ass = active_assistants_cache.get(chat_id)
    if cached_ass and cached_ass in assistants:
        return cached_ass
        
    db_record = await ass_collection.find_one({"chat_id": chat_id})
    if db_record and db_record.get("assistant") in assistants:
        ass_num = db_record["assistant"]
        active_assistants_cache[chat_id] = ass_num
        return ass_num
        
    return await configure_new_assistant(chat_id)

async def assign_group_assistant(self, chat_id: int):
    from MattoMusic.core.assistant_bot import assistants
    
    current_ass = active_assistants_cache.get(chat_id)
    
    if not current_ass:
        db_record = await ass_collection.find_one({"chat_id": chat_id})
        if not db_record:
            final_ass = await configure_new_assistant(chat_id)
        else:
            final_ass = db_record["assistant"]
            if final_ass in assistants:
                active_assistants_cache[chat_id] = final_ass
            else:
                final_ass = await configure_new_assistant(chat_id)
    else:
        if current_ass in assistants:
            final_ass = current_ass
        else:
            final_ass = await configure_new_assistant(chat_id)
            
    ass_obj_map = {
        1: self.one,
        2: self.two,
        3: self.three,
        4: self.four,
        5: self.five
    }
    return ass_obj_map.get(int(final_ass))