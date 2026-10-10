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


from yt_dl.downloader import _needs_cookies


def test_needs_cookies_true_for_login_messages():
    assert _needs_cookies(Exception("Login required"))
    assert _needs_cookies(Exception("Video is private"))
    assert _needs_cookies(Exception("HTTP Error 403: Forbidden"))
    assert _needs_cookies(Exception("Please sign in to continue"))


def test_needs_cookies_true_for_not_available():
    assert _needs_cookies(
        Exception("ERROR: [youtube] 1j2VdrJ3ZDI: This video is not available")
    )


def test_needs_cookies_false_for_other_errors():
    assert not _needs_cookies(Exception("Unable to extract video title"))
    assert not _needs_cookies(Exception("connection timed out"))
