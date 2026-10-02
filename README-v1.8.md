# Instagram Public Downloader v1.8

Windows-ready public Instagram downloader.

## What changed
- Added `gallery-dl==1.32.13` as the primary extractor for image/carousel posts.
- Kept `yt-dlp` as a fallback for video/Reels.
- One URL + one Download button; no user mode selection.
- Multiple media files are automatically returned as a ZIP.
- No username/password fields and no private-account access.

## Important
Instagram changes its public endpoints frequently. If Instagram redirects an anonymous request to login, the app reports that instead of pretending the URL is downloadable.

For local testing:
```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Then run the existing Windows launcher from this package.
