# Contributing to YouTube Downloader

Thanks for your interest in contributing! This project welcomes contributions of all kinds.

## Quick Start

1. Fork the repo
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/youtube-downloader.git`
3. Install dependencies: `uv sync`
4. Make your changes
5. Test: `make dev` to verify everything works
6. Commit with clear messages
7. Push and open a Pull Request

## Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
cd youtube-downloader

# Install dependencies
uv sync

# Run in development mode
make dev
```

## Code Style

- Follow existing code structure (modular, UI-agnostic business logic)
- Add docstrings to public functions
- Keep UI code in `src/ui/`, business logic outside it
- Use type hints where helpful

## What to Contribute

**Good first issues:**
- Add tests (we have none yet!)
- Improve error messages
- Add more quality presets
- Support for playlists
- Subtitle download options

**Bigger features:**
- Batch download queue
- Auto-update via Sparkle framework
- Linux/Windows packaging scripts
- Dark/light theme toggle
- Download resume after interruption

## Pull Request Process

1. Update the README if you add user-facing features
2. Ensure `make test` passes (once we have tests)
3. Keep PRs focused — one feature/fix per PR
4. Write a clear PR description explaining what and why

## Questions?

Open an issue or discussion — we're friendly!
