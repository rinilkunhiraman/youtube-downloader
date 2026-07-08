#!/bin/bash
# Build a standalone macOS .app bundle using PyInstaller

set -e

echo "🔨 Building YouTube Downloader.app..."

# Install dev dependencies if not present
if ! .venv/bin/python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    uv pip install pyinstaller
fi

# Clean previous builds
rm -rf build dist

# Build the .app bundle
.venv/bin/pyinstaller \
    --name "YouTube Downloader" \
    --windowed \
    --onefile \
    --icon assets/icon.png \
    --add-data "assets:assets" \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "yt_dlp" \
    main.py

echo ""
echo "✅ Build complete!"
echo "📦 App bundle: dist/YouTube Downloader.app"
echo ""
echo "To run:"
echo "  open 'dist/YouTube Downloader.app'"
