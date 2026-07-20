import pytest

from yt_dl.cli import main


def test_cookies_from_browser_choice_is_accepted(monkeypatch):
    captured = {}

    def fake_download(url, output_dir, fmt, cookies=None, cookies_from_browser=None):
        captured.update(
            url=url,
            fmt=fmt,
            cookies=cookies,
            cookies_from_browser=cookies_from_browser,
        )

    monkeypatch.setattr("yt_dl.cli.download", fake_download)
    main(["https://fb.watch/abc/", "--cookies-from-browser", "firefox"])
    assert captured["cookies_from_browser"] == "firefox"
    assert captured["cookies"] is None


def test_both_cookie_flags_rejected(monkeypatch):
    monkeypatch.setattr("yt_dl.cli.download", lambda *a, **k: None)
    with pytest.raises(SystemExit):
        main(
            [
                "https://fb.watch/abc/",
                "--cookies",
                "cookies.txt",
                "--cookies-from-browser",
                "chrome",
            ]
        )


def test_invalid_browser_rejected(monkeypatch):
    monkeypatch.setattr("yt_dl.cli.download", lambda *a, **k: None)
    with pytest.raises(SystemExit):
        main(
            [
                "https://fb.watch/abc/",
                "--cookies-from-browser",
                "internet-explorer",
            ]
        )
