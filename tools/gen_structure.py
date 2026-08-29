#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/gen_structure.py

產生 docs/STRUCTURE.md 與 docs/STRUCTURE.json。

=====================================================================
為何存在
=====================================================================
手寫的結构清單一定會過時。
2026-08-29 一天之内就有三次證據：

  1. 宣稱 main 的 alchemy/ ui/ memory/ ai-skills/ 是空的
     -> e5f99cb 裡實際有 17 個檔案，含完整的煉金術流水線
  2. 宣稱有 6 支 fixture
     -> verify_all.py 自動發現 8 支（298 條斷言）
  3. 宣稱 workflow 檔名是 verify_all.yml
     -> 實際是 verify.yml

三次都是同一個病：清單由記憶維護，而記憶不是收據。

verify_all.py 用自動發現解決了 fixture 層的同一個病。
本檔把同一個原則套到結构層。

=====================================================================
兩種模式
=====================================================================
  python3 tools/gen_structure.py
      重新產生 docs/STRUCTURE.md 與 docs/STRUCTURE.json

  python3 tools/gen_structure.py --check
      比對磁碟上的版本與現在該產生的版本。
      不一致 -> 非零退出。

--check 是關鍵。它讓「結构文件過時」變成 CI 失敗，
而不是變成一個沒人發現的謊。

=====================================================================
真值來源
=====================================================================
git ls-files -s

不是 os.walk，不是硬編碼清單。
未被 git 追蹤的檔案不存在於本文件 —— 這是刻意的。
倉庫的真實內容就是 git 認得的內容，其餘都是本機噪音。

=====================================================================
為何不含時間戳與 HEAD SHA
=====================================================================
--check 必須是純函數：同一棵樹 -> 同一份輸出。
若內容含 HEAD SHA，每次 commit 後 --check 必失敗，
那就不是偵測漂移，而是制造假警報。假警報最後會被忽略，
被忽略的閘等於沒有閘。

同理，docs/STRUCTURE.md 與 docs/STRUCTURE.json 本身被排除在
清冊外，否則它們的 blob SHA 會出現在自己的內容裡，形成
自指涉患問題。
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = chr(10)
TAB = chr(9)
LF = bytes([10])

MD_PATH = os.path.join("docs", "STRUCTURE.md")
JSON_PATH = os.path.join("docs", "STRUCTURE.json")
GENERATED = (MD_PATH.replace(os.sep, "/"), JSON_PATH.replace(os.sep, "/"))

# 九宮對照。來源：MIYA-WORLD 建設計畫 v0.7.2。
PALACES = [
    ("4", "kernel", ["kernel"], "常數與已驗值"),
    ("9", "ui", ["ui"], "顯化層"),
    ("2", "canon", ["canon"], "公理與裁示"),
    ("3", "protocol", ["protocol"], "協定"),
    ("5", "root", [""], "中樞（根層檔案）"),
    ("7", "ai-skills", ["ai-skills"], "技能"),
    ("8", "research", ["research"], "論文與外部材料"),
    ("1", "memory", ["memory"], "連續性"),
    ("6", "tools", ["tools", "alchemy"], "工具與煉金術"),
    ("inf", "outer", [".github", "ci", "docs", "hooks"], "外環：CI 與文件"),
]

DIR_TO_PALACE = {}
for _num, _key, _dirs, _desc in PALACES:
    for _d in _dirs:
        DIR_TO_PALACE[_d] = _key


def git(args):
    p = subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if p.returncode != 0:
        raise SystemExit("git " + " ".join(args) + " 失敗："
                         + (p.stderr or "").strip())
    return p.stdout


def tracked():
    """git 追蹤中的檔案。mode / blob sha1 / path。"""
    rows = []
    for line in git(["ls-files", "-s"]).splitlines():
        if not line.strip():
            continue
        left, _sep, path = line.partition(TAB)
        parts = left.split()
        if len(parts) < 3:
            continue
        if path in GENERATED:
            continue
        rows.append({"path": path, "mode": parts[0], "sha1": parts[1]})
    return sorted(rows, key=lambda r: r["path"])


def nlines(path):
    try:
        with open(os.path.join(ROOT, path), "rb") as f:
            data = f.read()
    except OSError:
        return None
    if not data:
        return 0
    n = data.count(LF)
    if data[-1:] != LF:
        n += 1
    return n


def palace_of(path):
    top = path.split("/")[0] if "/" in path else ""
    return DIR_TO_PALACE.get(top, "unclassified")


def collect():
    rows = tracked()
    for r in rows:
        r["lines"] = nlines(r["path"])
        r["palace"] = palace_of(r["path"])

    buckets = {}
    for r in rows:
        buckets.setdefault(r["palace"], []).append(r)

    fixtures = [r["path"] for r in rows
                if r["path"].startswith("tools/verify_")
                and r["path"].endswith(".py")
                and r["path"] != "tools/verify_all.py"]

    return rows, buckets, sorted(fixtures)


def render_md(rows, buckets, fixtures):
    L = []
    a = L.append

    a("# MIYA-WORLD 結构索引")
    a("")
    a("> 本檔由 `tools/gen_structure.py` 產生。**不要手改。**")
    a("> 真值來源是 `git ls-files -s`，不是任何人的記憶。")
    a("> 重新產生：`python3 tools/gen_structure.py`")
    a("> 偵測漂移：`python3 tools/gen_structure.py --check`")
    a("")
    a("本檔不含時間戳與 HEAD SHA。理由：`--check` 必須是純函數。")
    a("若內容含 HEAD，每次 commit 後必失敗，那是制造假警報，")
    a("而被忽略的閘等於沒有閘。")
    a("")
    a("---")
    a("")
    a("## 一、九宮落地狀態")
    a("")
    a("| 宮 | 目錄 | 職能 | 檔數 | 行數 |")
    a("| --- | --- | --- | --- | --- |")
    for num, key, dirs, desc in PALACES:
        items = buckets.get(key, [])
        tot = sum(r["lines"] or 0 for r in items)
        label = "/".join(d if d else "(根)" for d in dirs)
        a("| " + num + " | `" + label + "` | " + desc + " | "
          + str(len(items)) + " | " + str(tot) + " |")
    unc = buckets.get("unclassified", [])
    if unc:
        tot = sum(r["lines"] or 0 for r in unc)
        a("| ? | **未分類** | 不屬任何宮位，須裁示 | "
          + str(len(unc)) + " | " + str(tot) + " |")
    a("")
    if unc:
        a("⚠ 有未分類檔案。這不是錯誤，是訊號：")
        a("要麼九宮對照不完備，要麼檔案放錯位置。須人工裁示。")
        a("")
        for r in unc:
            a("- `" + r["path"] + "`")
        a("")
    a("總計：" + str(len(rows)) + " 個追蹤檔案，"
      + str(sum(r["lines"] or 0 for r in rows)) + " 行。")
    a("（不含本檔與 `docs/STRUCTURE.json`，避免自指涉。）")
    a("")
    a("---")
    a("")
    a("## 二、fixture 清冊")
    a("")
    a("自動發現，非手維清單。`tools/verify_all.py` 用同一規則掃描。")
    a("")
    if fixtures:
        a("| # | fixture | 行數 |")
        a("| --- | --- | --- |")
        i = 0
        for f in fixtures:
            i += 1
            ln = nlines(f)
            a("| " + str(i) + " | `" + f + "` | "
              + (str(ln) if ln is not None else "?") + " |")
        a("")
        a("共 " + str(len(fixtures)) + " 支。執行：`python3 tools/verify_all.py`")
    else\
            :
        a("⚠ 找不到任何 fixture。")
    a("")
    a("---")
    a("")
    a("## 三、逐檔清冊（含 git blob SHA-1）")
    a("")
    a("blob SHA-1 是內容指紋。內容一改，SHA 必改。")
    a("因此本表可直接當 integrity anchor 使用：")
    a("`git hash-object <path>` 對不上本表即為被篡改或未重生。")
    a("")
    for num, key, dirs, desc in PALACES:
        items = buckets.get(key, [])
        if not items:
            continue
        a("### " + num + " ・ " + desc)
        a("")
        a("| 檔案 | 行數 | blob SHA-1 |")
        a("| --- | --- | --- |")
        for r in items:
            ln = r["lines"]
            a("| `" + r["path"] + "` | "
              + (str(ln) if ln is not None else "?") + " | `"
              + r["sha1"][:12] + "` |")
        a("")
    if unc:
        a("### ? ・ 未分類")
        a("")
        a("| 檔案 | 行數 | blob SHA-1 |")
        a("| --- | --- | --- |")
        for r in unc:
            ln = r["lines"]
            a("| `" + r["path"] + "` | "
              + (str(ln) if ln is not None else "?") + " | `"
              + r["sha1"][:12] + "` |")
        a("")
    a("---")
    a("")
    a("## 四、本檔不声稱的事")
    a("")
    a("- 不聲稱任何檔案的內容正確。只聲稱它存在、有多長、指紋為何。")
    a("- 不聲稱 fixture 通過。那是 `tools/verify_all.py` 的職責。")
    a("- 不聲稱九宮對照正確。對照表是宣告（DECLARATIVE），不是定理。")
    a("- 不聲稱未被 git 追蹤的檔案不存在。它只說 git 不認得它們。")
    a("")
    return NL.join(L) + NL


def render_json(rows, buckets, fixtures):
    payload = {
        "schema": "miya-world/structure/v1",
        "generator": "tools/gen_structure.py",
        "truth_source": "git ls-files -s",
        "volatile_fields": [],
        "note": "不含時間戳與 HEAD SHA：--check 必須是純函數。",
        "excluded_from_inventory": list(GENERATED),
        "totals": {
            "files": len(rows),
            "lines": sum(r["lines"] or 0 for r in rows),
            "fixtures": len(fixtures),
        },
        "palaces": [],
        "fixtures": fixtures,
        "files": [
            {
                "path": r["path"],
                "palace": r["palace"],
                "lines": r["lines"],
                "blob_sha1": r["sha1"],
            }
            for r in rows
        ],
    }
    for num, key, dirs, desc in PALACES:
        items = buckets.get(key, [])
        payload["palaces"].append({
            "palace": num,
            "key": key,
            "dirs": dirs,
            "role": desc,
            "files": len(items),
            "lines": sum(r["lines"] or 0 for r in items),
        })
    unc = buckets.get("unclassified", [])
    payload["unclassified"] = [r["path"] for r in unc]
    return json.dumps(payload, ensure_ascii=False, indent=2,
                      sort_keys=True) + NL


def read_text(rel):
    try:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def write_text(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline=NL) as f:
        f.write(text)


def main(argv):
    check = "--check" in argv
    rows, buckets, fixtures = collect()
    md = render_md(rows, buckets, fixtures)
    js = render_json(rows, buckets, fixtures)

    if not check:
        write_text(MD_PATH, md)
        write_text(JSON_PATH, js)
        print("[OK] 已產生 " + MD_PATH)
        print("[OK] 已產生 " + JSON_PATH)
        print("     檔案 " + str(len(rows))
              + "，行數 " + str(sum(r["lines"] or 0 for r in rows))
              + "，fixture " + str(len(fixtures)))
        unc = buckets.get("unclassified", [])
        if unc:
            print("[WARN] " + str(len(unc)) + " 個檔案未分類，須裁示。")
        return 0

    bad = []
    for rel, want in ((MD_PATH, md), (JSON_PATH, js)):
        got = read_text(rel)
        if got is None:
            print("[FAIL] " + rel + " 不存在。請跑："
                  "python3 tools/gen_structure.py")
            bad.append(rel)
        elif got != want:
            print("[FAIL] " + rel + " 與現行樹不符。結构文件已過時。")
            print("       請跑：python3 tools/gen_structure.py 並 commit。")
            bad.append(rel)
        else:
            print("[PASS] " + rel + " 與現行樹一致。")

    if bad:
        print("")
        print("結构文件過時是 FAIL，不是警告。")
        print("一份過時的索引比沒有索引更危險："
              "沒有索引會讓人去查，過時的索引讓人停止查。")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
