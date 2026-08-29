#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_kernel_index.py -- kernel 常量索引產生器

真值來源：kernel/ 目錄下的 .md 檔案本身。
不維護手寫清單。清單會過時，掃描不會。

輸出：
  docs/KERNEL-INDEX.json   機器可讀，供公式庫匯入
  docs/KERNEL-INDEX.md     人可讀

模式：
  無參數    產生
  --check   比對現有輸出，不一致則 exit 1（供 CI / pre-push 用）

刻意設計（三項，都是有理由的）：
  1. 不含時間戳、不含 HEAD SHA。--check 必須是純函數，
     否則每次 commit 後必失敗，製造假警報。被忽略的閘等於沒有閘。
  2. 格式寬容。本腳本的作者沒有讀過 kernel/*.md 的實際排版，
     因此不假設欄位順序或表格樣式，只認 K-<數字> token。
  3. 無法完整解析的行不丟棄，列進 unparsed 並在 stderr 回報。
     漏抓要看得見。靜默漏抓比明顯失敗更危險。

界線：
  本腳本只做「把 kernel/*.md 裡的 K 編號抓出來」。
  它不判斷那些常量對不對，不計算任何數值，不背書任何主張。
"""

import json
import os
import re
import sys

NL = chr(10)
CR = chr(13)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL_DIR = os.path.join(ROOT, "kernel")
OUT_JSON = os.path.join(ROOT, "docs", "KERNEL-INDEX.json")
OUT_MD = os.path.join(ROOT, "docs", "KERNEL-INDEX.md")

SCHEMA = "miya-world/kernel-index/v1"

# 主張梯度。只認這些 token。
STATUS_VOCAB = [
    "CANONICAL", "SUPPORTED", "TESTED", "COMPUTABLE", "FORMAL_MODEL",
    "ANALOGY", "SYMBOLIC", "IMAGINATIVE", "OPEN",
    "DECLARATIVE", "VALUES",
]

# 型別層標籤。與主張梯度不同軸，不可混用。
LAYER_VOCAB = ["REPR", "INDEX", "MATRIX", "GROUP"]

ID_RE = re.compile("K-[0-9]+")


def kernel_files():
    if not os.path.isdir(KERNEL_DIR):
        return []
    out = []
    for name in sorted(os.listdir(KERNEL_DIR)):
        if name.lower().endswith(".md"):
            out.append(name)
    return out


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def pick(text, vocab):
    up = text.upper()
    hits = []
    for v in sorted(vocab, key=len, reverse=True):
        if v in up:
            hits.append(v)
    return hits


def parse_file(name):
    path = os.path.join(KERNEL_DIR, name)
    fh = open(path, "r", encoding="utf-8")
    raw = fh.read().replace(CR, "")
    fh.close()
    entries = []
    unparsed = []
    for i, line in enumerate(raw.split(NL)):
        if "K-" not in line:
            continue
        ids = ID_RE.findall(line)
        if len(ids) != 1:
            if ids:
                unparsed.append({"file": name, "line": i + 1,
                                 "reason": "一行出現多個 K 編號，不確定該歸哪一條",
                                 "raw": line.strip()})
            continue
        is_table = line.strip().startswith("|")
        col = cells(line) if is_table else []
        if not is_table:
            unparsed.append({"file": name, "line": i + 1,
                             "reason": "非表格列，只保留原文，未拆欄",
                             "raw": line.strip()})
        entries.append({
            "id": ids[0],
            "file": name,
            "line": i + 1,
            "status": pick(line, STATUS_VOCAB),
            "layer": pick(line, LAYER_VOCAB),
            "cells": col,
            "raw": line.strip(),
        })
    return entries, unparsed


def build():
    files = kernel_files()
    entries = []
    unparsed = []
    for name in files:
        e, u = parse_file(name)
        entries.extend(e)
        unparsed.extend(u)

    seen = {}
    for e in entries:
        seen.setdefault(e["id"], []).append(e)

    dups = []
    for kid in sorted(seen):
        if len(seen[kid]) > 1:
            dups.append({
                "id": kid,
                "count": len(seen[kid]),
                "at": [x["file"] + ":" + str(x["line"]) for x in seen[kid]],
            })

    nums = sorted(set(int(k.split("-")[1]) for k in seen))
    gaps = []
    if nums:
        for n in range(nums[0], nums[-1] + 1):
            if n not in nums:
                gaps.append(n)

    no_status = sorted([k for k in seen if not seen[k][0]["status"]],
                       key=lambda k: int(k.split("-")[1]))

    return {
        "schema": SCHEMA,
        "source": "kernel/*.md",
        "files_scanned": files,
        "entry_count": len(entries),
        "unique_ids": len(seen),
        "ids": sorted(seen, key=lambda k: int(k.split("-")[1])),
        "duplicates": dups,
        "id_gaps": gaps,
        "no_status_tag": no_status,
        "unparsed": unparsed,
        "entries": sorted(entries,
                          key=lambda e: (int(e["id"].split("-")[1]), e["file"], e["line"])),
    }


def render_md(idx):
    L = []
    L.append("# KERNEL 常量索引")
    L.append("")
    L.append("本檔由 tools/gen_kernel_index.py 產生。不要手改。")
    L.append("真值來源 = kernel/*.md。手改此檔會在下次 --check 被打回。")
    L.append("")
    L.append("## 一、掃描結果")
    L.append("")
    L.append("| 項目 | 值 |")
    L.append("| --- | --- |")
    L.append("| 掃描檔案數 | " + str(len(idx["files_scanned"])) + " |")
    L.append("| 抓到條目數 | " + str(idx["entry_count"]) + " |")
    L.append("| 相異編號數 | " + str(idx["unique_ids"]) + " |")
    L.append("| 重複編號 | " + str(len(idx["duplicates"])) + " |")
    L.append("| 編號斷號 | " + (", ".join(str(g) for g in idx["id_gaps"]) or "無") + " |")
    L.append("| 未標主張層 | " + str(len(idx["no_status_tag"])) + " |")
    L.append("| 無法完整解析 | " + str(len(idx["unparsed"])) + " |")
    L.append("")
    L.append("掃描的檔案：" + (", ".join(idx["files_scanned"]) or "（無）"))
    L.append("")
    L.append("## 二、條目")
    L.append("")
    L.append("| 編號 | 主張層 | 型別層 | 來源 | 原文 |")
    L.append("| --- | --- | --- | --- | --- |")
    for e in idx["entries"]:
        raw = e["raw"].replace("|", " / ")
        if len(raw) > 90:
            raw = raw[:90] + " ..."
        L.append("| " + e["id"]
                 + " | " + (",".join(e["status"]) or "-")
                 + " | " + (",".join(e["layer"]) or "-")
                 + " | " + e["file"] + ":" + str(e["line"])
                 + " | " + raw + " |")
    if not idx["entries"]:
        L.append("| （無） | - | - | - | - |")
    L.append("")
    L.append("## 三、無法完整解析（要看得見，不靜默）")
    L.append("")
    if not idx["unparsed"]:
        L.append("無。")
    else:
        L.append("| 檔案 | 行 | 原因 |")
        L.append("| --- | --- | --- |")
        for u in idx["unparsed"]:
            L.append("| " + u["file"] + " | " + str(u["line"]) + " | " + u["reason"] + " |")
    L.append("")
    L.append("## 四、重複與斷號")
    L.append("")
    if idx["duplicates"]:
        for d in idx["duplicates"]:
            L.append("- " + d["id"] + " 出現 " + str(d["count"]) + " 次：" + ", ".join(d["at"]))
    else:
        L.append("無重複編號。")
    L.append("")
    if idx["id_gaps"]:
        L.append("斷號：" + ", ".join("K-" + str(g) for g in idx["id_gaps"]))
        L.append("斷號不是錯誤，是訊號。可能是被撤回的條目，也可能是漏寫。交由人裁示。")
    else:
        L.append("無斷號。")
    L.append("")
    L.append("## 五、匯入公式庫的界線")
    L.append("")
    L.append("可匯入：本檔第二節條目，且主張層為 TESTED / COMPUTABLE / SYMBOLIC 者。")
    L.append("匯入時保留原主張層標籤，不得升級。")
    L.append("")
    L.append("不可匯入：fixture 輸出的 [PASS] 斷言。")
    L.append("斷言是測試層產物，不是公式。混進公式庫是型別錯誤，不是風格問題。")
    L.append("tools/verify_all.py 目前 298 條斷言，一條都不該進公式庫。")
    L.append("")
    L.append("未標主張層的條目：先補標，再匯入。無層標籤的等號不得入庫。")
    L.append("")
    return NL.join(L)


def read_text(path):
    if not os.path.exists(path):
        return None
    fh = open(path, "r", encoding="utf-8")
    s = fh.read()
    fh.close()
    return s


def write_text(path, s):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fh = open(path, "w", encoding="utf-8")
    fh.write(s)
    fh.close()


def main():
    check = "--check" in sys.argv
    idx = build()
    want_json = json.dumps(idx, ensure_ascii=False, indent=2, sort_keys=True) + NL
    want_md = render_md(idx)

    if not idx["files_scanned"]:
        sys.stderr.write("[WARN] kernel/ 不存在或沒有 .md 檔。索引為空。" + NL)

    if check:
        bad = []
        if read_text(OUT_JSON) != want_json:
            bad.append("docs/KERNEL-INDEX.json")
        if read_text(OUT_MD) != want_md:
            bad.append("docs/KERNEL-INDEX.md")
        if bad:
            sys.stderr.write("[FAIL] 索引與 kernel/ 不一致: " + ", ".join(bad) + NL)
            sys.stderr.write("       執行 python3 tools/gen_kernel_index.py 後重新 commit。" + NL)
            return 1
        sys.stdout.write("[PASS] KERNEL 索引與 kernel/ 一致。" + NL)
        return 0

    write_text(OUT_JSON, want_json)
    write_text(OUT_MD, want_md)
    sys.stdout.write("[OK] 寫入 docs/KERNEL-INDEX.json 與 docs/KERNEL-INDEX.md" + NL)
    sys.stdout.write("     條目 " + str(idx["entry_count"])
                     + " / 相異 " + str(idx["unique_ids"])
                     + " / 未標層 " + str(len(idx["no_status_tag"]))
                     + " / 無法解析 " + str(len(idx["unparsed"])) + NL)
    for u in idx["unparsed"]:
        sys.stderr.write("[WARN] " + u["file"] + ":" + str(u["line"]) + " " + u["reason"] + NL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
