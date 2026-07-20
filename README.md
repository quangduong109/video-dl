# yt-dl

A simple CLI tool to download videos from YouTube, Facebook, and 1000+ other sites — or extract audio as MP3.

Built with Python and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) — required for downloading and converting media
- [deno](https://deno.com/) — required by yt-dlp **for YouTube extraction only** (not needed for Facebook or other sites)

### Install prerequisites (macOS)

```bash
brew install ffmpeg
curl -fsSL https://deno.land/install.sh | sh
```

## Install

```bash
git clone https://github.com/<your-username>/youtube-download.git
cd youtube-download
pip install -e .
```

## Usage

```bash
# Download video (default) to ./downloads
yt-dl https://www.youtube.com/watch?v=VIDEO_ID

# Download as MP3
yt-dl https://www.youtube.com/watch?v=VIDEO_ID --format mp3

# Custom output directory
yt-dl https://www.youtube.com/watch?v=VIDEO_ID --output ~/videos

# Download a playlist
yt-dl https://www.youtube.com/playlist?list=PLAYLIST_ID

# Batch download from a text file (one URL per line)
yt-dl --batch urls.txt

# Batch download as MP3
yt-dl --batch urls.txt --format mp3
```

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

## Options

| Flag        | Default       | Description                              |
|-------------|---------------|------------------------------------------|
| `url`       | —             | Video URL (YouTube, Facebook, or other yt-dlp-supported site) |
| `--format`  | `video`       | Output format: `video` or `mp3`          |
| `--output`  | `./downloads` | Output directory                         |
| `--batch`   | —             | Path to a text file with URLs            |
| `--cookies` | —             | Path to a Netscape `cookies.txt` (HD/private videos) |
| `--cookies-from-browser` | — | `chrome\|firefox\|safari\|edge\|brave` |

## Batch File Format

One URL per line. Lines starting with `#` are ignored.

```
# My favorite videos
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=def456
```

## License

MIT
