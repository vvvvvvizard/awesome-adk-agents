#!/usr/bin/env python3
"""Download image and file assets from Google Drive."""

import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SOURCES_PATH = CONTENT_DIR / "sources.json"
IMAGES_DIR = ROOT / "images"

MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "application/pdf": ".pdf",
}


def load_sources() -> dict:
    with SOURCES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def drive_download_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def fetch_drive_file(file_id: str) -> tuple[bytes, str]:
    url = drive_download_url(file_id)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl.create_default_context()

    with urllib.request.urlopen(request, context=context, timeout=120) as response:
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
        data = response.read()

    if b"<!DOCTYPE html" in data[:200] or b"<html" in data[:200].lower():
        match = re.search(rb"confirm=([^&]+)&", data)
        if match:
            confirm = match.group(1).decode("utf-8", errors="replace")
            confirm_url = f"{url}&confirm={confirm}"
            request = urllib.request.Request(confirm_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, context=context, timeout=120) as response:
                content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
                data = response.read()

    return data, content_type


def extension_for(content_type: str, data: bytes) -> str:
    if content_type in MIME_EXTENSIONS:
        return MIME_EXTENSIONS[content_type]

    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG"):
        return ".png"
    if data.startswith(b"GIF8"):
        return ".gif"
    if data[:4] == b"%PDF":
        return ".pdf"
    return ".jpg"


def main() -> int:
    sources = load_sources()
    assets = sources.get("assets", {})
    if not assets:
        print("No assets configured.")
        return 0

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for key, asset in assets.items():
        file_id = asset["id"]
        output_base = ROOT / asset.get("output", f"images/{key}")
        output_base.parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {asset.get('label', key)} ({file_id}) ...")
        try:
            data, content_type = fetch_drive_file(file_id)
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"  Failed: {error}", file=sys.stderr)
            continue

        extension = extension_for(content_type, data)
        output_path = output_base.with_suffix(extension)

        for existing in output_base.parent.glob(output_base.name + ".*"):
            if existing != output_path:
                existing.unlink()

        output_path.write_bytes(data)
        relative_path = output_path.relative_to(ROOT).as_posix()
        manifest[key] = {
            "path": relative_path,
            "alt": asset.get("alt", asset.get("label", key)),
            "label": asset.get("label", key),
        }
        print(f"  Saved {output_path} ({len(data)} bytes)")

    manifest_path = CONTENT_DIR / "assets.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
