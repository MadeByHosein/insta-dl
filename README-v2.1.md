# Instagram Public Downloader v2.1

The homepage no longer uses the old `/api/quick-download` endpoint.

New behavior:
- URL -> `/api/gallery`
- Show each post media item in a gallery
- Individual download button per item
- No automatic ZIP download from the homepage
- Avoid srcset-resolution duplicates
- Only media found inside the Instagram post article is considered
