.PHONY: help dev build clean install test

help:
	@echo "YouTube Downloader - Development Commands"
	@echo ""
	@echo "  make dev       - Run app in development mode (picks up code changes instantly)"
	@echo "  make build     - Build standalone .app bundle (for distribution)"
	@echo "  make clean     - Remove build artifacts"
	@echo "  make install   - Install/sync dependencies"
	@echo "  make test      - Run import tests"
	@echo ""

dev:
	@echo "🚀 Launching in development mode..."
	./launch.sh

build:
	@echo "📦 Building distributable .app bundle..."
	./build_app.sh

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist *.spec
	@echo "✅ Clean complete"

install:
	@echo "📥 Installing dependencies..."
	uv sync
	@echo "✅ Dependencies installed"

test:
	@echo "🧪 Testing imports..."
	@.venv/bin/python -c "import sys; sys.path.insert(0, '.'); from src.ui.app import App; print('✅ All imports OK')"
