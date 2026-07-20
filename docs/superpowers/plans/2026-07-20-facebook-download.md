# Facebook Video Download (Best Quality) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Facebook video download at best quality (HD via cookies) to the multi-site `yt-dl` CLI, auto-detecting the site from the URL.

**Architecture:** A new pure module `sites.py` detects the site (facebook/youtube/generic) and returns the optimal yt-dlp `format` string. `downloader.py` is refactored so option-building (`build_ydl_opts`) and dependency selection (`required_deps`) are pure, testable helpers; the thin `download()` wrapper wires them plus cookies. `cli.py` adds `--cookies` and `--cookies-from-browser` flags.

**Tech Stack:** Python 3.10+, `yt-dlp` (existing), `pytest` (new dev dep), argparse.

**Reference spec:** `docs/superpowers/specs/2026-07-20-facebook-download-design.md`

---

## File Structure

- Create: `src/yt_dl/sites.py` — site detection + per-site format selection (pure)
- Create: `tests/__init__.py` — empty, makes `tests` a package
- Create: `tests/test_sites.py` — unit tests for detect_site / format_for
- Create: `tests/test_downloader.py` — unit tests for build_ydl_opts / required_deps / _needs_cookies
- Create: `tests/test_cli.py` — unit tests for argparse cookie-flag validation
- Modify: `src/yt_dl/downloader.py` — add helpers, wire site-aware format + deps + cookies + login hint
- Modify: `src/yt_dl/cli.py` — add `--cookies`, `--cookies-from-browser`, validation
- Modify: `src/yt_dl/batch.py` — accept and forward cookies args
- Modify: `pyproject.toml` — add pytest dev dependency + pytest config
- Modify: `README.md` — Facebook section + deno-is-YouTube-only note

---

## Task 1: Test infrastructure

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Add pytest dev dependency + config to `pyproject.toml`**

Append after the `[build-system]` table:

```toml

[project.optional-dependencies]
dev = [
    "pytest>=8",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

- [ ] **Step 2: Create empty `tests/__init__.py`**

```python
```
(empty file)

- [ ] **Step 3: Create a smoke test `tests/test_smoke.py`**

```python
def test_pytest_runs():
    assert 1 + 1 == 2
```

- [ ] **Step 4: Install the package with dev deps and run pytest**

Run: `pip install -e ".[dev]"`
Run: `pytest -q`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/
git commit -m "test: add pytest dev dependency and test harness"
```

---

## Task 2: `sites.detect_site()`

**Files:**
- Create: `src/yt_dl/sites.py`
- Test: `tests/test_sites.py`

- [ ] **Step 1: Write the failing tests for `detect_site`**

Create `tests/test_sites.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sites.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'yt_dl.sites'`

- [ ] **Step 3: Implement `sites.detect_site()`**

Create `src/yt_dl/sites.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_sites.py -q`
Expected: PASS (all parametrized cases)

- [ ] **Step 5: Commit**

```bash
git add src/yt_dl/sites.py tests/test_sites.py
git commit -m "feat: add site detection for facebook/youtube/generic"
```

---

## Task 3: `sites.format_for()`

**Files:**
- Modify: `src/yt_dl/sites.py`
- Test: `tests/test_sites.py`

- [ ] **Step 1: Write the failing tests for `format_for`**

Append to `tests/test_sites.py`:

```python
from yt_dl.sites import format_for


def test_format_for_facebook():
    assert format_for("facebook", "video") == "bestvideo*+bestaudio/best"
    assert format_for("facebook", "mp3") == "bestaudio/best"


def test_format_for_youtube_unchanged():
    assert (
        format_for("youtube", "video")
        == "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    )
    assert format_for("youtube", "mp3") == "bestaudio/best"


def test_format_for_generic():
    assert format_for("generic", "video") == "bestvideo*+bestaudio/best"
    assert format_for("generic", "mp3") == "bestaudio/best"


def test_format_for_default_fmt():
    assert format_for("facebook") == "bestvideo*+bestaudio/best"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_sites.py::test_format_for_facebook -q`
Expected: FAIL with `ImportError: cannot import name 'format_for'`

- [ ] **Step 3: Implement `format_for()`**

Append to `src/yt_dl/sites.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_sites.py -q`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/yt_dl/sites.py tests/test_sites.py
git commit -m "feat: add per-site format selection"
```

---

## Task 4: `downloader.build_ydl_opts()` and `required_deps()`

**Files:**
- Modify: `src/yt_dl/downloader.py`
- Test: `tests/test_downloader.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_downloader.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_downloader.py -q`
Expected: FAIL with `ImportError: cannot import name 'build_ydl_opts'`

- [ ] **Step 3: Refactor `downloader.py` to add the helpers**

Replace the entire contents of `src/yt_dl/downloader.py` with:

```python
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
    return any(k in msg for k in ("login", "private", "sign in", "authorize", "403"))


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_downloader.py -q`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add src/yt_dl/downloader.py tests/test_downloader.py
git commit -m "feat: site-aware format/deps/cookies in downloader (+pure helpers)"
```

---

## Task 5: `_needs_cookies()` unit test

**Files:**
- Test: `tests/test_downloader.py`

(The helper already ships in Task 4; this task pins its behavior explicitly.)

- [ ] **Step 1: Write the tests**

Append to `tests/test_downloader.py`:

```python
from yt_dl.downloader import _needs_cookies


def test_needs_cookies_true_for_login_messages():
    assert _needs_cookies(Exception("Login required"))
    assert _needs_cookies(Exception("Video is private"))
    assert _needs_cookies(Exception("HTTP Error 403: Forbidden"))
    assert _needs_cookies(Exception("Please sign in to continue"))


def test_needs_cookies_false_for_other_errors():
    assert not _needs_cookies(Exception("Unable to extract video title"))
    assert not _needs_cookies(Exception("connection timed out"))
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_downloader.py -q`
Expected: PASS (already-implemented helper satisfies these)

- [ ] **Step 3: Commit**

```bash
git add tests/test_downloader.py
git commit -m "test: cover _needs_cookies login-error detection"
```

---

## Task 6: CLI flags + validation

**Files:**
- Modify: `src/yt_dl/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -q`
Expected: FAIL (`--cookies-from-browser` not recognized by argparse)

- [ ] **Step 3: Implement the new CLI**

Replace the entire contents of `src/yt_dl/cli.py` with:

```python
import argparse

from .batch import download_batch
from .downloader import download

_BROWSERS = ("chrome", "firefox", "safari", "edge", "brave")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="yt-dl",
        description=(
            "Download videos (YouTube, Facebook, and more) "
            "or extract audio as MP3."
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Video URL (YouTube, Facebook, or other yt-dlp-supported site)",
    )
    parser.add_argument(
        "--format",
        choices=["video", "mp3"],
        default="video",
        help="Output format (default: video)",
    )
    parser.add_argument(
        "--output",
        default="./downloads",
        help="Output directory (default: ./downloads)",
    )
    parser.add_argument(
        "--batch",
        help="Path to a text file with URLs (one per line)",
    )
    parser.add_argument(
        "--cookies",
        help="Path to a Netscape cookies.txt file (for HD/private videos)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        choices=_BROWSERS,
        dest="cookies_from_browser",
        help="Read cookies from a browser: chrome|firefox|safari|edge|brave",
    )

    args = parser.parse_args(argv)

    if not args.url and not args.batch:
        parser.error("Provide a URL or use --batch to specify a file of URLs.")

    if args.cookies and args.cookies_from_browser:
        parser.error("Use --cookies OR --cookies-from-browser, not both.")

    if args.batch:
        download_batch(
            args.batch,
            args.output,
            args.format,
            args.cookies,
            args.cookies_from_browser,
        )
    else:
        download(
            args.url,
            args.output,
            args.format,
            args.cookies,
            args.cookies_from_browser,
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/yt_dl/cli.py tests/test_cli.py
git commit -m "feat: add --cookies and --cookies-from-browser CLI flags"
```

---

## Task 7: Batch forwards cookies

**Files:**
- Modify: `src/yt_dl/batch.py`

- [ ] **Step 1: Implement the signature change**

Replace the entire contents of `src/yt_dl/batch.py` with:

```python
from pathlib import Path

from .downloader import download


def download_batch(
    file_path: str,
    output_dir: str,
    fmt: str = "video",
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
) -> None:
    urls = _read_urls(file_path)
    if not urls:
        print("No URLs found in batch file.")
        return

    total = len(urls)
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{total}] {url}")
        try:
            download(url, output_dir, fmt, cookies, cookies_from_browser)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nBatch complete: {total} URLs processed.")


def _read_urls(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Batch file not found: {file_path}")
        raise SystemExit(1)

    urls = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls
```

- [ ] **Step 2: Verify the full test suite still passes**

Run: `pytest -q`
Expected: PASS (all tests; batch change is a pass-through, covered by import + existing CLI tests)

- [ ] **Step 3: Commit**

```bash
git add src/yt_dl/batch.py
git commit -m "feat: forward cookies args through batch downloads"
```

---

## Task 8: README — Facebook section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the description and add Facebook docs**

Edit `README.md`:
- Change the tagline line `A simple CLI tool to download YouTube videos or extract audio as MP3.` to:
  `A simple CLI tool to download videos from YouTube, Facebook, and 1000+ other sites — or extract audio as MP3.`
- Add a `## Facebook` section after the `## Usage` section's YouTube examples and before `## Options`, and add the two new flags to the Options table.

Insert after the batch usage block (after the `# Batch download as MP3` example):

```markdown

## Facebook

Download Facebook videos at the best quality available. Public videos work
without login; HD / private / restricted videos need cookies.

```bash
# Public Facebook video (best available quality, no login)
yt-dl https://www.facebook.com/watch?v=VIDEO_ID

# fb.watch short links work too
yt-dl https://fb.watch/ABC123/

# HD or private video — read cookies from your browser
yt-dl https://www.facebook.com/watch?v=VIDEO_ID --cookies-from-browser chrome

# Or use a Netscape cookies.txt file
yt-dl https://www.facebook.com/watch?v=VIDEO_ID --cookies cookies.txt
```

> **Tip:** `--cookies-from-browser` supports `chrome`, `firefox`, `safari`,
> `edge`, and `brave`. Using cookies is the reliable way to get true HD quality.
```

Update the Options table by appending two rows:

```markdown
| `--cookies` | — | Path to a Netscape `cookies.txt` (HD/private videos) |
| `--cookies-from-browser` | — | `chrome\|firefox\|safari\|edge\|brave` |
```

Update the Prerequisites section: change the deno bullet so it reads as YouTube-only:

```markdown
- [deno](https://deno.com/) — required by yt-dlp **for YouTube extraction only** (not needed for Facebook or other sites)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add Facebook download section and cookies flags"
```

---

## Task 9: Final verification

- [ ] **Step 1: Run the full test suite**

Run: `pytest -q`
Expected: all tests PASS (sites, downloader, cli, smoke)

- [ ] **Step 2: Smoke-test the CLI help**

Run: `yt-dl --help`
Expected: usage lists `--cookies` and `--cookies-from-browser {chrome,firefox,safari,edge,brave}`, and the `url` help mentions Facebook.

- [ ] **Step 3: Smoke-test site detection + format selection without network**

Run:
```bash
python -c "from yt_dl.sites import detect_site, format_for; print(detect_site('https://fb.watch/abc/'), format_for('facebook','video'))"
```
Expected: `facebook bestvideo*+bestaudio/best`

- [ ] **Step 4: Confirm both-cookie rejection**

Run: `yt-dl https://fb.watch/abc/ --cookies c.txt --cookies-from-browser chrome`
Expected: exits non-zero with `Use --cookies OR --cookies-from-browser, not both.`

(No commit — verification only.)
