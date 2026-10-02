# Instagram Downloader v2.2

Clean rebuild of the local API/frontend.

Important:
- The homepage has NO `/api/quick-download` call.
- The homepage has NO ZIP download logic.
- The only download flow is `/api/gallery`.
- Each returned post media item is shown individually with its own download link.
- Profile/avatar/UI images are filtered by rendered size and URL patterns.
- Carousel navigation is attempted to collect separate slides.
- Public Instagram content only.
