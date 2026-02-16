import asyncio
import speedtest
from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.decorators.language import language

def execute_speedtest(loader_msg, _):
    try:
        s_test = speedtest.Speedtest()
        s_test.get_best_server()
        loader_msg = loader_msg.edit_text(_["server_12"])
        
        s_test.download()
        loader_msg = loader_msg.edit_text(_["server_13"])
        
        s_test.upload()
        s_test.results.share()
        
        result_data = s_test.results.dict()
        loader_msg = loader_msg.edit_text(_["server_14"])
        return result_data
    except Exception as err:
        loader_msg.edit_text(f"❌ <code>{err}</code>")
        return None

@app.on_message(filters.command(["speedtest", "spt"]) & SUDOERS)
@language
async def trigger_speedtest(client, message: Message, _):
    loader = await message.reply_text(_["server_11"])
    loop_mgr = asyncio.get_event_loop()
    
    test_results = await loop_mgr.run_in_executor(None, execute_speedtest, loader, _)
    
    if test_results:
        summary_text = _["server_15"].format(
            test_results["client"]["isp"],
            test_results["client"]["country"],
            test_results["server"]["name"],
            test_results["server"]["country"],
            test_results["server"]["cc"],
            test_results["server"]["sponsor"],
            test_results["server"]["latency"],
            test_results["ping"],
        )
        await message.reply_photo(photo=test_results["share"], caption=summary_text)
        
    await loader.delete()