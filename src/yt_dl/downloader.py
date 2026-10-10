import shutil
from pathlib import Path

import yt_dlp

from .sites import detect_site, format_for


def check_dependency(name: str) -> None:
    if not shutil.which(name):
        labels = {
            "ffmpeg": (
                "ffmpeg is required for downloading and converting media.\n"
                "Install it with:\n"
                "  macOS:   brew install ffmpeg\n"
                "  Ubuntu:  sudo apt install ffmpeg\n"
                "  Windows: winget install ffmpeg"
            ),
            "deno": (
                "deno is required by yt-dlp for YouTube extraction.\n"
                "Install it with:\n"
                "  macOS/Linux: curl -fsSL https://deno.land/install.sh | sh\n"
                "  Windows:     irm https://deno.land/install.ps1 | iex\n"
                "  Or visit:    https://docs.deno.com/runtime/getting_started/"
            ),
        }
        print(f"Error: {labels.get(name, f'{name} is required.')}")
        raise SystemExit(1)


def required_deps(site: str) -> list[str]:
    """External tools needed for the given site. deno is YouTube-only."""
    deps = ["ffmpeg"]
    if site == "youtube":
        deps.append("deno")
    return deps


def build_ydl_opts(
    url: str,
    fmt: str,
    output_path: Path,
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
) -> dict:
    """Build the yt-dlp options dict (pure: no network, no side effects)."""
    site = detect_site(url)
    opts: dict = {
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook],
        "format": format_for(site, fmt),
    }
    if fmt == "mp3":
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }
        ]
    if cookies:
        opts["cookiefile"] = cookies
    elif cookies_from_browser:
        opts["cookiesfrombrowser"] = (cookies_from_browser,)
    return opts


def _needs_cookies(exc: BaseException) -> bool:
    """True when an exception message suggests authentication is required."""
    msg = str(exc).lower()
    return any(
        k in msg
        for k in ("login", "private", "sign in", "authorize", "403", "not available")
    )


def download(
    url: str,
    output_dir: str,
    fmt: str = "video",
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
) -> None:
    site = detect_site(url)
    for dep in required_deps(site):
        check_dependency(dep)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = build_ydl_opts(url, fmt, output_path, cookies, cookies_from_browser)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        if _needs_cookies(e) and not (cookies or cookies_from_browser):
            print(
                "\n  HD/private video needs cookies — "
                "try --cookies-from-browser chrome"
            )
        raise


def _progress_hook(d: dict) -> None:
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?")
        speed = d.get("_speed_str", "?")
        eta = d.get("_eta_str", "?")
        print(f"\r  Downloading: {percent} at {speed} ETA {eta}", end="", flush=True)
    elif d["status"] == "finished":
        print("\n  Download finished, processing...")
