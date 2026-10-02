# Instagram Public Downloader v1.8.1

Fixed the startup error:
`ImportError: cannot import name 'resolve_public_url'`

The extractor now preserves the API expected by `main.py` and serves generated downloads through `/downloads`.

Engines:
- gallery-dl 1.32.13 for public image/carousel posts
- yt-dlp fallback for public videos/Reels

No login credentials are collected and private-account access is not implemented.
