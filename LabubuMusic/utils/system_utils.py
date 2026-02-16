import time
import psutil

from MattoMusic.misc import _boot_
from MattoMusic.utils.formatters import get_readable_time

async def bot_sys_stats():
    active_time = int(time.time() - _boot_)
    sys_up = f"{get_readable_time(active_time)}"
    cpu_percent = f"{psutil.cpu_percent(interval=0.5)}%"
    ram_percent = f"{psutil.virtual_memory().percent}%"
    disk_percent = f"{psutil.disk_usage('/').percent}%"
    return sys_up, cpu_percent, ram_percent, disk_percent