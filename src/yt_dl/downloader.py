import shutil
from pathlib import Path

import yt_dlp


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


def download(url: str, output_dir: str, fmt: str = "video") -> None:
    check_dependency("ffmpeg")
    check_dependency("deno")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts: dict = {
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook],
    }

    if fmt == "mp3":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }
        ]
    else:
        ydl_opts["format"] = (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def _progress_hook(d: dict) -> None:
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?")
        speed = d.get("_speed_str", "?")
        eta = d.get("_eta_str", "?")
        print(f"\r  Downloading: {percent} at {speed} ETA {eta}", end="", flush=True)
    elif d["status"] == "finished":
        print("\n  Download finished, processing...")
