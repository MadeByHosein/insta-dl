# Instagram Public Downloader v1.9

Browser-based public extractor.

This version no longer relies on raw `requests` HTML extraction as the primary path.
It launches Playwright Chromium, opens the public Instagram URL, reads media exposed
by the rendered page, then downloads the media and creates a ZIP for multiple files.

Install:
    .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    .\.venv\Scripts\python.exe -m playwright install chromium

The extractor does not collect Instagram usernames/passwords and does not implement
private-account access.
