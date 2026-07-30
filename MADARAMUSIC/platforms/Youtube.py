# -----------------------------------------------
# 🔸 RAJSHREE MUSIC — YouTube Platform
# 🔹 Direct yt-dlp backend (no external API)
#    Cookie rotation • Async thread download
#    Zero-lag, 24-hour uptime
# -----------------------------------------------

import asyncio
import os
import re
import random
from pathlib import Path
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython import VideosSearch, Playlist

DOWNLOAD_DIR = "downloads"
COOKIE_DIR = "MADARAMUSIC/assets"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ── Cookie manager ────────────────────────────
_cookies: list[str] = []
_cookies_loaded = False


def _get_cookie() -> str | None:
    global _cookies, _cookies_loaded
    if not _cookies_loaded:
        _cookies_loaded = True
        if os.path.isdir(COOKIE_DIR):
            _cookies = [
                os.path.join(COOKIE_DIR, f)
                for f in os.listdir(COOKIE_DIR)
                if f.endswith(".txt")
            ]
    return random.choice(_cookies) if _cookies else None


# ── yt-dlp base options ───────────────────────
def _base_opts(cookie: str | None) -> dict:
    opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "overwrites": False,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
    }
    if cookie:
        opts["cookiefile"] = cookie
    return opts


# ── Standalone download helpers ───────────────
async def download_song(link: str) -> str | None:
    """Download audio as opus/webm — fast, lossless, Telegram-ready."""
    video_id = _extract_id(link)
    if not video_id:
        return None

    cached = _cached(video_id, ("webm", "opus", "m4a", "mp3"))
    if cached:
        return cached

    cookie = _get_cookie()
    ydl_opts = {
        **_base_opts(cookie),
        "format": "bestaudio[ext=webm][acodec=opus]/bestaudio[ext=m4a]/bestaudio",
    }

    return await asyncio.to_thread(_run_download, link, ydl_opts, video_id, ("webm", "opus", "m4a", "mp3"))


async def download_video(link: str) -> str | None:
    """Download video ≤720p mp4 — balanced quality/size."""
    video_id = _extract_id(link)
    if not video_id:
        return None

    cached = _cached(video_id, ("mp4",))
    if cached:
        return cached

    cookie = _get_cookie()
    ydl_opts = {
        **_base_opts(cookie),
        "format": "bestvideo[height<=?720][ext=mp4]+bestaudio/best[height<=?720]/best",
        "merge_output_format": "mp4",
    }

    return await asyncio.to_thread(_run_download, link, ydl_opts, video_id, ("mp4",))


# ── Internal helpers ──────────────────────────
def _extract_id(link: str) -> str | None:
    if "v=" in link:
        return link.split("v=")[-1].split("&")[0]
    if "youtu.be/" in link:
        return link.split("youtu.be/")[-1].split("?")[0]
    if re.match(r"^[A-Za-z0-9_-]{11}$", link):
        return link
    return link if link else None


def _cached(video_id: str, exts: tuple) -> str | None:
    for ext in exts:
        p = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def _run_download(url: str, ydl_opts: dict, video_id: str, exts: tuple) -> str | None:
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception:
        return None
    return _cached(video_id, exts)


def time_to_seconds(time) -> int:
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# ── Main YouTubeAPI class (interface unchanged) ─
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None) -> list:
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ydl_opts = {"quiet": True, "no_warnings": True}
        cookie = _get_cookie()
        if cookie:
            ydl_opts["cookiefile"] = cookie
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        formats_available = []
        with ydl:
            r = ydl.extract_info(link, download=False)
            for fmt in r.get("formats", []):
                try:
                    if "dash" not in str(fmt.get("format", "")).lower():
                        formats_available.append(
                            {
                                "format": fmt["format"],
                                "filesize": fmt.get("filesize"),
                                "format_id": fmt["format_id"],
                                "ext": fmt["ext"],
                                "format_note": fmt.get("format_note", ""),
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            if video or songvideo:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            return None, False
        except Exception:
            return None, False


YouTube = YouTubeAPI()
