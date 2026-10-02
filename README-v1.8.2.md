# Instagram Public Downloader v1.8.2

Fixed API compatibility with the existing `main.py`.

The previous build exposed:
`download_public_url(url)`

while the existing route calls it with three positional arguments. The function now accepts the legacy extra arguments and keeps the one-click automatic extraction behavior.

Engines:
- gallery-dl for public image/carousel posts
- yt-dlp fallback for public videos/Reels

Private-account access and credential collection are not implemented.
