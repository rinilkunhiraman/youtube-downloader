"""
Download history — load, save, and query past downloads.

Completely UI-agnostic; returns plain dicts the UI layer can render however it wants.
"""
import json
import os
from datetime import datetime
from typing import Optional

from src.config import HISTORY_FILE


class HistoryEntry:
    """Represents a single download history record."""

    __slots__ = ("title", "path", "url", "media_type", "date")

    def __init__(
        self,
        title: str,
        path: str,
        media_type: str,
        date: str,
        url: str = "",
    ):
        self.title = title
        self.path = path
        self.url = url
        self.media_type = media_type  # "Video" | "Audio (MP3)"
        self.date = date

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "path": self.path,
            "url": self.url,
            "type": self.media_type,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(
            title=d.get("title", "Unknown"),
            path=d.get("path", ""),
            url=d.get("url", ""),
            media_type=d.get("type", "Video"),
            date=d.get("date", ""),
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HistoryEntry {self.media_type!r} {self.title!r}>"


class HistoryManager:
    """
    Manages a JSON-backed list of HistoryEntry objects.

    Usage::

        hm = HistoryManager()
        hm.add(title="...", path="...", url="...", audio_only=False)
        for entry in hm.entries:
            print(entry.title)
        hm.clear()
    """

    def __init__(self, history_file: str = HISTORY_FILE):
        self._file = history_file
        self._entries: list[HistoryEntry] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[HistoryEntry]:
        """Return entries newest-first (read-only view)."""
        return list(self._entries)

    def add(
        self,
        title: str,
        path: str,
        audio_only: bool,
        url: str = "",
        date: Optional[str] = None,
    ) -> HistoryEntry:
        """Prepend a new entry and persist immediately."""
        entry = HistoryEntry(
            title=title,
            path=path,
            url=url,
            media_type="Audio (MP3)" if audio_only else "Video",
            date=date or datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        self._entries.insert(0, entry)
        self._save()
        return entry

    def remove(self, index: int) -> None:
        """Delete the entry at *index* (0 = newest) and persist."""
        if 0 <= index < len(self._entries):
            self._entries.pop(index)
            self._save()

    def clear(self) -> None:
        """Wipe all history and persist."""
        self._entries.clear()
        self._save()

    def search(self, query: str) -> list[HistoryEntry]:
        """Case-insensitive title search."""
        q = query.lower()
        return [e for e in self._entries if q in e.title.lower()]

    def __len__(self) -> int:
        return len(self._entries)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not os.path.exists(self._file):
            return
        try:
            with open(self._file, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._entries = [HistoryEntry.from_dict(d) for d in raw]
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file — start fresh rather than crashing
            self._entries = []

    def _save(self) -> None:
        try:
            with open(self._file, "w", encoding="utf-8") as fh:
                json.dump(
                    [e.to_dict() for e in self._entries],
                    fh,
                    indent=2,
                    ensure_ascii=False,
                )
        except OSError as exc:
            # Non-fatal — history just won't persist this time
            print(f"[HistoryManager] Could not save history: {exc}")
