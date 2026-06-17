# Adding credentials & files

Drop new files here or in `assets/certs/`, then add an entry to `content/credentials.json`.

## Example — PDF certificate

1. Save file as `assets/certs/my-cert.pdf`
2. Add to `content/credentials.json`:

```json
{
  "id": "my-cert",
  "title": "Course Name",
  "issuer": "Provider",
  "type": "pdf",
  "file": "assets/certs/my-cert.pdf"
}
```

## Example — badge image

1. Save image as `assets/certs/my-badge.png`
2. Add entry with `"type": "image"` and `"file": "assets/certs/my-badge.png"`

## Resume

Latest resume PDF: `assets/resume.pdf`  
Replace the file and re-run `./deploy.sh`.

## Uploads folder (optional)

You can also drop files in `portfolio-site/uploads/` and run:

```bash
python3 import_uploads.py
```
