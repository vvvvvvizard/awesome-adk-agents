#!/usr/bin/env python3
"""Copy files from portfolio-site/uploads/ into assets and update credentials.json."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"
CERTS = ROOT / "assets" / "certs"
CREDENTIALS_PATH = ROOT / "content" / "credentials.json"


def main() -> int:
    if not UPLOADS.exists():
        print("No uploads/ folder yet. Create it and drop PDFs or images there.")
        return 0

    CERTS.mkdir(parents=True, exist_ok=True)
    files = [path for path in UPLOADS.iterdir() if path.is_file() and not path.name.startswith(".")]

    if not files:
        print("uploads/ is empty.")
        return 0

    credentials = []
    if CREDENTIALS_PATH.exists():
        credentials = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))

    for path in files:
        lowered = path.name.lower()
        if "resume" in lowered:
            target = ROOT / "assets" / "resume.pdf"
            shutil.copy2(path, target)
            print(f"Updated resume → {target}")
            continue

        if "profile" in lowered and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            target = ROOT / "assets" / "profile.jpg"
            shutil.copy2(path, target)
            print(f"Updated profile photo → {target}")
            continue

        target = CERTS / path.name.replace(" ", "-").lower()
        shutil.copy2(path, target)
        print(f"Copied → {target}")

        entry_id = target.stem.replace("_", "-")
        if not any(item.get("id") == entry_id for item in credentials):
            file_type = "pdf" if target.suffix.lower() == ".pdf" else "image"
            credentials.append({
                "id": entry_id,
                "title": entry_id.replace("-", " ").title(),
                "issuer": "Add issuer in credentials.json",
                "type": file_type,
                "file": target.relative_to(ROOT).as_posix(),
            })

    CREDENTIALS_PATH.write_text(json.dumps(credentials, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {CREDENTIALS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
