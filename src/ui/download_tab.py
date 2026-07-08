"""
Download tab — URL input, video metadata preview, format options, and download trigger.

All heavy work (network, yt-dlp) is delegated to Downloader and utils;
this module only handles layout and event wiring.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.config import DEFAULT_DOWNLOAD_DIR, QUALITY_PRESET_NAMES, VIDEO_QUALITY_PRESETS
from src.downloader import Downloader, DownloadError, check_ffmpeg_installed
from src.utils import fetch_thumbnail, format_duration, reveal_in_finder
from src.ui.components import (
    DownloadButton,
    ProgressSection,
    SectionFrame,
    ThumbnailWidget,
)


class DownloadTab(ctk.CTkFrame):
    """
    Self-contained download tab widget.

    Args:
        master:       Parent widget (the CTkTabview tab frame).
        on_complete:  Called with (title, file_path, audio_only) after a
                      successful download so the app can update history.
    """

    def __init__(
        self,
        master,
        on_complete: Optional[Callable[[str, str, bool], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_complete = on_complete
        self._save_path = DEFAULT_DOWNLOAD_DIR
        self._current_info: Optional[dict] = None

        self._downloader = Downloader(
            on_progress=self._on_progress,
            on_status=self._on_status,
        )

        self._build()
        self._check_ffmpeg()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # Wrap everything in a scrollable frame so content doesn't get cut off
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

        # --- URL row ---
        url_frame = ctk.CTkFrame(scroll_container)
        url_frame.pack(pady=15, padx=25, fill="x")

        ctk.CTkLabel(
            url_frame, text="YouTube URL:", font=ctk.CTkFont(size=15)
        ).pack(side="left", padx=(20, 10))

        self._url_entry = ctk.CTkEntry(
            url_frame, height=45, placeholder_text="Paste YouTube link here…"
        )
        self._url_entry.pack(side="left", padx=5, fill="x", expand=True)
        # Allow pressing Enter to fetch
        self._url_entry.bind("<Return>", lambda _e: self._fetch_video())

        ctk.CTkButton(
            url_frame,
            text="Fetch Info",
            width=130,
            height=45,
            command=self._fetch_video,
        ).pack(side="right", padx=20)

        # --- Metadata preview ---
        meta = SectionFrame(scroll_container)
        meta.pack(pady=10, padx=25, fill="x")

        self._title_label = ctk.CTkLabel(
            meta,
            text="Title: —",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
            wraplength=850,
        )
        self._title_label.pack(anchor="w", padx=25, pady=(15, 2))

        self._meta_label = ctk.CTkLabel(
            meta,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            anchor="w",
        )
        self._meta_label.pack(anchor="w", padx=25, pady=(0, 6))

        self._thumbnail = ThumbnailWidget(meta)
        self._thumbnail.pack(pady=10)

        # --- Options ---
        options = SectionFrame(scroll_container, title="Options")
        options.pack(pady=10, padx=25, fill="x")

        # Quality selector (only applies to video, not audio-only)
        quality_row = ctk.CTkFrame(options, fg_color="transparent")
        quality_row.pack(fill="x", padx=25, pady=(12, 4))
        
        ctk.CTkLabel(quality_row, text="Video Quality:", anchor="w").pack(anchor="w")
        self._quality_var = ctk.StringVar(value=QUALITY_PRESET_NAMES[0])
        self._quality_menu = ctk.CTkOptionMenu(
            quality_row,
            variable=self._quality_var,
            values=QUALITY_PRESET_NAMES,
            width=200,
        )
        self._quality_menu.pack(anchor="w", pady=(4, 0))

        self._audio_var = tk.BooleanVar(value=False)
        audio_cb = ctk.CTkCheckBox(
            options,
            text="🎵  Audio Only (MP3)",
            variable=self._audio_var,
            font=ctk.CTkFont(size=15),
            command=self._on_audio_toggle,
        )
        audio_cb.pack(anchor="w", padx=25, pady=(12, 4))

        # Browser cookie selector — fixes 403 errors
        cookie_row = ctk.CTkFrame(options, fg_color="transparent")
        cookie_row.pack(fill="x", padx=25, pady=(4, 12))

        ctk.CTkLabel(
            cookie_row,
            text="Use cookies from browser (fixes 403 errors):",
            anchor="w",
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w")

        self._browser_var = ctk.StringVar(value="None")
        ctk.CTkOptionMenu(
            cookie_row,
            variable=self._browser_var,
            values=["None", "chrome", "safari", "firefox", "edge", "brave"],
            width=160,
            command=self._on_browser_change,
        ).pack(anchor="w", pady=(4, 0))

        # Save-to path
        path_row = ctk.CTkFrame(options, fg_color="transparent")
        path_row.pack(fill="x", padx=25, pady=(0, 12))

        ctk.CTkLabel(path_row, text="Save to:", anchor="w").pack(anchor="w")
        self._path_label = ctk.CTkLabel(
            path_row, text=self._save_path, text_color="#7ec8ff", anchor="w"
        )
        self._path_label.pack(anchor="w", pady=(2, 8))
        ctk.CTkButton(
            path_row, text="Change Folder", width=150, command=self._choose_folder
        ).pack(anchor="w")

        # --- Progress ---
        self._progress = ProgressSection(scroll_container)
        self._progress.pack(pady=15, padx=30, fill="x")

        # --- Download button ---
        self._dl_btn = DownloadButton(scroll_container, command=self._start_download)
        self._dl_btn.pack(pady=20, padx=40, fill="x")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _check_ffmpeg(self) -> None:
        """Warn if FFmpeg is missing (needed for format conversion and merging)."""
        if not check_ffmpeg_installed():
            self.after(
                500,
                lambda: messagebox.showwarning(
                    "FFmpeg Not Found",
                    "FFmpeg is not installed or not in PATH.\n\n"
                    "Video format conversion and stream merging will fail.\n"
                    "Install FFmpeg from https://ffmpeg.org/download.html",
                ),
            )

    def _on_audio_toggle(self) -> None:
        """Disable quality selector when audio-only is checked."""
        audio_only = self._audio_var.get()
        state = "disabled" if audio_only else "normal"
        self._quality_menu.configure(state=state)

    def _on_browser_change(self, browser: str) -> None:
        """Recreate the Downloader with the selected browser for cookies."""
        selected = None if browser == "None" else browser
        self._downloader = Downloader(
            on_progress=self._on_progress,
            on_status=self._on_status,
            cookies_from_browser=selected,
        )

    def _fetch_video(self) -> None:
        url = self._url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please paste a YouTube URL.")
            return

        self._progress.set_status("Fetching video info…")
        self.update_idletasks()

        try:
            info = self._downloader.fetch_info(url)
        except DownloadError as exc:
            messagebox.showerror("Fetch Failed", str(exc))
            self._progress.set_status("Ready")
            return

        self._current_info = info
        title = info.get("title", "Unknown")
        duration = format_duration(info.get("duration"))
        uploader = info.get("uploader") or info.get("channel") or "Unknown"

        self._title_label.configure(text=f"Title: {title}")
        self._meta_label.configure(text=f"⏱ {duration}  •  👤 {uploader}")

        # Fetch thumbnail in background to avoid blocking the UI
        thumb_url = info.get("thumbnail")
        if thumb_url:
            self.after(50, lambda: self._load_thumbnail(thumb_url))

        self._progress.set_status("✅ Ready to download")

    def _load_thumbnail(self, url: str) -> None:
        img = fetch_thumbnail(url)
        if img:
            self._thumbnail.set_image(img)

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory(initialdir=self._save_path)
        if folder:
            self._save_path = folder
            self._path_label.configure(text=folder)

    def _start_download(self) -> None:
        if not self._current_info:
            messagebox.showwarning("No Video", "Please fetch a video first.")
            return

        url = self._url_entry.get().strip()
        audio_only = self._audio_var.get()

        # Resolve selected quality preset to yt-dlp format string
        selected_quality_name = self._quality_var.get()
        video_format = None
        for name, fmt in VIDEO_QUALITY_PRESETS:
            if name == selected_quality_name:
                video_format = fmt
                break

        self._dl_btn.set_busy()
        self._progress.reset()

        self._downloader.download(
            url=url,
            output_dir=self._save_path,
            audio_only=audio_only,
            video_format=video_format,
            on_complete=lambda path: self._handle_complete(path, audio_only),
        )

    def _handle_complete(self, file_path: str, audio_only: bool) -> None:
        """Called from the downloader thread — schedule GUI work on main thread."""
        self.after(0, lambda: self._finalise(file_path, audio_only))

    def _finalise(self, file_path: str, audio_only: bool) -> None:
        self._dl_btn.set_idle()
        title = self._current_info.get("title", "download") if self._current_info else "download"

        if self._on_complete:
            self._on_complete(title, file_path, audio_only)

        result = messagebox.askyesno(
            "Download Complete",
            f"'{title}' saved successfully.\n\nOpen containing folder?",
        )
        if result:
            try:
                reveal_in_finder(file_path)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Downloader callbacks (called from background thread)
    # ------------------------------------------------------------------

    def _on_progress(self, percent: float, speed: Optional[str], eta: Optional[str]) -> None:
        self.after(0, lambda: self._progress.set_progress(percent, speed, eta))

    def _on_status(self, msg: str) -> None:
        self.after(0, lambda: self._progress.set_status(msg))
