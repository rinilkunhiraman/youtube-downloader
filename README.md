# YouTube Downloader

A clean, modular YouTube video and audio downloader with a modern GUI built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

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

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- FFmpeg (required for video conversion and stream merging)

### Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

### Install with uv

```bash
git clone https://github.com/rinilkunhiraman/youtube-downloader.git
cd youtube-downloader
uv sync
```

### Install with pip

```bash
git clone https://github.com/rinilkunhiraman/youtube-downloader.git
cd youtube-downloader
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install customtkinter pillow requests yt-dlp
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

### Quick reference

```bash
make dev      # Run in dev mode (instant code updates)
make build    # Build .app bundle
make clean    # Remove build artifacts
make install  # Sync dependencies
```

### Development workflow

**During active coding:**
```bash
make dev
# or just: ./launch.sh
```
This runs the app directly from source. Every time you restart it, it picks up your latest code changes immediately — no rebuild needed.

**Testing the packaged .app:**
```bash
make build
open "dist/YouTube Downloader.app"
```
This creates a standalone `.app` bundle. You must rebuild every time you change code if you want the `.app` to reflect those changes.

**Auto-rebuild on save (optional):**
```bash
# First install fswatch
brew install fswatch

# Then run the watcher
./watch_and_rebuild.sh
```
This watches your Python files and automatically rebuilds the `.app` whenever you save. Great for testing the packaged version during development.

### Adding new features

- **New download format?** → Update `src/downloader.py` and `src/config.py`
- **New UI widget?** → Add to `src/ui/components.py`
- **Change app theme/colors?** → Edit `src/config.py`
- **Add more sharing options?** → Extend `src/utils.py`

### Running tests

(Tests not yet implemented — PRs welcome!)

### How do real apps update themselves?

You asked: "How do we update the code and make it reflect in the app just like the real app?"

**During development:**
- Run `make dev` — picks up changes instantly, no rebuild
- Or use `./watch_and_rebuild.sh` to auto-rebuild the `.app` on every save

**For distribution (like App Store apps):**
Real apps use one of these strategies:
1. **Manual rebuild + distribute** — rebuild with `make build`, then share the new `.app` (what we're doing now)
2. **Auto-update frameworks** — integrate [Sparkle](https://sparkle-project.org/) (macOS) or similar to check for updates on launch
3. **App Store** — Apple handles updates automatically
4. **CI/CD pipeline** — GitHub Actions rebuilds and uploads new versions on every commit

For a simple project like this, **option 1** (manual rebuild) is cleanest. If you want auto-updates later, add Sparkle or publish via the Mac App Store.

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

**Error:** "Apple could not verify 'YouTube Downloader' is free of malware"

This happens because the app isn't code-signed (requires a paid Apple Developer account).

**Fix:**
1. Right-click (or Control+click) the app → select "Open"
2. Click "Open" in the security dialog
3. The app will now open, and you won't see this warning again

**Alternative via Terminal:**
```bash
xattr -d com.apple.quarantine "/path/to/YouTube Downloader.app"
```

**Why this happens:** macOS Gatekeeper blocks all unsigned apps by default. Code signing requires a $99/year Apple Developer membership.

## License

MIT (or your preferred license)

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Some good first contributions:
- Add tests
- Playlist support
- Subtitle download options
- Linux/Windows packaging scripts

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the amazing download engine
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the beautiful modern UI toolkit
