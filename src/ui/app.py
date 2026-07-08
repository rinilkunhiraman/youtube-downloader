"""
Root application window — wires tabs and shared services together.
"""
from __future__ import annotations

import customtkinter as ctk

from src.config import (
    APP_GEOMETRY,
    APP_MIN_SIZE,
    APP_TITLE,
    APPEARANCE_MODE,
    COLOR_THEME,
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

        # Shared services
        self._history = HistoryManager()

        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(pady=10, padx=20, fill="both", expand=True)

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
