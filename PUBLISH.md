# Publishing to GitHub

## Step 1: Create a GitHub repo

1. Go to https://github.com/new
2. Name: `youtube-downloader`
3. Description: "A clean, modular YouTube video and audio downloader with a modern GUI"
4. Public or Private: **Public** (for open-source)
5. **Do NOT** initialize with README, .gitignore, or license (we already have them)
6. Click "Create repository"

## Step 2: Push your code

GitHub will show you commands, but here's the exact version:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/youtube-downloader.git

# Push all commits
git push -u origin main
```

## Step 3: Update README links

After pushing, update the README URLs:
1. Edit `README.md`
2. Replace all instances of `YOUR_USERNAME` with your actual GitHub username
3. Commit and push:
   ```bash
   git add README.md CONTRIBUTING.md
   git commit -m "docs: update repo URLs"
   git push
   ```

## Step 4: Create your first release (optional but recommended)

This triggers the GitHub Action to build the .app automatically:

```bash
# Tag the current commit
git tag -a v0.2.0 -m "Initial public release"

# Push the tag
git push origin v0.2.0
```

After a few minutes:
- Go to https://github.com/YOUR_USERNAME/youtube-downloader/releases
- You'll see "YouTube-Downloader-macOS.zip" ready for download

## Step 5: Add topics (optional)

On GitHub, go to your repo → About (gear icon) → Add topics:
- `youtube-downloader`
- `youtube`
- `yt-dlp`
- `customtkinter`
- `macos`
- `python`
- `gui`

## Done! 🎉

Your repo is now live at:
`https://github.com/YOUR_USERNAME/youtube-downloader`

### Next steps:
- Share the link on Reddit (r/Python, r/learnpython)
- Tweet it with #Python #OpenSource
- Add screenshots to the README
- Star your own repo (shameless but effective 😄)
