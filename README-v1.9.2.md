# Instagram Public Downloader v1.9.2

Fixed:
`too many values to unpack (expected 3, got 5)`

The existing `main.py` route expects exactly three values from
`download_public_url()`:
1. path
2. filename
3. temp_dir

The browser extractor now returns that exact legacy tuple while keeping
the internal result metadata private to the extractor.
