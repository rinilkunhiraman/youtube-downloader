"""
Entry point — kept intentionally thin.

Run with:
    python main.py
or via uv:
    uv run main.py
"""
from src.ui.app import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
