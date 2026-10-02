import asyncio
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOWNLOAD_ROOT = PROJECT_ROOT / "downloads"
DOWNLOAD_ROOT.mkdir(exist_ok=True)


def normalize_url(url: str) -> str:
    p = urlparse(str(url).strip())
    if p.scheme not in ("http", "https") or p.netloc.lower() not in {
        "instagram.com", "www.instagram.com", "m.instagram.com"
    }:
        raise HTTPException(status_code=400, detail="Only public Instagram URLs are supported.")
    return f"https://www.instagram.com{p.path.rstrip('/')}/"


def _good_media_url(url: str) -> bool:
    if not url:
        return False
    u = url.lower()
    # Exclude Instagram UI/static assets and obvious avatars.
    bad = (
        "profile_pic", "profilepic", "avatar", "s150x150", "s320x320",
        "instagram_glyph", "instagram_logo", "favicon", "sprite",
        "emoji", "static.cdninstagram", "static.xx.fbcdn"
    )
    if any(x in u for x in bad):
        return False
    return "cdninstagram.com" in u or "fbcdn.net" in u


async def _browser_collect(url: str):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Playwright is not installed. Run: pip install -r backend\\requirements.txt"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            proxy={"server": "http://127.0.0.1:10809"}
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 1000},
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            await page.goto(normalize_url(url), wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4500)
# موقت
            html = await page.content()

            with open("instagram_debug.html", "w", encoding="utf-8") as f:
                f.write(html)

            print("HTML SAVED", len(html))
            if "/accounts/login" in page.url.lower():
                raise HTTPException(
                    status_code=502,
                    detail="Instagram redirected the public request to login."
                )

            # Instagram may not expose the post inside an <article>.
            # Use article -> main -> body as progressively broader scopes.
            article = page.locator("article").first
            if await article.count() > 0:
                scope = article
            else:
                main = page.locator("main").first
                if await main.count() > 0:
                    scope = main
                else:
                    scope = page.locator("body")

            found = []

            async def collect_visible_media():
                for img in await scope.locator("img").all():
                    try:
                        box = await img.bounding_box()
                        src = await img.get_attribute("src")
                        srcset = await img.get_attribute("srcset")
                    except Exception:
                        continue

                    if not box:
                        continue

                    if box["width"] < 180 or box["height"] < 180:
                        continue

                    candidates = []
                    if src:
                        candidates.append(src)

                    if srcset:
                        for part in srcset.split(","):
                            candidate = part.strip().split(" ")[0]
                            if candidate:
                                candidates.append(candidate)

                    for candidate in candidates:
                        if _good_media_url(candidate):
                            found.append(candidate)

                for video in await scope.locator("video").all():
                    try:
                        box = await video.bounding_box()
                        src = await video.get_attribute("src")
                    except Exception:
                        continue

                    if src and box and box["width"] >= 180 and box["height"] >= 180:
                        if _good_media_url(src):
                            found.append(src)

            await collect_visible_media()

            # For carousels, look for Instagram's next-slide controls.
            for _ in range(20):
                before = len(set(found))
                buttons = await page.locator("button").all()
                next_button = None

                for b in buttons:
                    try:
                        aria = (await b.get_attribute("aria-label") or "").lower()
                        title = (await b.get_attribute("title") or "").lower()
                        txt = (await b.inner_text()).strip().lower()
                    except Exception:
                        continue

                    label = f"{aria} {title} {txt}"

                    if any(k in label for k in (
                        "next", "بعدی", "right", "next slide"
                    )):
                        next_button = b
                        break

                if next_button is None:
                    break

                try:
                    await next_button.click(timeout=1500)
                    await page.wait_for_timeout(1500)
                    await collect_visible_media()
                except Exception:
                    break

                after = len(set(found))
                if after == before:
                    break

            result = []
            seen = set()

            for u in found:
                if u not in seen:
                    seen.add(u)
                    result.append(u)
            if not result:
                raise HTTPException(
                    status_code=502,
                    detail="No post images or videos were exposed by Instagram."
                )

            return result
        finally:
            await context.close()
            await browser.close()


async def _download_media(urls):
    stamp = str(time.time_ns())
    outdir = DOWNLOAD_ROOT / stamp
    outdir.mkdir(parents=True, exist_ok=True)

    items = []
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=60,
        headers={"User-Agent": "Mozilla/5.0"},
    ) as client:
        for n, url in enumerate(urls, 1):
            try:
                r = await client.get(url)
                if r.status_code != 200 or not r.content:
                    continue

                ctype = r.headers.get("content-type", "").lower()
                if "video" in ctype or ".mp4" in url.lower():
                    ext = ".mp4"
                    kind = "video"
                elif "png" in ctype or ".png" in url.lower():
                    ext = ".png"
                    kind = "image"
                elif "webp" in ctype or ".webp" in url.lower():
                    ext = ".webp"
                    kind = "image"
                else:
                    ext = ".jpg"
                    kind = "image"

                path = outdir / f"{len(items)+1:02d}{ext}"
                path.write_bytes(r.content)
                items.append({
                    "index": len(items),
                    "filename": path.name,
                    "url": f"/downloads/{outdir.name}/{path.name}",
                    "type": kind,
                })
            except Exception:
                continue

    if not items:
        raise HTTPException(status_code=502, detail="Media could not be downloaded.")

    return items


async def extract_gallery(url: str):
    urls = await _browser_collect(url)
    return await _download_media(urls)


# Legacy functions are retained for compatibility with the older API.
def resolve_public_url(url: str, *args, **kwargs):
    return {"url": normalize_url(url), "supported": True}


def download_public_url(url: str, *args, **kwargs):
    # Intentionally returns one individual media file, never a ZIP.
    async def run():
        items = await extract_gallery(url)
        first = items[0]
        return str(DOWNLOAD_ROOT / Path(first["url"]).parts[-2] / first["filename"]), first["filename"], None
    return asyncio.run(run())


def download_instagram(url: str):
    return download_public_url(url)



