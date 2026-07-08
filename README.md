# YouTube Downloader

A clean, modular YouTube video and audio downloader with a modern GUI built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features

- 🎥 **Download videos** in best quality (video+audio merged)
- 🎵 **Extract audio** as MP3 files
- 🖼️ **Live preview** with thumbnail, duration, and uploader info
- 📋 **Download history** with search, per-item delete, and clear all
- 🔍 **Search history** as you type
- 📂 **Quick access** to downloaded files via "Open Folder" button
- 📱 **WhatsApp sharing** built-in (macOS/Windows/Linux)
- ⌨️ **Keyboard shortcuts** — press Enter to fetch video info
- 🌙 **Dark mode** UI with responsive layout

## Installation

### Requirements

- Python 3.13+ (or Python 3.10+ should work)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install with uv

```bash
git clone <your-repo-url>
cd youtube-downloader
uv sync
```

### Install with pip

```bash
git clone <your-repo-url>
cd youtube-downloader
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt  # or install dependencies manually
```

## Usage

### Run the app

```bash
# With uv (recommended)
uv run main.py

# With standard Python
python main.py
```

### Basic workflow

1. **Paste a YouTube URL** into the input field
2. **Click "Fetch Info"** (or press Enter) to load video metadata
3. **Choose your options:**
   - Check "🎵 Audio Only (MP3)" if you only want audio
   - Click "Change Folder" to select a different save location
4. **Click "⬇️ START DOWNLOAD"** and watch the progress
5. **Access your downloads** via the History tab

### Optional: Cookie file

If you're downloading age-restricted or members-only videos, you can export your browser cookies:

1. Export cookies from your browser using a cookie extension (e.g., [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid))
2. Save as `cookies.txt` in the project root
3. The downloader will automatically detect and use it

## Project Structure

```
youtube-downloader/
├── main.py                   # Entry point
├── src/
│   ├── config.py             # App-wide constants and settings
│   ├── downloader.py         # Core yt-dlp download logic (UI-agnostic)
│   ├── history.py            # Download history management
│   ├── utils.py              # File operations, sharing, thumbnail fetching
│   └── ui/
│       ├── app.py            # Main application window
│       ├── components.py     # Reusable UI widgets
│       ├── download_tab.py   # Download tab UI
│       └── history_tab.py    # History tab UI
├── cookies.txt               # Optional: browser cookies for restricted content
├── download_history.json     # Auto-generated download history
└── pyproject.toml            # Python project config
```

## Architecture Highlights

- **Modular design** — business logic is fully decoupled from the UI
- **Thread safety** — all downloader callbacks are dispatched to the main thread via `after(0, ...)`
- **No tkinter in core modules** — `downloader.py` and `history.py` can be reused in CLI or web versions
- **Clean separation** — each module has a single, well-defined responsibility

## Dependencies

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — YouTube video/audio extraction
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** — Modern CTk-based GUI
- **[Pillow](https://python-pillow.org/)** — Image processing for thumbnails
- **[requests](https://requests.readthedocs.io/)** — HTTP requests for thumbnails

## Development

### Adding new features

- **New download format?** → Update `src/downloader.py` and `src/config.py`
- **New UI widget?** → Add to `src/ui/components.py`
- **Change app theme/colors?** → Edit `src/config.py`
- **Add more sharing options?** → Extend `src/utils.py`

### Running tests

(Tests not yet implemented — PRs welcome!)

## Troubleshooting

### "ModuleNotFoundError: No module named 'customtkinter'"

Make sure you've installed dependencies:

```bash
uv sync  # or pip install -r requirements.txt
```

### Downloads fail with "HTTP Error 403"

Some videos require authentication. Export cookies from your browser and save as `cookies.txt` in the project root.

### "WhatsApp share" doesn't work

- **macOS:** Make sure WhatsApp Desktop is installed
- **Windows:** WhatsApp Desktop must be installed and associated with `whatsapp:` URLs
- **Linux:** Depends on your desktop environment's URL handler setup

### App doesn't launch on macOS

If you see a "Python" quit unexpectedly error, you may need Tkinter support. Install Python via Homebrew:

```bash
brew install python-tk@3.13
```

## License

MIT (or your preferred license)

## Contributing

PRs welcome! Feel free to open issues for bugs or feature requests.

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the amazing download engine
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the beautiful modern UI toolkit
