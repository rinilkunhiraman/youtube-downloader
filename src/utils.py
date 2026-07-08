"""
Platform utilities — file operations, sharing, thumbnail fetching.

No UI imports here; all functions return data or raise exceptions so the
UI layer can decide how to present results/errors.
"""
import os
import subprocess
import sys
from io import BytesIO
from typing import Optional

import requests
from PIL import Image

from src.config import THUMBNAIL_SIZE


# ---------------------------------------------------------------------------
# File / folder helpers
# ---------------------------------------------------------------------------


def reveal_in_finder(file_path: str) -> None:
    """
    Open the folder containing *file_path* in the system file manager.
    Works on macOS, Linux, and Windows.
    """
    folder = os.path.dirname(os.path.abspath(file_path))
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    if sys.platform == "darwin":
        # Select the file inside Finder when it exists
        if os.path.exists(file_path):
            subprocess.run(["open", "-R", file_path], check=True)
        else:
            subprocess.run(["open", folder], check=True)
    elif sys.platform == "win32":
        subprocess.run(["explorer", f"/select,{file_path}"], check=False)
    else:
        subprocess.run(["xdg-open", folder], check=True)


def open_file(file_path: str) -> None:
    """Open *file_path* with the default system application."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if sys.platform == "darwin":
        subprocess.run(["open", file_path], check=True)
    elif sys.platform == "win32":
        os.startfile(file_path)  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", file_path], check=True)


def format_file_size(num_bytes: int) -> str:
    """Human-readable file size string (e.g. '12.3 MB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024  # type: ignore[assignment]
    return f"{num_bytes:.1f} PB"


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Replace characters that are illegal in file names across common OSes."""
    illegal = r'\/:*?"<>|'
    for ch in illegal:
        name = name.replace(ch, replacement)
    return name.strip()


# ---------------------------------------------------------------------------
# Sharing
# ---------------------------------------------------------------------------


def share_to_whatsapp(file_path: str) -> None:
    """
    Attempt to open WhatsApp Desktop and pass *file_path* to it.

    Raises:
        FileNotFoundError  if the file doesn't exist.
        RuntimeError       if WhatsApp cannot be opened.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if sys.platform == "darwin":
            subprocess.run(["open", "-a", "WhatsApp", file_path], check=True)
        elif sys.platform == "win32":
            subprocess.run(["start", "whatsapp:", file_path], shell=True, check=True)
        else:
            subprocess.run(["xdg-open", f"whatsapp://send?file={file_path}"], check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Could not open WhatsApp. Make sure WhatsApp Desktop is installed."
        ) from exc


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


def fetch_thumbnail(
    url: str,
    size: tuple[int, int] = THUMBNAIL_SIZE,
    timeout: int = 10,
) -> Optional[Image.Image]:
    """
    Download and resize a thumbnail image.

    Returns:
        A PIL Image resized to *size*, or None if the download fails.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.resize(size, Image.Resampling.LANCZOS)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Duration formatting
# ---------------------------------------------------------------------------


def format_duration(seconds: Optional[int]) -> str:
    """Convert a raw seconds integer to 'H:MM:SS' or 'M:SS'."""
    if not seconds:
        return "Unknown"
    h, remainder = divmod(int(seconds), 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
