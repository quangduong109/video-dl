import argparse

from .batch import download_batch
from .downloader import download


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="yt-dl",
        description="Download YouTube videos or extract audio as MP3.",
    )
    parser.add_argument("url", nargs="?", help="YouTube video or playlist URL")
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

    args = parser.parse_args()

    if not args.url and not args.batch:
        parser.error("Provide a URL or use --batch to specify a file of URLs.")

    if args.batch:
        download_batch(args.batch, args.output, args.format)
    else:
        download(args.url, args.output, args.format)


if __name__ == "__main__":
    main()
