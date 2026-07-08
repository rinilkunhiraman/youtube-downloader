"""
Download tab — URL input, video metadata preview, format options, and download trigger.
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

BROWSERS = ["None", "chrome", "safari", "firefox", "edge", "brave"]


class DownloadTab(ctk.CTkFrame):
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
        self._advanced_visible = False

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
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── URL bar ──────────────────────────────────────────────────
        url_frame = ctk.CTkFrame(scroll)
        url_frame.pack(pady=(16, 8), padx=24, fill="x")

        self._url_entry = ctk.CTkEntry(
            url_frame,
            height=46,
            placeholder_text="Paste YouTube URL here…",
            font=ctk.CTkFont(size=14),
        )
        self._url_entry.pack(side="left", padx=(16, 8), fill="x", expand=True)
        self._url_entry.bind("<Return>", lambda _e: self._fetch_video())

        ctk.CTkButton(
            url_frame,
            text="Fetch Info",
            width=120,
            height=46,
            command=self._fetch_video,
        ).pack(side="right", padx=(0, 16))

        # ── Video info card ───────────────────────────────────────────
        info_card = SectionFrame(scroll)
        info_card.pack(pady=8, padx=24, fill="x")

        # Thumbnail placeholder — styled box
        self._thumbnail = ThumbnailWidget(
            info_card,
            width=480,
            height=270,
            fg_color="#1e1e2e",
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            text_color="#555577",
        )
        self._thumbnail.pack(pady=(14, 8), padx=24)

        self._title_label = ctk.CTkLabel(
            info_card,
            text="No video loaded",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
            wraplength=860,
            text_color="#cccccc",
        )
        self._title_label.pack(anchor="w", padx=24, pady=(4, 2))

        self._meta_label = ctk.CTkLabel(
            info_card,
            text="Paste a URL above and click Fetch Info",
            font=ctk.CTkFont(size=12),
            text_color="#666688",
            anchor="w",
        )
        self._meta_label.pack(anchor="w", padx=24, pady=(0, 14))

        # ── Options ───────────────────────────────────────────────────
        opts = SectionFrame(scroll, title="Download Options")
        opts.pack(pady=8, padx=24, fill="x")

        # Two-column layout for quality + audio
        cols = ctk.CTkFrame(opts, fg_color="transparent")
        cols.pack(fill="x", padx=20, pady=(8, 4))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        # Left col — quality
        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=(0, 12))
        ctk.CTkLabel(left, text="Video Quality", font=ctk.CTkFont(size=13), text_color="#aaaacc").pack(anchor="w")
        self._quality_var = ctk.StringVar(value=QUALITY_PRESET_NAMES[0])
        self._quality_menu = ctk.CTkOptionMenu(
            left,
            variable=self._quality_var,
            values=QUALITY_PRESET_NAMES,
            width=190,
            height=36,
        )
        self._quality_menu.pack(anchor="w", pady=(4, 0))

        # Right col — audio only toggle
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(right, text="Format", font=ctk.CTkFont(size=13), text_color="#aaaacc").pack(anchor="w")
        self._audio_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            right,
            text="Audio Only (MP3)",
            variable=self._audio_var,
            font=ctk.CTkFont(size=14),
            command=self._on_audio_toggle,
        ).pack(anchor="w", pady=(8, 0))

        # Save-to path
        path_row = ctk.CTkFrame(opts, fg_color="#1e1e2e", corner_radius=8)
        path_row.pack(fill="x", padx=20, pady=(12, 4))

        ctk.CTkLabel(
            path_row, text="Save to", font=ctk.CTkFont(size=12),
            text_color="#888899"
        ).pack(side="left", padx=(14, 6), pady=10)

        self._path_label = ctk.CTkLabel(
            path_row,
            text=self._save_path,
            text_color="#7ec8ff",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self._path_label.pack(side="left", fill="x", expand=True, pady=10)

        ctk.CTkButton(
            path_row,
            text="Change",
            width=80,
            height=30,
            fg_color="transparent",
            border_width=1,
            command=self._choose_folder,
        ).pack(side="right", padx=10, pady=8)

        # Advanced toggle
        adv_toggle = ctk.CTkButton(
            opts,
            text="⚙  Advanced ▾",
            fg_color="transparent",
            hover_color="#2a2a3a",
            text_color="#888899",
            font=ctk.CTkFont(size=12),
            anchor="w",
            height=28,
            command=self._toggle_advanced,
        )
        adv_toggle.pack(anchor="w", padx=20, pady=(8, 4))

        # Advanced section (hidden by default)
        self._advanced_frame = ctk.CTkFrame(opts, fg_color="#1a1a2a", corner_radius=8)
        # Not packed yet — shown on toggle

        ctk.CTkLabel(
            self._advanced_frame,
            text="Browser cookies (helps with 403 / login-restricted videos)",
            font=ctk.CTkFont(size=12),
            text_color="#888899",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self._browser_var = ctk.StringVar(value="None")
        ctk.CTkOptionMenu(
            self._advanced_frame,
            variable=self._browser_var,
            values=BROWSERS,
            width=160,
            height=32,
            command=self._on_browser_change,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        # ── Progress ──────────────────────────────────────────────────
        self._progress = ProgressSection(scroll)
        self._progress.pack(pady=(12, 4), padx=28, fill="x")

        # ── Download button ───────────────────────────────────────────
        self._dl_btn = DownloadButton(scroll, command=self._start_download)
        self._dl_btn.pack(pady=(8, 24), padx=36, fill="x")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _toggle_advanced(self) -> None:
        if self._advanced_visible:
            self._advanced_frame.pack_forget()
            self._advanced_visible = False
        else:
            self._advanced_frame.pack(fill="x", padx=20, pady=(0, 12))
            self._advanced_visible = True

    def _check_ffmpeg(self) -> None:
        if not check_ffmpeg_installed():
            self.after(
                500,
                lambda: messagebox.showwarning(
                    "FFmpeg Not Found",
                    "FFmpeg is not installed or not in PATH.\n\n"
                    "Video conversion will fail.\n"
                    "Install with: brew install ffmpeg",
                ),
            )

    def _on_audio_toggle(self) -> None:
        state = "disabled" if self._audio_var.get() else "normal"
        self._quality_menu.configure(state=state)

    def _on_browser_change(self, browser: str) -> None:
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
            self._progress.reset()
            return

        self._current_info = info
        title = info.get("title", "Unknown")
        duration = format_duration(info.get("duration"))
        uploader = info.get("uploader") or info.get("channel") or "Unknown"
        view_count = info.get("view_count")
        views = f"  •  👁 {view_count:,}" if view_count else ""

        self._title_label.configure(text=title, text_color="white")
        self._meta_label.configure(
            text=f"⏱ {duration}  •  👤 {uploader}{views}",
            text_color="#aaaacc",
        )

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

        video_format = next(
            (fmt for name, fmt in VIDEO_QUALITY_PRESETS if name == self._quality_var.get()),
            None,
        )

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
        self.after(0, lambda: self._finalise(file_path, audio_only))

    def _finalise(self, file_path: str, audio_only: bool) -> None:
        self._dl_btn.set_idle()
        title = self._current_info.get("title", "download") if self._current_info else "download"

        if self._on_complete:
            self._on_complete(title, file_path, audio_only)

        if messagebox.askyesno("Download Complete", f"'{title}' saved.\n\nOpen containing folder?"):
            try:
                reveal_in_finder(file_path)
            except Exception:
                pass

    def _on_progress(self, percent: float, speed: Optional[str], eta: Optional[str]) -> None:
        self.after(0, lambda: self._progress.set_progress(percent, speed, eta))

    def _on_status(self, msg: str) -> None:
        self.after(0, lambda: self._progress.set_status(msg))
