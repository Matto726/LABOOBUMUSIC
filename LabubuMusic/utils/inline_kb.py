from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton as Ikb

from .utility_funcs import get_urls_from_text as is_url

def keyboard(btn_layout, row_width: int = 2):
    kb_obj = InlineKeyboard(row_width=row_width)
    constructed_btns = [
        (
            Ikb(text=str(b_data[0]), callback_data=str(b_data[1]))
            if not is_url(b_data[1])
            else Ikb(text=str(b_data[0]), url=str(b_data[1]))
        )
        for b_data in btn_layout
    ]
    kb_obj.add(*constructed_btns)
    return kb_obj

def ikb(dict_data: dict, row_width: int = 2):
    return keyboard(dict_data.items(), row_width=row_width)