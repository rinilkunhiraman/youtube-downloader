"""
Entry point — kept intentionally thin.

Run with:
    python main.py
or via uv:
    uv run main.py
"""
import sys
import traceback
from tkinter import messagebox

from src.ui.app import App


def main() -> None:
    try:
        app = App()
        app.mainloop()
    except Exception:
        # Last-resort handler — show a clean dialog instead of a raw traceback
        error = traceback.format_exc()
        try:
            messagebox.showerror(
                "Unexpected Error",
                f"YouTube Downloader crashed unexpectedly.\n\n{error}",
            )
        except Exception:
            print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
