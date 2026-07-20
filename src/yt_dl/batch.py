from pathlib import Path

from .downloader import download


def download_batch(file_path: str, output_dir: str, fmt: str = "video") -> None:
    urls = _read_urls(file_path)
    if not urls:
        print("No URLs found in batch file.")
        return

    total = len(urls)
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{total}] {url}")
        try:
            download(url, output_dir, fmt)
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
