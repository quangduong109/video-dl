import pytest

from yt_dl.sites import detect_site


@pytest.mark.parametrize(
    "url",
    [
        "https://www.facebook.com/watch?v=123",
        "https://facebook.com/user/videos/456",
        "https://m.facebook.com/watch?v=123",
        "https://web.facebook.com/reel/123",
        "https://fb.watch/abcdef/",
        "https://www.fb.com/video.php?v=1",
        "HTTPS://WWW.FACEBOOK.COM/watch?v=1",
        "facebook.com/watch?v=1",  # no scheme
    ],
)
def test_detect_site_facebook(url):
    assert detect_site(url) == "facebook"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=abc",
        "https://youtu.be/abc",
        "https://m.youtube.com/watch?v=abc",
        "https://music.youtube.com/watch?v=abc",
    ],
)
def test_detect_site_youtube(url):
    assert detect_site(url) == "youtube"


def test_detect_site_generic():
    assert detect_site("https://vimeo.com/123456") == "generic"
    assert detect_site("https://example.com/page") == "generic"
