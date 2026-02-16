import os
from contextlib import suppress
from config import autoclean

async def auto_clean(popped_item):
    try:
        file_path = popped_item.get("file")
        if not file_path:
            return
            
        autoclean.remove(file_path)
        
        if autoclean.count(file_path) == 0:
            if not any(marker in file_path for marker in ["vid_", "live_", "index_"]):
                with suppress(OSError):
                    os.remove(file_path)
    except Exception:
        pass