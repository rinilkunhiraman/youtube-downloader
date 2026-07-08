"""
Application-wide constants and default settings.
"""
import os

# --- App ---
APP_NAME = "YouTube Downloader"
APP_VERSION = "0.3.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"
APP_GEOMETRY = "950x750"
APP_MIN_SIZE = (900, 700)
APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

# --- Paths ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_FILE = os.path.join(ROOT_DIR, "cookies.txt")
HISTORY_FILE = os.path.join(ROOT_DIR, "download_history.json")
DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

# --- Download ---
# Video quality presets: (display_name, yt-dlp format string)
# "bestvideo+bestaudio" downloads two streams and merges them — this is
# intentional and NOT the multi-format bug. It produces one output file.
VIDEO_QUALITY_PRESETS = [
    ("Best (4K/1080p)",     "bestvideo+bestaudio/best"),
    ("High (1080p)",        "bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
    ("Medium (720p)",       "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    ("Low (480p)",          "bestvideo[height<=480]+bestaudio/best[height<=480]"),
    ("Smallest (360p)",     "bestvideo[height<=360]+bestaudio/best[height<=360]"),
]
QUALITY_PRESET_NAMES = [name for name, _ in VIDEO_QUALITY_PRESETS]
DEFAULT_VIDEO_FORMAT   = VIDEO_QUALITY_PRESETS[0][1]

DEFAULT_AUDIO_FORMAT   = "bestaudio/best"
DEFAULT_AUDIO_CODEC    = "mp3"
DEFAULT_AUDIO_QUALITY  = "192"   # kbps

# Always re-encode to mp4 so the output is guaranteed playable everywhere,
# even when the source stream is webm, mkv, or any other container.
FFMPEG_CONVERT_TO_MP4 = True

HTTP_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# --- UI ---
ACCENT_GREEN         = "#00cc66"
WHATSAPP_GREEN       = "#25D366"
THUMBNAIL_SIZE       = (480, 270)
HISTORY_TITLE_MAX_LEN = 65
