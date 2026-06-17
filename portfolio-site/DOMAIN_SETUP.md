# Custom domain: agenticai54.co.za

The site deploys to `vvvvvvizard.github.io` with a `CNAME` file pointing at your domain.

## 1. Deploy the site

```bash
cd portfolio-site && ./deploy.sh
```

## 2. GitHub Pages settings

In **vvvvvvvizard/vvvvvvizard.github.io** → **Settings → Pages**:

- Custom domain: `agenticai54.co.za`
- Enable **Enforce HTTPS** (after DNS propagates)

## 3. DNS at your registrar (.co.za)

For the **apex** domain `agenticai54.co.za`, add **A records**:

| Type | Host | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

Optional **www** subdomain:

| Type | Host | Value |
|------|------|-------|
| CNAME | www | vvvvvvizard.github.io |

DNS can take up to 24–48 hours (often much faster).

## 4. Profile photo

Save your headshot as:

```
portfolio-site/assets/profile.jpg
```

Or drop it in `portfolio-site/uploads/` as `profile.jpg` and run:

```bash
python3 import_uploads.py
```

Then redeploy with `./deploy.sh`.
