#!/data/data/com.termux/files/usr/bin/bash
echo "⚗️ MIYA 煉金術 — 開始組裝..."
python3 alchemy/scanner.py
python3 alchemy/mapper.py
python3 alchemy/assembler.py
python3 alchemy/renderer.py
echo "🎉 完成！統一UI：ui/index.html"
