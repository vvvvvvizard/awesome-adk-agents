# Assets

Degree certificate and other files from Google Drive land here after sync.

```bash
python3 sync_assets.py   # downloads degree PDF → assets/degree.pdf
./deploy.sh              # sync + deploy
```

## PDF vs image

- Current degree file is a **PDF** (`assets/degree.pdf`) — shown in an embedded viewer.
- When you have an **image**, add its Drive file ID to `content/sources.json` under `degree_image.id`, then re-run sync. The site will prefer the image over the PDF.
