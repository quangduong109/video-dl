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
