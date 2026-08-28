#!/data/data/com.termux/files/usr/bin/bash
# MIYA 自動驗證腳本
echo "🧠 執行 MIYA 結構驗證..."
[ -f "kernel/ORIGIN.md" ] && echo "✅ 原點存在" || echo "❌ 原點缺失"
[ -f "README.md" ] && echo "✅ 導航存在" || echo "❌ 導航缺失"
echo "驗證完成 ✨"
