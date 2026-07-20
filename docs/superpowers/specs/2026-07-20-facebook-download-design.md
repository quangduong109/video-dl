# Facebook Video Download (Best Quality) - Design Spec

## Overview

Extend the existing `yt-dl` CLI so it downloads **Facebook** videos at the best
available quality (true HD where cookies allow), in addition to the existing
YouTube support. The tool becomes multi-site: it auto-detects the site from the
URL and applies the optimal quality settings per site. Built on `yt-dlp`, which
already supports Facebook natively.

## Goals

- Download Facebook videos at the **best quality** available.
- Support **HD / private / restricted** Facebook videos via cookies.
- Keep existing YouTube behavior **unchanged**.
- Keep the existing flags (`--format`, `--output`, `--batch`) working for all sites.
- Add unit tests for the pure, network-free logic (the project currently has none).

## Non-goals (out of scope)

- Quality / resolution selector (`--quality`). Always pick best.
- Per-site playlist handling beyond what yt-dlp already does.
- GUI, parallel batch downloads, resuming.

## Architecture

No new dependencies. The only runtime dependency remains `yt-dlp >= 2025.1`;
`ffmpeg` and (for YouTube only) `deno` remain external tools.

One new module is added; two existing modules are modified:

```
src/yt_dl/
├── __init__.py
├── cli.py          # modified: relaxed url help, +--cookies, +--cookies-from-browser
├── downloader.py   # modified: site-aware format + dependency checks + cookies opts
├── batch.py        # unchanged (each URL is auto-detected)
└── sites.py        # NEW: site detection + per-site format selection
tests/
├── test_sites.py        # detect_site() + format_for()
└── test_downloader.py   # cookies-opt + dependency-check wiring (no network)
```

## Components

### 1. `sites.py` (new) — pure, network-free, unit-tested

**`detect_site(url: str) -> str`** — returns one of `"facebook"`, `"youtube"`,
`"generic"` based on the URL host. Lowercases the URL before matching.

| Site | Hosts matched |
|------|---------------|
| `facebook` | `facebook.com`, `m.facebook.com`, `web.facebook.com`, `fb.com`, `fb.watch` |
| `youtube` | `youtube.com`, `m.youtube.com`, `youtu.be`, `music.youtube.com` |
| `generic` | anything else (yt-dlp supports 1000+ sites) |

**`format_for(site: str, fmt: str) -> str`** — returns the yt-dlp `format`
string.

| site \ fmt | `video` (default) | `mp3` |
|------------|-------------------|-------|
| `facebook` | `bestvideo*+bestaudio/best` | `bestaudio/best` |
| `youtube`  | `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best` (unchanged) | `bestaudio/best` |
| `generic`  | `bestvideo*+bestaudio/best` | `bestaudio/best` |

**Why Facebook uses `bestvideo*+bestaudio/best`:** this is yt-dlp's universal
"always best" selector. It first tries to **merge** the highest-resolution
separate video and audio streams (true max quality, e.g. 1080p), and falls back
to the best **progressive** (video+audio combined) stream via `/best` when no
separate streams exist. Facebook serves a mix of progressive and DASH sources
depending on the video, so this selector reliably yields the best quality in
both cases. The YouTube string is left untouched so existing behavior is
identical.

### 2. `downloader.py` (modified)

`download()` gains two optional parameters: `cookies: str | None` and
`cookies_from_browser: str | None`.

Changes inside `download()`:

1. **Site detection:** `site = detect_site(url)`.
2. **Format selection:** `ydl_opts["format"] = format_for(site, fmt)`.
3. **Dependency checks made site-aware:**
   - `ffmpeg` — always checked (needed for mp3 + muxing).
   - `deno` — checked **only when `site == "youtube"`** (yt-dlp uses deno for
     the YouTube player JS; Facebook and generic sites do not need it).
4. **Cookies wiring** — when provided, set exactly one of:
   - `ydl_opts["cookiesfile"] = cookies` for a `cookies.txt` path, or
   - `ydl_opts["cookiesfrombrowser"] = (browser,)` for a browser name.
   - Both provided is a caller error (validated in `cli.py`).

### 3. `cli.py` (modified)

- `url` positional help → `"Video URL (YouTube, Facebook, or other yt-dlp-supported site)"`.
- New `--cookies <path>` — path to a Netscape `cookies.txt`.
- New `--cookies-from-browser <browser>` — `chrome|firefox|safari|edge|brave`
  (validated choices; yt-dlp accepts these names).
- Validation: if both `--cookies` and `--cookies-from-browser` are given,
  `parser.error(...)` with a clear message.
- Pass both through to `download()` / `download_batch()`.

`--format`, `--output`, `--batch` are unchanged. Batch mode auto-detects each
URL's site independently (no per-line config needed).

## Behavior

### Best quality on Facebook

- Public video, no cookies: downloads the best public quality yt-dlp can reach.
- With cookies (`--cookies-from-browser chrome` or `--cookies <file>`): yt-dlp
  authenticates, unlocking HD/1080p and access to private/group/watch-party
  videos.

### Dependency checks

- YouTube: requires `ffmpeg` **and** `deno` (as today).
- Facebook / generic: requires `ffmpeg` only.

## Error handling

- **FB download fails with a login/authorization error and no cookies supplied:**
  catch and print a friendly hint:
  `HD/private video needs cookies — try --cookies-from-browser chrome`.
  (Detected via yt-dlp's exception message; re-raise other errors normally.)
- **Missing cookies file:** clear "file not found" error before invoking yt-dlp.
- **Unknown browser name:** rejected by argparse `choices`.
- **Both cookie flags given:** `parser.error("Use --cookies OR --cookies-from-browser, not both.")`.
- Existing error handling (missing ffmpeg/deno, invalid URL, batch continue-on-error) preserved.

## Testing

New `tests/` directory. Pure unit tests, no network:

- `test_sites.py`
  - `detect_site()` for: FB canonical, `fb.watch`, `m.facebook.com`, `web.facebook.com`,
    YouTube canonical, `youtu.be`, `music.youtube.com`, an unrelated site → `generic`,
    and case-insensitivity (`HTTPS://WWW.FACEBOOK.COM/...`).
  - `format_for()` returns the exact expected string for each (site × fmt) cell
    in the table above.
- `test_downloader.py`
  - Building `ydl_opts` sets `format` from `format_for(detect_site(url), fmt)`.
  - Cookies: `cookiesfile` set when `cookies` given; `cookiesfrombrowser` tuple
    set when `cookies_from_browser` given; neither set when both `None`.
  - Dependency checks: `deno` checked for youtube, skipped for facebook/generic.

These are tested by refactoring the option-building into a small pure helper
(e.g. `build_ydl_opts(...)`) so it can be asserted without invoking yt-dlp. The
actual `download()` wrapper stays a thin caller over that helper.

No network/download tests (flaky and slow).

## Documentation

- `README.md`: add a **Facebook** section with install note (cookies), examples
  for public and HD/private downloads, and note `deno` is YouTube-only.
- Keep the `yt-dl` command name (now multi-site; renaming is an out-of-scope
  breaking change).

## CLI interface (updated)

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `url` | Yes (unless `--batch`) | — | Video URL (YouTube, Facebook, or other yt-dlp-supported site) |
| `--format` | No | `video` | `video` or `mp3` |
| `--output` | No | `./downloads` | Output directory |
| `--batch` | No | — | Path to text file with URLs (one per line) |
| `--cookies` | No | — | Path to a Netscape `cookies.txt` |
| `--cookies-from-browser` | No | — | `chrome\|firefox\|safari\|edge\|brave` |
