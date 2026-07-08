"""
Core download logic — completely decoupled from any UI framework.

Callbacks use plain callables so any frontend (Tkinter, CLI, web) can plug in.
"""
import os
import shutil
from threading import Thread
from typing import Callable, Optional
import yt_dlp

from src.config import (
    COOKIES_FILE,
    DEFAULT_AUDIO_CODEC,
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_AUDIO_QUALITY,
    DEFAULT_VIDEO_FORMAT,
    FFMPEG_CONVERT_TO_MP4,
    HTTP_HEADERS,
    USER_AGENT,
)

# Type aliases for readability
ProgressCallback = Callable[[float, Optional[str], Optional[str]], None]
StatusCallback = Callable[[str], None]


class DownloadError(Exception):
    """Raised when a download fails."""


def check_ffmpeg_installed() -> bool:
    """Returns True if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


class Downloader:
    """
    Wraps yt-dlp for video/audio downloading.

    Args:
        on_progress:  Called with (percent: float, speed: str | None, eta: str | None)
        on_status:    Called with a human-readable status string
    """

    def __init__(
        self,
        on_progress: Optional[ProgressCallback] = None,
        on_status: Optional[StatusCallback] = None,
    ):
        self.on_progress = on_progress
        self.on_status = on_status
        self._active_ydl: Optional[yt_dlp.YoutubeDL] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_info(self, url: str) -> dict:
        """
        Fetch video metadata without downloading.

        Returns:
            yt-dlp info dict (title, thumbnail, duration, formats, …)

        Raises:
            DownloadError on any yt-dlp failure.
        """
        opts = self._base_opts()
        opts.update({"quiet": True, "no_warnings": True})
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(str(exc)) from exc

    def download(
        self,
        url: str,
        output_dir: str,
        audio_only: bool = False,
        video_format: Optional[str] = None,
        on_complete: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Start a download in a background thread.

        Args:
            url:          Video URL.
            output_dir:   Directory to save the file.
            audio_only:   Extract MP3 instead of keeping video.
            video_format: yt-dlp format string (e.g., 'best', 'bestvideo+bestaudio').
                          If None, uses DEFAULT_VIDEO_FORMAT.
            on_complete:  Called with the saved file path when done.
        """
        thread = Thread(
            target=self._download_worker,
            args=(url, output_dir, audio_only, video_format, on_complete),
            daemon=True,
        )
        thread.start()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _base_opts(self) -> dict:
        opts = {
            "http_headers": HTTP_HEADERS,
            "user_agent": USER_AGENT,
        }
        if os.path.exists(COOKIES_FILE):
            opts["cookiefile"] = COOKIES_FILE
        return opts

    def _build_download_opts(
        self, output_dir: str, audio_only: bool, video_format: Optional[str] = None
    ) -> dict:
        opts = self._base_opts()
        opts["outtmpl"] = os.path.join(output_dir, "%(title)s.%(ext)s")
        opts["progress_hooks"] = [self._progress_hook]
        opts["postprocessor_hooks"] = [self._postprocessor_hook]

        if audio_only:
            opts["format"] = DEFAULT_AUDIO_FORMAT
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": DEFAULT_AUDIO_CODEC,
                    "preferredquality": DEFAULT_AUDIO_QUALITY,
                }
            ]
        else:
            opts["format"] = video_format or DEFAULT_VIDEO_FORMAT
            
            # Always convert to mp4 for maximum compatibility
            # (handles webm, mkv, flv, etc. that might not play on all devices)
            if FFMPEG_CONVERT_TO_MP4:
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": "mp4",  # Note: yt-dlp uses "prefered" (sic)
                    }
                ]
                # Force final extension to .mp4
                opts["outtmpl"] = os.path.join(output_dir, "%(title)s.mp4")

        return opts

    def _download_worker(
        self,
        url: str,
        output_dir: str,
        audio_only: bool,
        video_format: Optional[str],
        on_complete: Optional[Callable[[str], None]],
    ) -> None:
        saved_path: Optional[str] = None

        def _postprocessor_hook_capture(d: dict) -> None:
            nonlocal saved_path
            self._postprocessor_hook(d)
            if d["status"] == "finished":
                saved_path = d.get("info_dict", {}).get("filepath") or d.get(
                    "info_dict", {}
                ).get("_filename")

        opts = self._build_download_opts(output_dir, audio_only, video_format)
        opts["postprocessor_hooks"] = [_postprocessor_hook_capture]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                self._active_ydl = ydl
                info = ydl.extract_info(url, download=True)

            # Resolve final file path from info dict if hook didn't capture it
            if saved_path is None and info:
                ext = DEFAULT_AUDIO_CODEC if audio_only else "mp4"
                title = info.get("title", "download")
                saved_path = os.path.join(output_dir, f"{title}.{ext}")

            self._emit_status("✅ Download completed successfully!")

            if on_complete and saved_path:
                on_complete(saved_path)

        except Exception as exc:
            self._emit_status(f"❌ Error: {exc}")
            raise DownloadError(str(exc)) from exc
        finally:
            self._active_ydl = None

    def _progress_hook(self, d: dict) -> None:
        if d["status"] != "downloading" or not self.on_progress:
            return
        try:
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total) * 100 if total > 0 else 0
            self.on_progress(percent, d.get("_speed_str"), d.get("_eta_str"))
        except Exception:
            pass

    def _postprocessor_hook(self, d: dict) -> None:
        if d["status"] == "finished":
            title = d.get("info_dict", {}).get("title", "file")
            self._emit_status(f"⚙️  Processing: {title}")

    def _emit_status(self, msg: str) -> None:
        if self.on_status:
            self.on_status(msg)
