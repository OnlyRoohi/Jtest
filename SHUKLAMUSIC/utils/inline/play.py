import math
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
import config
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC.utils.formatters import time_to_seconds



def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [

        [
            InlineKeyboardButton(
                text=_["➕ IηTЄGЯATЄ Iη YOƱЯ CHΛT ➕"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.DANGER
            ),
            ],
            [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            InlineKeyboardButton(text="Replay", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="End", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"⛦ ᴊᴏɪɴ ⛦",
              url="https://t.me/+dv_rcq5uIXhmMWM1",
                style=ButtonStyle.SUCCESS
            ),
        ],
    ]

    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "◉—————————"
    elif 10 < umm < 20:
        bar = "—◉————————"
    elif 20 <= umm < 30:
        bar = "——◉———————"
    elif 30 <= umm < 40:
        bar = "———◉——————"
    elif 40 <= umm < 50:
        bar = "————◉—————"
    elif 50 <= umm < 60:
        bar = "—————◉————"
    elif 60 <= umm < 70:
        bar = "——————◉———"
    elif 70 <= umm < 80:
        bar = "———————◉——"
    elif 80 <= umm < 95:
        bar = "————————◉—"
    else:
        bar = "—————————◉"
        
    buttons  = [

        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
          ],
          [
            InlineKeyboardButton(
                text="ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"
            ),
            InlineKeyboardButton(
                text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"⛦ ᴊᴏɪɴ ⛦",
              url="https://t.me/+dv_rcq5uIXhmMWM1",
                style=ButtonStyle.SUCCESS
            ),
        ],
    ]

    return buttons


def stream_markup(_, chat_id):
    buttons  = [

        [
            InlineKeyboardButton(
                text=_["➕ IηTЄGЯATЄ Iη YOƱЯ CHΛT ➕"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.DANGER
            ),
          ],
          [
            InlineKeyboardButton(
                text="ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            InlineKeyboardButton(text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}",style=ButtonStyle.DANGER,),
            InlineKeyboardButton(text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"style=ButtonStyle.DANGER,),
        ],
        [
            InlineKeyboardButton(
                text=f"⛦ ᴊᴏɪɴ ⛦",
              url="https://t.me/+dv_rcq5uIXhmMWM1",
                style=ButtonStyle.SUCCESS
            ),
        ],
    ]

    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=ButtonStyle.DANGER
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
           InlineKeyboardButton(

                text=_["S_B_5"],

                url=f"https://t.me/{app.username}?startgroup=true",

            ),

        ],
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
           InlineKeyboardButton(

                text=_["S_B_5"],

                url=f"https://t.me/{app.username}?startgroup=true",

            ),

        ],
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
     ]
    return buttons

        
## Queue Markup

def queue_markup(_, videoid, chat_id):

    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
            ],
            [
            InlineKeyboardButton(
                text="ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"
            ),
            InlineKeyboardButton(
                text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"⛦ ᴊᴏɪɴ ⛦",
              url="https://t.me/+dv_rcq5uIXhmMWM1",
            ),
        ],
    ]

    return buttons

def speed_markup(_, chat_id):
    upl = InlineKeyboardMarkup(
        buttons = [
        [
            [
                InlineKeyboardButton(
                    text="🕒 0.5x",
                    callback_data=f"SpeedUP {chat_id}|0.5",
                ),
                InlineKeyboardButton(
                    text="🕓 0.75x",
                    callback_data=f"SpeedUP {chat_id}|0.75",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["P_B_4"],
                    callback_data=f"SpeedUP {chat_id}|1.0",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🕤 1.5x",
                    callback_data=f"SpeedUP {chat_id}|1.5",
                ),
                InlineKeyboardButton(
                    text="🕛 2.0x",
                    callback_data=f"SpeedUP {chat_id}|2.0",
                ),
            ],
                    [
            InlineKeyboardButton(text="sᴘᴇᴇᴅ", callback_data=f"ADMIN speed|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"⛦ ᴊᴏɪɴ ⛦",
              url="https://t.me/+dv_rcq5uIXhmMWM1",
            ),
        ],
    ]
    
    
        ]
                )
                
    return buttons
                                 
