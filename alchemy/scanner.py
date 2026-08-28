#!/usr/bin/env python3
"""
⚗️ MIYA 煉金術 — 全域掃描器
自動發現所有模組、語義分類、建立索引
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
PATTERNS = {
    "kernel": [r"原點", r"核心", r"ORIGIN", r"不動點", r"C₀·O₁", r"MATH"],
    "canon": [r"正典", r"CANON", r"洛書", r"黎曼", r"對稱", r"規範"],
    "research": [r"研究", r"RESEARCH", r"交叉", r"數學", r"物理", r"哲學"],
    "memory": [r"記憶", r"MEMORY", r"日誌", r"連續性"],
    "protocol": [r"閘門", r"協定", r"GATE", r"邊界", r"安全", r"驗證"],
    "ai-skills": [r"提示詞", r"PROMPT", r"AI技能", r"系統指令"],
    "uiux": [r"介面", r"UI", r"展示", r"視覺"],
    "tools": [r"工具", r"腳本", r"TOOL", r"引擎"],
}

def scan():
    items = []
    for path in ROOT.rglob("*.md"):
        if any(p in str(path) for p in [".github", "ui/", "alchemy/", "node_modules"]):
            continue
        text = path.read_text(encoding="utf-8")
        cat = "other"
        for c, pats in PATTERNS.items():
            if any(re.search(p, text, re.I) for p in pats):
                cat = c
                break
        items.append({
            "path": str(path.relative_to(ROOT)),
            "name": path.stem,
            "category": cat,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        })
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items

if __name__ == "__main__":
    data = scan()
    (ROOT / "alchemy" / "index.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 掃描完成：發現 {len(data)} 個模組")
