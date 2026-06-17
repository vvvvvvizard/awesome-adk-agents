#!/usr/bin/env python3
"""Download resume from Google Docs and parse into structured JSON."""

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
RAW_PATH = CONTENT_DIR / "resume.txt"
JSON_PATH = CONTENT_DIR / "resume.json"

SECTION_HEADERS = {
    "summary": ("summary", "profile", "about", "professional summary", "objective"),
    "experience": ("experience", "work experience", "employment", "professional experience"),
    "education": ("education", "academic"),
    "skills": ("skills", "technical skills", "core competencies", "expertise"),
    "certifications": ("certifications", "certificates", "licenses"),
    "achievements": ("achievements", "awards", "honors"),
}


def load_sources():
    with SOURCES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def download_doc(doc_id: str, fmt: str = "txt") -> str:
    url = f"https://docs.google.com/document/d/{doc_id}/export?format={fmt}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, context=context, timeout=60) as response:
        if fmt == "txt":
            return response.read().decode("utf-8", errors="replace")
        return response.read()


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def detect_section(line: str) -> str | None:
    lowered = line.lower().strip(":- ")
    for section, aliases in SECTION_HEADERS.items():
        if lowered in aliases:
            return section
    return None


def looks_like_date(line: str) -> bool:
    return bool(
        re.search(
            r"(\b\d{4}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b)",
            line,
            re.I,
        )
        and re.search(r"[-–—]|to|present|current", line, re.I)
    )


def parse_resume(text: str) -> dict:
    lines = [normalize_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    data = {
        "name": "",
        "headline": "",
        "contact": {"email": "", "phone": "", "location": "", "linkedin": "", "github": ""},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "achievements": [],
        "raw_line_count": len(lines),
    }

    if not lines:
        return data

    data["name"] = lines[0]
    contact_line = lines[1] if len(lines) > 1 else ""
    if "@" in contact_line or "linkedin" in contact_line.lower() or re.search(r"\+\d", contact_line):
        data["headline"] = lines[2] if len(lines) > 2 and len(lines[2]) < 120 else ""
        for part in re.split(r"[|•·]", contact_line):
            part = part.strip()
            lower = part.lower()
            if "@" in part:
                data["contact"]["email"] = part
            elif "linkedin.com" in lower:
                data["contact"]["linkedin"] = part if part.startswith("http") else f"https://{part}"
            elif "github.com" in lower:
                data["contact"]["github"] = part if part.startswith("http") else f"https://{part}"
            elif re.search(r"\+\d", part):
                data["contact"]["phone"] = part
            elif part:
                data["contact"]["location"] = part
    elif len(lines) > 1 and len(lines[1]) < 120:
        data["headline"] = lines[1]

    current_section = None
    current_item = None
    summary_lines = []

    for line in lines[2:]:
        section = detect_section(line)
        if section:
            current_section = section
            current_item = None
            continue

        if current_section == "summary":
            summary_lines.append(line)
            continue

        if current_section == "skills":
            for skill in re.split(r"[,;•|]", line):
                skill = skill.strip(" -")
                if skill and skill not in data["skills"]:
                    data["skills"].append(skill)
            continue

        if current_section in {"certifications", "achievements", "education"}:
            bucket = data[current_section]
            if line.startswith(("-", "•", "·")):
                bucket.append(line.lstrip("-•· ").strip())
            else:
                bucket.append(line)
            continue

        if current_section == "experience":
            is_bullet = line.startswith(("-", "•", "·"))
            if is_bullet and current_item:
                current_item["bullets"].append(line.lstrip("-•· ").strip())
                continue

            if looks_like_date(line) and current_item and not current_item.get("dates"):
                current_item["dates"] = line
                continue

            if current_item and not current_item.get("title") and len(line) < 100:
                current_item["title"] = line
                continue

            current_item = {
                "organization": line,
                "title": "",
                "dates": "",
                "bullets": [],
            }
            data["experience"].append(current_item)
            continue

    data["summary"] = " ".join(summary_lines).strip()
    return data


def main() -> int:
    sources = load_sources()
    doc_id = sources["resume"]["id"]
    print(f"Downloading resume {doc_id} ...")

    try:
        text = download_doc(doc_id, "txt")
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"Failed to download resume: {error}", file=sys.stderr)
        print("Ensure the doc is shared as 'Anyone with the link can view'.", file=sys.stderr)
        return 1

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(text, encoding="utf-8")
    parsed = parse_resume(text)
    JSON_PATH.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

    print(f"Saved {RAW_PATH}")
    print(f"Saved {JSON_PATH}")
    print(f"Parsed {len(parsed['experience'])} experience entries, {len(parsed['skills'])} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
