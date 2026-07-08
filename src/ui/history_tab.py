"""
History tab — scrollable list of past downloads with search, open, share, and delete.
"""
from __future__ import annotations

from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

from src.config import HISTORY_TITLE_MAX_LEN, WHATSAPP_GREEN
from src.history import HistoryEntry, HistoryManager
from src.utils import reveal_in_finder, share_to_whatsapp


class HistoryTab(ctk.CTkFrame):
    """
    Self-contained history tab widget.

    Args:
        master:          Parent widget.
        history_manager: Shared HistoryManager instance.
    """

    def __init__(self, master, history_manager: HistoryManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._hm = history_manager
        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build(self) -> None:
        # --- Header row ---
        header = ctk.CTkFrame(self)
        header.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            header,
            text="Download History",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header, text="Clear All", width=100, fg_color="#cc3333",
            command=self._clear_all,
        ).pack(side="right", padx=(4, 20))

        ctk.CTkButton(
            header, text="Refresh", width=100, command=self.refresh,
        ).pack(side="right", padx=4)

        # --- Search bar ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(padx=20, pady=(0, 8), fill="x")

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh())

        ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            placeholder_text="🔍  Search history…",
            height=36,
        ).pack(fill="x", padx=0)

        # --- Scrollable list ---
        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.pack(pady=4, padx=20, fill="both", expand=True)

        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Re-render the list from the HistoryManager (call after adding entries)."""
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        query = self._search_var.get().strip() if hasattr(self, "_search_var") else ""
        entries = self._hm.search(query) if query else self._hm.entries

        if not entries:
            msg = "No results found." if query else "No downloads yet."
            ctk.CTkLabel(
                self._list_frame,
                text=msg,
                font=ctk.CTkFont(size=16),
                text_color="gray",
            ).pack(pady=50)
            return

        for idx, entry in enumerate(entries):
            self._render_entry(idx, entry)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render_entry(self, idx: int, entry: HistoryEntry) -> None:
        row = ctk.CTkFrame(self._list_frame)
        row.pack(pady=5, padx=8, fill="x")

        # Left: info text
        short_title = (
            entry.title[:HISTORY_TITLE_MAX_LEN] + "…"
            if len(entry.title) > HISTORY_TITLE_MAX_LEN
            else entry.title
        )
        info_text = f"{entry.date}  •  {entry.media_type}\n{short_title}"
        ctk.CTkLabel(
            row,
            text=info_text,
            anchor="w",
            justify="left",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=15, pady=10, fill="x", expand=True)

        # Right: action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=6)

        ctk.CTkButton(
            btn_frame,
            text="Open Folder",
            width=95,
            height=32,
            command=lambda e=entry: self._open_folder(e),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="Share",
            width=70,
            height=32,
            fg_color=WHATSAPP_GREEN,
            command=lambda e=entry: self._share(e),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame,
            text="✕",
            width=32,
            height=32,
            fg_color="#555",
            hover_color="#cc3333",
            command=lambda i=idx: self._delete_entry(i),
        ).pack(side="left", padx=3)

    def _open_folder(self, entry: HistoryEntry) -> None:
        try:
            reveal_in_finder(entry.path)
        except FileNotFoundError:
            messagebox.showerror(
                "Not Found",
                f"The file no longer exists:\n{entry.path}",
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _share(self, entry: HistoryEntry) -> None:
        try:
            share_to_whatsapp(entry.path)
            messagebox.showinfo(
                "Share via WhatsApp",
                "The file has been revealed in Finder and WhatsApp is open.\n\n"
                "Drag the file into any WhatsApp chat to send it.",
            )
        except FileNotFoundError:
            messagebox.showerror("Not Found", f"File not found:\n{entry.path}")
        except RuntimeError as exc:
            if str(exc) == "whatsapp_web":
                messagebox.showinfo(
                    "WhatsApp Web Opened",
                    "WhatsApp Desktop wasn't found.\n\n"
                    "WhatsApp Web has been opened in your browser.\n"
                    "The file is revealed in Finder — drag it into a chat to send.",
                )
            else:
                messagebox.showerror("Share Failed", str(exc))

    def _delete_entry(self, idx: int) -> None:
        self._hm.remove(idx)
        self.refresh()

    def _clear_all(self) -> None:
        if not self._hm.entries:
            return
        if messagebox.askyesno(
            "Clear History",
            "Delete all download history? This cannot be undone.",
        ):
            self._hm.clear()
            self.refresh()
