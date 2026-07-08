"""
Root application window — wires tabs and shared services together.
"""
from __future__ import annotations

import os
from pathlib import Path
from tkinter import PhotoImage

import customtkinter as ctk

from src.config import (
    APP_AUTHOR,
    APP_GEOMETRY,
    APP_MIN_SIZE,
    APP_TITLE,
    APP_VERSION,
    APPEARANCE_MODE,
    COLOR_THEME,
    ROOT_DIR,
)
from src.history import HistoryManager
from src.ui.download_tab import DownloadTab
from src.ui.history_tab import HistoryTab


class App(ctk.CTk):
    """
    Main application window.

    Responsibilities:
    - Apply global CTk theme settings.
    - Instantiate shared services (HistoryManager).
    - Build the tabview and mount both tab widgets.
    - Bridge the download-complete event from DownloadTab → HistoryTab.
    """

    def __init__(self):
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(*APP_MIN_SIZE)

        # Set app icon if available
        self._set_icon()

        # Shared services
        self._history = HistoryManager()

        self._build()

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------

    def _set_icon(self) -> None:
        """Set window icon from assets/icon.png if it exists."""
        icon_path = Path(ROOT_DIR) / "assets" / "icon.png"
        if icon_path.exists():
            try:
                # For Tk windows, iconphoto expects a PhotoImage
                img = PhotoImage(file=str(icon_path))
                self.iconphoto(True, img)
                # Keep a reference to prevent garbage collection
                self._icon = img
            except Exception:
                pass  # Icon optional, silently skip if it fails

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(pady=(10, 0), padx=20, fill="both", expand=True)

        # --- Downloader tab ---
        dl_frame = self._tabs.add("⬇️  Downloader")
        self._download_tab = DownloadTab(
            dl_frame,
            on_complete=self._on_download_complete,
        )
        self._download_tab.pack(fill="both", expand=True)

        # --- History tab ---
        hist_frame = self._tabs.add("📋  History")
        self._history_tab = HistoryTab(hist_frame, history_manager=self._history)
        self._history_tab.pack(fill="both", expand=True)

        # --- Footer -------------------------------------------------------
        footer = ctk.CTkFrame(self, height=28, fg_color="#0d0d0d", corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer,
            text=f"YouTube Downloader  v{APP_VERSION}  •  {APP_AUTHOR}",
            font=ctk.CTkFont(size=11),
            text_color="#555577",
        ).pack(side="left", padx=16)

        ctk.CTkLabel(
            footer,
            text="Powered by yt-dlp",
            font=ctk.CTkFont(size=11),
            text_color="#444466",
        ).pack(side="right", padx=16)

        # Dark/light mode toggle in footer
        self._theme_btn = ctk.CTkButton(
            footer,
            text="☀️ Light",
            width=80,
            height=20,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#2a2a3a",
            text_color="#555577",
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=(0, 8))
        self._is_dark = True

    # ------------------------------------------------------------------
    # Theme toggle
    # ------------------------------------------------------------------

    def _toggle_theme(self) -> None:
        if self._is_dark:
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="🌙 Dark")
            self._is_dark = False
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="☀️ Light")
            self._is_dark = True

    # ------------------------------------------------------------------
    # Cross-tab event bridge
    # ------------------------------------------------------------------

    def _on_download_complete(
        self, title: str, file_path: str, audio_only: bool
    ) -> None:
        """
        Called by DownloadTab when a download finishes successfully.
        Persists the entry and refreshes the history tab.
        """
        self._history.add(
            title=title,
            path=file_path,
            audio_only=audio_only,
        )
        # Refresh history list in case user is already on that tab
        self._history_tab.refresh()
