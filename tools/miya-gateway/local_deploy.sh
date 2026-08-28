#!/usr/bin/env bash
# local_deploy.sh
# Run this on your Termux / VPS to deploy miya-gateway locally
set -e
REPO_DIR="$1"
if [ -z "$REPO_DIR" ]; then
  echo "Usage: ./local_deploy.sh /path/to/MIYA-WORLD"
  exit 1
fi
cd "$REPO_DIR"
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn typer notion-client PyGithub
# create .env sample
cat > .env.sample <<'EOF'
NOTION_TOKEN=your_notion_token_here
GITHUB_TOKEN=your_github_token_here
EOF
echo "Deploy scaffold ready. Set env vars and run: python tools/miya-gateway/server.py"
