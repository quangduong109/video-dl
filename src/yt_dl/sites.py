"""Site detection and per-site yt-dlp format selection."""

from urllib.parse import urlparse

_FACEBOOK_HOSTS = {
    "facebook.com",
    "m.facebook.com",
    "web.facebook.com",
    "fb.com",
    "fb.watch",
}

_YOUTUBE_HOSTS = {
    "youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def _host(url: str) -> str:
    """Extract the lowercase netloc, stripped of a leading 'www.', tolerating
    URLs that omit the scheme."""
    u = url.lower()
    if "://" not in u:
        u = "//" + u
    host = urlparse(u).netloc
    if host.startswith("www."):
        host = host[4:]
    return host


def detect_site(url: str) -> str:
    """Return 'facebook', 'youtube', or 'generic' based on the URL host."""
    host = _host(url)
    if host in _FACEBOOK_HOSTS:
        return "facebook"
    if host in _YOUTUBE_HOSTS:
        return "youtube"
    return "generic"


_FORMATS = {
    "facebook": {
        "video": "bestvideo*+bestaudio/best",
        "mp3": "bestaudio/best",
    },
    "youtube": {
        "video": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "mp3": "bestaudio/best",
    },
    "generic": {
        "video": "bestvideo*+bestaudio/best",
        "mp3": "bestaudio/best",
    },
}

_DEFAULT = "bestvideo*+bestaudio/best"


def format_for(site: str, fmt: str = "video") -> str:
    """Return the yt-dlp format string for the given site and output format."""
    return _FORMATS.get(site, _FORMATS["generic"]).get(fmt, _DEFAULT)
