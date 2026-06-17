#!/usr/bin/env bash
# Deploy portfolio-site/ to https://vvvvvvizard.github.io/
set -euo pipefail

REPO="vvvvvvizard/vvvvvvizard.github.io"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKDIR="${TMPDIR:-/tmp}/vvvvvvizard.github.io-deploy"

echo "→ Syncing assets from Google Drive (if available) ..."
if python3 "$DEPLOY_DIR/sync_assets.py"; then
  python3 "$DEPLOY_DIR/update_portfolio.py" || true
else
  echo "  Asset sync skipped — using existing assets."
fi

echo "→ Syncing resume from Google Docs (if available) ..."
if python3 "$DEPLOY_DIR/sync_resume.py"; then
  python3 "$DEPLOY_DIR/update_portfolio.py"
else
  echo "  Resume sync skipped — using existing portfolio content."
fi

echo "→ Cloning $REPO ..."
rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR"
cd "$WORKDIR"

echo "→ Replacing site files ..."
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
cp -r "$DEPLOY_DIR/index.html" "$DEPLOY_DIR/css" "$DEPLOY_DIR/js" .
if [ -f "$DEPLOY_DIR/CNAME" ]; then
  cp "$DEPLOY_DIR/CNAME" .
fi
if [ -d "$DEPLOY_DIR/assets" ] && [ "$(ls -A "$DEPLOY_DIR/assets" 2>/dev/null)" ]; then
  cp -r "$DEPLOY_DIR/assets" .
fi
if [ -d "$DEPLOY_DIR/images" ] && [ "$(ls -A "$DEPLOY_DIR/images" 2>/dev/null)" ]; then
  cp -r "$DEPLOY_DIR/images" .
fi

git add -A
if git diff --cached --quiet; then
  echo "Nothing to deploy."
  exit 0
fi

git commit -m "Deploy portfolio site"
git push origin main

echo ""
echo "Live at: https://vvvvvvizard.github.io/"
echo "(GitHub Pages may take 1–2 minutes to update)"
