from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def queue_markup(_, DURATION, CPLAY, videoid, played: Union[bool, int] = None, dur: Union[bool, int] = None):
    btn_no_dur = [
        [
            InlineKeyboardButton(text=_["QU_B_1"], callback_data=f"GetQueued {CPLAY}|{videoid}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    ]
    btn_dur = [
        [
            InlineKeyboardButton(text=_["QU_B_2"].format(played, dur), callback_data="GetTimer")
        ],
        [
            InlineKeyboardButton(text=_["QU_B_1"], callback_data=f"GetQueued {CPLAY}|{videoid}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return InlineKeyboardMarkup(btn_no_dur if DURATION == "Unknown" else btn_dur)

def queue_back_markup(_, CPLAY):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data=f"queue_back_timer {CPLAY}"),
                InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
            ]
        ]
    )

def aq_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    ]