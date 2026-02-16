from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def stats_buttons(_, status):
    sudo_layout = [
        InlineKeyboardButton(text=_["SA_B_2"], callback_data="bot_stats_sudo"),
        InlineKeyboardButton(text=_["SA_B_3"], callback_data="TopOverall"),
    ]
    not_sudo_layout = [
        InlineKeyboardButton(text=_["SA_B_1"], callback_data="TopOverall"),
    ]
    
    return InlineKeyboardMarkup(
        [
            sudo_layout if status else not_sudo_layout,
            [
                InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
            ],
        ]
    )

def back_stats_buttons(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="stats_back"),
                InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
            ],
        ]
    )