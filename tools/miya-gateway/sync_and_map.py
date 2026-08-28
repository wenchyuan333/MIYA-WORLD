#!/usr/bin/env python3
"""
sync_and_map.py
Standalone Notion -> Markdown sync + simple loshu mapping script.
Run this on your local machine or Termux after setting NOTION_TOKEN.

Writes Markdown files into module directories (kernel/, ai-skills/, etc.) and
updates alchemy/index.json and alchemy/map.json minimally.

Note: This is a pragmatic prototype; review outputs before pushing to main.
"""
import os
import re
import json
from notion_client import Client
from pathlib import Path
from datetime import datetime

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise SystemExit('NOTION_TOKEN not set in environment')

client = Client(auth=NOTION_TOKEN)

# Loshu mapping heuristics (keywords -> module)
LOS_MAPPINGS = [
    (['core','kernel','math','axiom','原點','中樞','kernel'], 'kernel'),
    (['ui','interface','homepage','home','display','顯示','視覺'], 'ui'),
    (['canon','洛書','黎曼','正典','canon'], 'canon'),
    (['protocol','gate','閘門','protocol','權限','auth'], 'protocol'),
    (['ai','prompt','提示詞','人格','persona'], 'ai-skills'),
    (['research','研究','paper','論文'], 'research'),
    (['memory','log','日誌','版本','history'], 'memory'),
    (['tool','script','alchemy','工具','automation'], 'tools'),
]

MODULES = set([m for _, m in LOS_MAPPINGS])
MODULES.add('BOOT')

OUTPUT_ROOT = Path('.')
ALCHEMY_INDEX = OUTPUT_ROOT / 'alchemy' / 'index.json'
ALCHEMY_MAP = OUTPUT_ROOT / 'alchemy' / 'map.json'

def slugify(s: str):
    s = s.strip().lower()
    s = re.sub(r"[\s\/]+", '-', s)
    s = re.sub(r"[^a-z0-9\-\_\.]+", '', s)
    s = re.sub(r"\-+", '-', s)
    return s.strip('-')[:120]

def detect_module(title: str, props: dict):
    text = title + ' ' + ' '.join([str(v) for v in (props or {}).values()])
    text = text.lower()
    for keys, mod in LOS_MAPPINGS:
        for k in keys:
            if k in text:
                return mod
    return 'research'  # fallback

# Basic block -> markdown converter
def blocks_to_markdown(blocks):
    lines = []
    for b in blocks:
        t = b.get('type')
        data = b.get(t, {})
        if t == 'paragraph':
            plain = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            lines.append(plain + '\n')
        elif t in ('heading_1','heading_2','heading_3'):
            level = {'heading_1':'#','heading_2':'##','heading_3':'###'}[t]
            plain = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            lines.append(f"{level} {plain}\n")
        elif t in ('bulleted_list_item','numbered_list_item'):
            plain = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            prefix = '-' if t=='bulleted_list_item' else '1.'
            lines.append(f"{prefix} {plain}\n")
        elif t == 'code':
            lang = data.get('language') or ''
            text = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            lines.append(f"```{lang}\n{text}\n```\n")
        elif t == 'quote':
            text = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            lines.append(f"> {text}\n")
        elif t == 'to_do':
            checked = data.get('checked')
            text = ''.join([r.get('plain_text','') for r in data.get('text', [])])
            mark = 'x' if checked else ' '
            lines.append(f"- [{mark}] {text}\n")
        elif t == 'image':
            url = data.get('file',{}).get('url') or data.get('external',{}).get('url')
            caption = ''.join([r.get('plain_text','') for r in data.get('caption', [])])
            lines.append(f"![{caption}]({url})\n")
        else:
            # generic fallback
            plain = ''.join([r.get('plain_text','') for r in data.get('text', [])]) if isinstance(data, dict) else str(data)
            if plain:
                lines.append(plain + '\n')
    return '\n'.join(lines)

def fetch_page_blocks(page_id):
    all_blocks = []
    cursor = None
    while True:
        res = client.blocks.children.list(block_id=page_id, start_cursor=cursor)
        results = res.get('results', [])
        all_blocks.extend(results)
        if not res.get('has_more'):
            break
        cursor = res.get('next_cursor')
    return all_blocks


def write_markdown(module, title, md, origin_url):
    mod_dir = OUTPUT_ROOT / module
    mod_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    filename = f"{slug}.md" if slug else f"page-{datetime.utcnow().timestamp()}.md"
    path = mod_dir / filename
    front = {
        'title': title,
        'module': module,
        'loshu': 5 if module=='BOOT' else None,
        'origin': origin_url,
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d'),
        'status': 'mapped'
    }
    fm = '---\n'
    for k,v in front.items():
        if v is not None:
            fm += f"{k}: \"{v}\"\n"
    fm += '---\n\n'
    content = fm + md
    path.write_text(content, encoding='utf-8')
    return str(path)


def update_alchemy_index(entry):
    ALCHEMY_INDEX.parent.mkdir(parents=True, exist_ok=True)
    idx = {}
    if ALCHEMY_INDEX.exists():
        try:
            idx = json.loads(ALCHEMY_INDEX.read_text(encoding='utf-8') or '{}')
        except Exception:
            idx = {}
    idx_key = entry.get('path')
    idx[idx_key] = entry
    ALCHEMY_INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding='utf-8')


def update_alchemy_map(mapping):
    ALCHEMY_MAP.parent.mkdir(parents=True, exist_ok=True)
    current = []
    if ALCHEMY_MAP.exists():
        try:
            current = json.loads(ALCHEMY_MAP.read_text(encoding='utf-8') or '[]')
        except Exception:
            current = []
    current.append(mapping)
    # deduplicate by path
    dedup = {m['path']: m for m in current}
    ALCHEMY_MAP.write_text(json.dumps(list(dedup.values()), ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    print('Searching Notion for pages accessible to integration...')
    res = client.search()
    results = res.get('results', [])
    print(f'Found {len(results)} pages / dbs')

    for page in results:
        if page.get('object') != 'page':
            continue
        page_id = page.get('id')
        title = 'Untitled'
        props = page.get('properties', {})
        # try to extract title
        for k,v in props.items():
            if isinstance(v, dict) and v.get('type') == 'title':
                title_parts = v.get('title', [])
                title = ''.join([t.get('plain_text','') for t in title_parts]) or title
                break
        module = detect_module(title, props)
        print(f'Page: {title} -> module {module}')
        # fetch blocks
        blocks = fetch_page_blocks(page_id)
        md = blocks_to_markdown(blocks)
        origin_url = f'https://www.notion.so/{page_id.replace("-","")}'
        path = write_markdown(module, title, md, origin_url)
        entry = {'title': title, 'module': module, 'path': path, 'synced_at': datetime.utcnow().isoformat()}
        update_alchemy_index(entry)
        update_alchemy_map({'title': title, 'module': module, 'path': path})
        print(f'Wrote: {path}')

if __name__ == '__main__':
    main()
