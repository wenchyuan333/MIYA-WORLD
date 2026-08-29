MIYA Gateway - 全域性函式對接工具窗口 (prototype)

快速上手:
1. 在本機或 Termux 建立 Python env:
   python -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn typer notion-client PyGithub

2. 設定 secrets:
   export NOTION_TOKEN=...
   export GITHUB_TOKEN=...

3. 啟動 server:
   python tools/miya-gateway/server.py

4. 使用 CLI:
   python tools/miya-gateway/cli.py list
   python tools/miya-gateway/cli.py call notion.dump_page '{"page_id":"PAGE_ID"}'
   
設計說明:
- registry.py 提供註冊與列出函式
- adapters/ 包含 Notion 與 GitHub 的示範函式
- executor.py 管理調用並寫入 memory/OPERATION-LOG.md
- server.py 提供 HTTP API (/functions, /invoke)
- CLI 提供本機快速呼叫
安全:
- 請確保 token 不入 repo，使用環境變數或系統 secret
