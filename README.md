# yt-dl

A simple CLI tool to download YouTube videos or extract audio as MP3.

Built with Python and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) — required for downloading and converting media
- [deno](https://deno.com/) — required by yt-dlp for YouTube extraction

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

## Options

| Flag        | Default       | Description                              |
|-------------|---------------|------------------------------------------|
| `url`       | —             | YouTube video or playlist URL            |
| `--format`  | `video`       | Output format: `video` or `mp3`          |
| `--output`  | `./downloads` | Output directory                         |
| `--batch`   | —             | Path to a text file with URLs            |

## Batch File Format

One URL per line. Lines starting with `#` are ignored.

```
# My favorite videos
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=def456
```

## License

MIT
