"""
Reusable CustomTkinter widgets shared across tabs.
"""
from __future__ import annotations

import customtkinter as ctk
from PIL import ImageTk

from src.config import ACCENT_GREEN


# ---------------------------------------------------------------------------
# Thumbnail display
# ---------------------------------------------------------------------------

class ThumbnailWidget(ctk.CTkLabel):
    """
    A label that can display a PIL Image as a thumbnail, or show placeholder text.
    """

    PLACEHOLDER = "Thumbnail will appear here"

    def __init__(self, master, **kwargs):
        super().__init__(master, text=self.PLACEHOLDER, **kwargs)
        self._photo: ImageTk.PhotoImage | None = None

    def set_image(self, pil_image) -> None:
        """Render a PIL Image. Call from the main thread only."""
        self._photo = ImageTk.PhotoImage(pil_image)
        self.configure(image=self._photo, text="")

    def clear(self) -> None:
        self._photo = None
        self.configure(image="", text=self.PLACEHOLDER)


# ---------------------------------------------------------------------------
# Progress section
# ---------------------------------------------------------------------------

class ProgressSection(ctk.CTkFrame):
    """
    A progress bar + status label bundled together.

    Usage::

        ps = ProgressSection(parent)
        ps.set_progress(42.5, speed="1.2 MiB/s", eta="00:12")
        ps.set_status("✅ Done")
        ps.reset()
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.bar = ctk.CTkProgressBar(self, height=22)
        self.bar.pack(pady=8, padx=20, fill="x")
        self.bar.set(0)

        self.label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=14))
        self.label.pack(pady=5)

    def set_progress(
        self,
        percent: float,
        speed: str | None = None,
        eta: str | None = None,
    ) -> None:
        self.bar.set(percent / 100)
        parts = [f"{percent:.1f}%"]
        if speed:
            parts.append(speed)
        if eta:
            parts.append(f"ETA: {eta}")
        self.label.configure(text=" • ".join(parts))

    def set_status(self, msg: str) -> None:
        self.label.configure(text=msg)

    def reset(self) -> None:
        self.bar.set(0)
        self.label.configure(text="Ready")


# ---------------------------------------------------------------------------
# Download button with built-in busy state
# ---------------------------------------------------------------------------

class DownloadButton(ctk.CTkButton):
    """
    A large start-download button that knows about its own busy/idle states.
    """

    _IDLE_TEXT = "⬇️  START DOWNLOAD"
    _BUSY_TEXT = "Downloading…"

    def __init__(self, master, command=None, **kwargs):
        kwargs.setdefault("height", 55)
        kwargs.setdefault("font", ctk.CTkFont(size=18, weight="bold"))
        kwargs.setdefault("fg_color", ACCENT_GREEN)
        super().__init__(master, text=self._IDLE_TEXT, command=command, **kwargs)

    def set_busy(self) -> None:
        self.configure(state="disabled", text=self._BUSY_TEXT)

    def set_idle(self) -> None:
        self.configure(state="normal", text=self._IDLE_TEXT)


# ---------------------------------------------------------------------------
# Section frame with an optional title label
# ---------------------------------------------------------------------------

class SectionFrame(ctk.CTkFrame):
    """
    A padded CTkFrame with an optional bold section title at the top.
    Keeps tab code cleaner by standardising section spacing.
    """

    def __init__(self, master, title: str = "", **kwargs):
        super().__init__(master, **kwargs)
        if title:
            ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
            ).pack(anchor="w", padx=20, pady=(12, 4))


# ---------------------------------------------------------------------------
# Labelled row (label on the left, widget fills the right)
# ---------------------------------------------------------------------------

class LabelledRow(ctk.CTkFrame):
    """
    Horizontal row: fixed-width label on the left, content area on the right.

    Usage::

        row = LabelledRow(parent, label="Save to:")
        ctk.CTkButton(row.content, text="Browse").pack()
    """

    def __init__(self, master, label: str, label_width: int = 90, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=label, width=label_width, anchor="w").pack(
            side="left", padx=(0, 8)
        )
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="x", expand=True)
