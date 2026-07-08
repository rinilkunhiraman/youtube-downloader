#!/bin/bash
# Watch for Python file changes and auto-rebuild the .app
# Requires fswatch: brew install fswatch

if ! command -v fswatch &> /dev/null; then
    echo "❌ fswatch not found. Install with: brew install fswatch"
    exit 1
fi

echo "👀 Watching for Python file changes..."
echo "   Will auto-rebuild .app when you save files"
echo ""

# Do an initial build
./build_app.sh

# Watch for changes in src/ and main.py
fswatch -o src/ main.py | while read event; do
    echo ""
    echo "🔄 File changed, rebuilding..."
    ./build_app.sh
done
