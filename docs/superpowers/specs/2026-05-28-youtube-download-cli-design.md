# YouTube Download CLI - Design Spec

## Overview
A Python CLI tool that downloads YouTube videos or extracts audio as MP3. Wraps `yt-dlp` for reliable downloading.

## Architecture
- **Language**: Python 3.10+
- **Core dependency**: `yt-dlp` (Python API)
- **Optional dependency**: `ffmpeg` (required for MP3 conversion)
- **Package manager**: `uv` with `pyproject.toml`

## Project Structure
```
youtube-download/
├── pyproject.toml
├── src/
│   └── yt_dl/
│       ├── __init__.py
│       ├── cli.py          # argparse CLI entry point
│       ├── downloader.py   # yt-dlp wrapper logic
│       └── batch.py        # Batch file parsing
```

## CLI Interface

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `url` | Yes (unless `--batch`) | — | YouTube URL |
| `--format` | No | `video` | `video` or `mp3` |
| `--output` | No | `./downloads` | Output directory |
| `--batch` | No | — | Path to text file with URLs (one per line) |

### Usage
```bash
# Download video (default)
yt-dl https://youtube.com/watch?v=xxx

# Download as MP3
yt-dl https://youtube.com/watch?v=xxx --format mp3

# Custom output directory
yt-dl https://youtube.com/watch?v=xxx --output ~/videos

# Playlist
yt-dl https://youtube.com/playlist?list=xxx

# Batch from file
yt-dl --batch urls.txt
```

## Behavior

### Video mode (`--format video`, default)
- Downloads best quality video+audio as mp4
- Uses `yt-dlp` format: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best`
- Output: `{title}.mp4`

### MP3 mode (`--format mp3`)
- Extracts audio, converts to mp3 at best quality
- Uses `yt-dlp` post-processor: `FFmpegExtractAudioPP` with `preferredcodec: mp3`
- Output: `{title}.mp3`
- Requires `ffmpeg` installed on system

### Batch mode (`--batch urls.txt`)
- Reads URLs from a text file (one URL per line)
- Skips empty lines and lines starting with `#`
- Downloads each URL sequentially with the same format/output settings

### Playlist support
- Handled natively by `yt-dlp` — playlist URLs are detected automatically
- All videos in playlist downloaded with same format settings

### Progress bar
- Uses `yt-dlp` built-in progress hooks
- Shows download speed, ETA, percentage

## Error handling
- Missing `yt-dlp`: print install instructions
- Missing `ffmpeg` (for MP3): print install instructions
- Invalid URL: clear error message
- Download failure: print error, continue to next (in batch mode)
- Output directory: create if it doesn't exist
