#!/usr/bin/env python3
"""
🎨 統一UI渲染器 — 自動生成完整網頁介面
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
UI = ROOT / "ui"
UI.mkdir(exist_ok=True)

def render():
    nav = json.loads((ROOT / "alchemy" / "nav.json").read_text(encoding="utf-8"))
    updated = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌌 MIYA-WORLD | 煉金術 · 統一入口</title>
    <style>
        *{{box-sizing:border-box;margin:0;padding:0}}
        body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0a0a0f;color:#e6e6fa;line-height:1.6}}
        header{{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:2rem;text-align:center;border-bottom:1px solid #333}}
        h1{{font-size:2rem;margin-bottom:.5rem}}
        .subtitle{{color:#a0a0c0;opacity:.8}}
        .container{{max-width:1200px;margin:0 auto;padding:2rem}}
        .search{{width:100%;padding:.8rem;border-radius:8px;border:1px solid #333;background:#12121a;color:#fff;font-size:1rem;margin-bottom:2rem}}
        .category{{margin-bottom:2.5rem;border:1px solid #2a2a3a;border-radius:12px;padding:1.5rem;background:#0f0f17}}
        .cat-title{{font-size:1.4rem;margin-bottom:1rem;color:#d8b4fe;border-bottom:1px solid #2a2a3a;padding-bottom:.5rem}}
        .item{{display:block;color:#a0d2ff;text-decoration:none;padding:.5rem .8rem;border-radius:6px;margin:.3rem 0;transition:all .2s}}
        .item:hover{{background:#1e1e2f;color:#fff}}
        .footer{{text-align:center;padding:2rem;color:#666;font-size:.9rem;border-top:1px solid #2a2a3a;margin-top:3rem}}
        .updated{{text-align:right;color:#666;font-size:.85rem;margin-top:1rem}}
    </style>
</head>
<body>
    <header>
        <h1>🌌 MIYA-WORLD</h1>
        <p class="subtitle">C₀·O₁·V₁₃ :: PUB :: B↔ — 自動組裝 · 跨倉庫統一入口</p>
    </header>
    <div class="container">
        <input type="search" class="search" id="q" placeholder="🔍 全域搜尋所有模組..." oninput="filter(this.value)">
"""
    for cat in nav:
        html += f'        <div class="category"><h2 class="cat-title">{cat["name"]}</h2>\n'
        if not cat["items"]:
            html += '            <p style="color:#555">尚無內容</p>\n'
        else:
            for item in cat["items"]:
                html += f'            <a href="../{item["path"]}" class="item">{item["name"]}</a>\n'
        html += '        </div>\n'

    html += f"""
        <p class="updated">🔄 自動更新：{updated}</p>
    </div>
    <div class="footer">
        <p>⚗️ MIYA 煉金術引擎 — 碎片進來，完整的世界出來 ✨</p>
        <p>v0.7.0 | 中樞不動 · 外環無限 · 邏輯連續 · 無損升級</p>
    </div>
    <script>
        function filter(q){{
            q = q.toLowerCase();
            document.querySelectorAll('.item').forEach(el=>
                el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none'
            )
        }}
    </script>
</body>
</html>
"""
    (UI / "index.html").write_text(html, encoding="utf-8")
    print(f"✅ UI渲染完成：ui/index.html")

if __name__ == "__main__":
    render()
