# -----------------------------------------------
# 🔸 RAJSHREE MUSIC BOT
# 🔹 Developed & Owned by: MADARA
# 📅 Copyright © 2025 – All Rights Reserved
# -----------------------------------------------

from MADARAMUSIC.core.bot import MADARA
from MADARAMUSIC.core.dir import dirr
from MADARAMUSIC.core.git import git
from MADARAMUSIC.core.userbot import Userbot
from MADARAMUSIC.misc import dbb, heroku
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = MADARA()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "InflexOwnerBot"
