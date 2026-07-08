#!/bin/bash
# Build a standalone macOS .app bundle using PyInstaller
# FFmpeg is bundled inside the .app so users don't need to install it separately.

set -e

echo "🔨 Building YouTube Downloader.app..."

# Install dev dependencies if not present
if ! .venv/bin/python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    uv pip install pyinstaller
fi

# Locate ffmpeg
FFMPEG_PATH=$(which ffmpeg 2>/dev/null || echo "")
if [ -z "$FFMPEG_PATH" ]; then
    echo "❌ ffmpeg not found. Install with: brew install ffmpeg"
    exit 1
fi
echo "📍 Found ffmpeg at: $FFMPEG_PATH"

# Clean previous builds
rm -rf build dist

# Build the .app bundle using --onedir (more reliable for bundling binaries)
# --add-binary copies ffmpeg into the bundle's Contents/MacOS/ folder
.venv/bin/pyinstaller \
    --name "YouTube Downloader" \
    --windowed \
    --onedir \
    --icon assets/icon.png \
    --add-data "assets:assets" \
    --add-binary "$FFMPEG_PATH:." \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "yt_dlp" \
    main.py

# Verify ffmpeg made it in
BUNDLED_FFMPEG="dist/YouTube Downloader.app/Contents/MacOS/ffmpeg"
if [ -f "$BUNDLED_FFMPEG" ]; then
    echo "✅ ffmpeg bundled successfully ($(du -sh "$BUNDLED_FFMPEG" | cut -f1))"
else
    echo "⚠️  ffmpeg not found in bundle — users will need ffmpeg installed"
fi

echo ""
echo "✅ Build complete!"
echo "📦 App bundle: dist/YouTube Downloader.app"
echo "   (FFmpeg is bundled — users don't need to install it)"
echo ""
echo "To run:"
echo "  open 'dist/YouTube Downloader.app'"
