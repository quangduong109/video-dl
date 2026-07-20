from pathlib import Path

from yt_dl.downloader import build_ydl_opts, required_deps


def test_required_deps_youtube_needs_deno():
    assert required_deps("youtube") == ["ffmpeg", "deno"]


def test_required_deps_facebook_skips_deno():
    assert required_deps("facebook") == ["ffmpeg"]


def test_required_deps_generic_skips_deno():
    assert required_deps("generic") == ["ffmpeg"]


def test_build_ydl_opts_facebook_video_format():
    opts = build_ydl_opts(
        "https://www.facebook.com/watch?v=1", "video", Path("/tmp/out")
    )
    assert opts["format"] == "bestvideo*+bestaudio/best"
    assert opts["outtmpl"] == str(Path("/tmp/out") / "%(title)s.%(ext)s")
    assert "cookiefile" not in opts
    assert "cookiesfrombrowser" not in opts


def test_build_ydl_opts_youtube_video_format_unchanged():
    opts = build_ydl_opts("https://youtu.be/abc", "video", Path("/tmp/out"))
    assert opts["format"] == "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"


def test_build_ydl_opts_mp3_adds_postprocessor():
    opts = build_ydl_opts("https://youtu.be/abc", "mp3", Path("/tmp/out"))
    assert opts["format"] == "bestaudio/best"
    assert opts["postprocessors"] == [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",
        }
    ]


def test_build_ydl_opts_cookies_file():
    opts = build_ydl_opts(
        "https://www.facebook.com/watch?v=1",
        "video",
        Path("/tmp/out"),
        cookies="/path/to/cookies.txt",
    )
    assert opts["cookiefile"] == "/path/to/cookies.txt"
    assert "cookiesfrombrowser" not in opts


def test_build_ydl_opts_cookies_from_browser():
    opts = build_ydl_opts(
        "https://www.facebook.com/watch?v=1",
        "video",
        Path("/tmp/out"),
        cookies_from_browser="chrome",
    )
    assert opts["cookiesfrombrowser"] == ("chrome",)
    assert "cookiefile" not in opts
