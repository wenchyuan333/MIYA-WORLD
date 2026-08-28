#!/usr/bin/env python3
"""
🧩 語義映射器 — 分類、標籤、依賴解析
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORY_MAP = {
    "kernel": {"name": "🧠 核心中樞", "desc": "原點論、數學公理、系統核心"},
    "canon": {"name": "📜 正典規範", "desc": "洛書、黎曼、對稱、共時性"},
    "research": {"name": "🔬 研究文檔", "desc": "數理、哲學、交叉學科"},
    "memory": {"name": "💾 記憶連續性", "desc": "日誌、版本、狀態"},
    "protocol": {"name": "⚙️ 閘門協定", "desc": "邊界、權限、驗證"},
    "ai-skills": {"name": "🤖 AI技能庫", "desc": "提示詞、系統指令、模板"},
    "uiux": {"name": "🎨 介面展示", "desc": "UI、視覺、成品"},
    "tools": {"name": "🛠️ 工具腳本", "desc": "引擎、腳本、工具"},
    "other": {"name": "📁 其他", "desc": "未分類內容"},
}

def build_map():
    data = json.loads((ROOT / "alchemy" / "index.json").read_text(encoding="utf-8"))
    grouped = {}
    for item in data:
        grouped.setdefault(item["category"], []).append(item)
    result = {
        "categories": CATEGORY_MAP,
        "groups": grouped,
        "updated": __import__("datetime").datetime.now().isoformat(),
        "total": len(data)
    }
    (ROOT / "alchemy" / "map.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 映射完成：{len(grouped)} 分類，共 {len(data)} 個模組")

if __name__ == "__main__":
    build_map()
