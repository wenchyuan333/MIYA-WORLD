#!/usr/bin/env python3
"""
⚙️ 自動組裝器 — 生成導航、路由、索引
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

def assemble():
    data = json.loads((ROOT / "alchemy" / "map.json").read_text(encoding="utf-8"))
    nav = []
    for cat_key, cat_info in data["categories"].items():
        items = data["groups"].get(cat_key, [])
        nav.append({
            "key": cat_key,
            "name": cat_info["name"],
            "desc": cat_info["desc"],
            "items": items
        })
    (ROOT / "alchemy" / "nav.json").write_text(json.dumps(nav, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 組裝完成：{len(nav)} 大模組")

if __name__ == "__main__":
    assemble()
