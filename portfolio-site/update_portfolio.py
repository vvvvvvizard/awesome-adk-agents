#!/usr/bin/env python3
"""Apply parsed resume JSON to portfolio index.html."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "content" / "resume.json"
INDEX_PATH = ROOT / "index.html"
SOURCES_PATH = ROOT / "content" / "sources.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def render_degree_credential(degree_asset: dict, drive_id: str) -> str:
    path = degree_asset["path"]
    alt = esc(degree_asset.get("alt", "Degree certificate"))

    if path.lower().endswith(".pdf"):
        return f"""          <object
            data="{esc(path)}"
            type="application/pdf"
            class="credential-pdf"
            aria-label="{alt}"
          >
            <a class="btn btn-primary" href="{esc(path)}" target="_blank" rel="noopener noreferrer">Open degree certificate (PDF)</a>
          </object>"""

    return f"""          <a href="{esc(path)}" target="_blank" rel="noopener noreferrer">
            <img src="{esc(path)}" alt="{alt}" class="credential-image" loading="lazy" width="800" height="600">
          </a>"""


def update_degree_section(index: str, sources: dict) -> str:
    assets = load_json(ROOT / "content" / "assets.json")
    degree = assets.get("degree_image") or assets.get("degree")
    if not degree:
        return index

    drive_id = sources.get("assets", {}).get("degree", {}).get("id", "")
    viewer_html = render_degree_credential(degree, drive_id)
    drive_link = (
        f'<a href="{esc(f"https://drive.google.com/file/d/{drive_id}/view")}" '
        'target="_blank" rel="noopener noreferrer">View on Google Drive</a>'
        if drive_id else ""
    )

    block = f"""        <div class="credential-viewer" id="degree-credential">
{viewer_html}
        </div>
        <p class="credential-caption">
          BSc Honours Data Science · {drive_link}
        </p>"""

    return replace_block(index, "<!-- DEGREE_CREDENTIAL_START -->", "<!-- DEGREE_CREDENTIAL_END -->", block)


def badge_for_org(org: str) -> str:
    org_lower = org.lower()
    if any(word in org_lower for word in ("bank", "fnb", "absa")):
        return "Banking"
    if any(word in org_lower for word in ("sanlam", "insurance")):
        return "Insurance"
    if any(word in org_lower for word in ("eqplus", "consult")):
        return "Consulting"
    return "Experience"


def render_experience(items: list) -> str:
    if not items:
        return ""
    chunks = []
    for item in items[:8]:
        org = item.get("organization", "")
        title = item.get("title", "")
        dates = item.get("dates", "")
        bullets = item.get("bullets", [])
        summary = bullets[0] if bullets else ""
        if len(bullets) > 1:
            summary = "; ".join(bullets[:3])
        chunks.append(
            f"""        <article class="timeline-item">
          <div class="timeline-meta">
            <span class="timeline-date">{esc(dates)}</span>
            <span class="badge">{esc(badge_for_org(org))}</span>
          </div>
          <h3>{esc(title or org)}</h3>
          <p class="timeline-org">{esc(org if title else "")}</p>
          <p>{esc(summary)}</p>
        </article>"""
        )
    return "\n".join(chunks)


def render_skills(skills: list) -> str:
    if not skills:
        return ""
    return "\n".join(f"          <li>{esc(skill)}</li>" for skill in skills[:8])


def render_certifications(certs: list) -> str:
    if not certs:
        return ""
    return "\n".join(f"          <li>{esc(cert)}</li>" for cert in certs[:6])


def replace_block(content: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{new_block}\n      {end_marker}"
    if not pattern.search(content):
        raise ValueError(f"Markers not found: {start_marker}")
    return pattern.sub(replacement, content, count=1)


def main() -> int:
    resume = load_json(JSON_PATH)
    if not resume:
        print("No resume.json found. Run sync_resume.py first.", file=sys.stderr)
        return 1

    sources = load_json(SOURCES_PATH)
    doc_id = sources.get("resume", {}).get("id", "")
    resume_pdf = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

    name = resume.get("name") or "Yusuf Rawat"
    headline = resume.get("headline") or "AWS · Business Intelligence · Google ADK"
    summary = resume.get("summary") or (
        "Solution architect with experience across cloud, business intelligence, "
        "and production multi-agent AI systems."
    )
    hero_lead = summary[:320] + ("…" if len(summary) > 320 else "")

    contact = resume.get("contact", {})
    location = contact.get("location") or "Fourways, Johannesburg"
    linkedin = contact.get("linkedin") or "https://www.linkedin.com/in/yusuf-rawat-123/"
    github = contact.get("github") or "https://github.com/vvvvvvizard"

    index = INDEX_PATH.read_text(encoding="utf-8")

    index = index.replace("<title>Yusuf Rawat · AWS &amp; AI Agent Developer</title>",
                          f"<title>{esc(name)} · AWS &amp; AI Agent Developer</title>")
    index = re.sub(r'(<a class="logo" href="#">)(.*?)(</a>)',
                   rf"\1{esc(name)}\3", index, count=1)
    index = re.sub(r'(<p class="eyebrow">)(.*?)(</p>)',
                   rf"\1{esc(headline)}\3", index, count=1)
    index = re.sub(
        r'(<p class="hero-lead">\s*)(.*?)(\s*</p>)',
        rf"\1{esc(hero_lead)}\3",
        index,
        count=1,
        flags=re.DOTALL,
    )

    about_text = summary
    index = re.sub(
        r'(<p class="about-text">\s*)(.*?)(\s*</p>)',
        rf"\1{esc(about_text)}\3",
        index,
        count=1,
        flags=re.DOTALL,
    )

    skills_html = render_skills(resume.get("skills", []))
    if skills_html:
        index = replace_block(index, "<ul class=\"highlight-list\">", "</ul>", skills_html)

    experience_html = render_experience(resume.get("experience", []))
    if experience_html:
        index = replace_block(index, "<div class=\"timeline\">", "</div>", experience_html)

    certs = resume.get("certifications", []) + resume.get("achievements", [])
    if certs and "<section id=\"credentials\"" not in index:
        credentials_section = f"""
    <section id="credentials" class="section">
      <div class="section-header">
        <h2>Credentials</h2>
        <p>Certifications and highlights from my resume.</p>
      </div>
      <ul class="highlight-list credentials-list">
{render_certifications(certs)}
      </ul>
    </section>
"""
        index = index.replace('    <section id="projects" class="section">', credentials_section + '\n    <section id="projects" class="section">', 1)

    contact_blurb = f"{location} · Open to consulting, collaborations, and ADK contributions."
    index = re.sub(
        r'(<div class="contact-card">\s*<h2>Get in touch</h2>\s*<p>)(.*?)(</p>)',
        rf"\1{esc(contact_blurb)}\3",
        index,
        count=1,
        flags=re.DOTALL,
    )

    if 'href="#resume"' not in index:
        index = index.replace(
            '<a class="btn btn-primary" href="#projects">View agent projects</a>',
            '<a class="btn btn-primary" href="#projects">View agent projects</a>\n'
            f'        <a class="btn btn-ghost" href="{resume_pdf}" target="_blank" rel="noopener noreferrer">Download resume</a>',
            1,
        )

    index = re.sub(
        r'(<a class="btn btn-primary" href=")([^"]*)(" target="_blank" rel="noopener noreferrer">LinkedIn</a>)',
        rf"\1{esc(linkedin)}\3",
        index,
        count=1,
    )
    index = re.sub(
        r'(<a class="btn btn-ghost" href=")(https://github.com/vvvvvvizard)(" target="_blank" rel="noopener noreferrer">GitHub</a>)',
        rf"\1{esc(github)}\3",
        index,
        count=1,
    )

    sources = load_json(SOURCES_PATH)
    index = update_degree_section(index, sources)

    INDEX_PATH.write_text(index, encoding="utf-8")
    print(f"Updated {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
