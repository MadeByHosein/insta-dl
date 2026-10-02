# Instagram Public Downloader v1.8.3

Fixed:
`cannot unpack non-iterable coroutine object`

The existing FastAPI route expects synchronous return values from the legacy downloader API. v1.8.3 adds synchronous compatibility wrappers around the async extraction engine, so the route can unpack the result normally.

The actual extraction remains automatic:
- gallery-dl for public image/carousel posts
- yt-dlp fallback for public videos/Reels
- multiple files become ZIP
