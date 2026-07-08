#!/bin/bash
# Simple launcher script for YouTube Downloader
# Makes the app executable without building a full .app bundle

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run: uv sync"
    exit 1
fi

# Launch with venv python
.venv/bin/python main.py
