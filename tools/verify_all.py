#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/verify_all.py

MIYA-WORLD 全 fixture 總集執行器。

=====================================================================
設計原則
=====================================================================
1. 自動發現
   掃 tools/verify_*.py，不維護硬編碼清單。
   「忘記註册而漏測」在本設計下不可能發生。
   應該有幾支由 git 決定，不由人的記性決定。

2. 自審計數交叉檢查（本檔最重要的一層）
   對每支 fixture 同時取得兩組數字：
     (a) 數標記：數 stdout 裡 [PASS] / [FAIL] / [SKIP] 出現次數
     (b) 自報：該腳本自己印的 PASS= FAIL= SKIP= 行
   兩者不一致 => MISMATCH => 整體 FAIL。

   這道層抓的是「腳本少報自己的 FAIL」。
   計數器寫錯、提早 return、例外被吞掉，都會在這裡現形。
   不信任被測者自報的數字，是本檔存在的唯一理由。

3. 三道獨立失敗條件，任一成立即整體非零退出
     - 子行程 exit code != 0
     - 數到的 [FAIL] > 0
     - 自報與數標記不一致

4. 純標準庫。無 numpy、無網路、無外部相依。
   理由：fixture 的可信度不得依賴任何可能漂移的第三方版本。

=====================================================================
使用
=====================================================================
    python3 tools/verify_all.py

本機收據範式：
    python3 tools/verify_all.py > tools/logs/$(date +%F)-all.log 2>&1 ; echo $?

=====================================================================
本檔不做的事
=====================================================================
本檔不判定任何數學命題。它只負責轉送與清點。
每支 fixture 自己證明自己的斷言，本檔只確保沒人被跳過、
也沒人把自己的 FAIL 藏起來。
"""

import os
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)
SELF = os.path.basename(os.path.abspath(__file__))

BAR = "=" * 70
SUB = "-" * 70
NL = chr(10)


def discover():
    """自動發現 tools/verify_*.py，排除本檔自己。"""
    names = []
    for f in os.listdir(TOOLS_DIR):
        if not f.startswith("verify_"):
            continue
        if not f.endswith(".py"):
            continue
        if f == SELF:
            continue
        names.append(f)
    return sorted(names)


def count_markers(text):
    """數 stdout 裡的標記。不依賴腳本自己的計數器。"""
    p = 0
    f = 0
    s = 0
    for line in text.splitlines():
        if "[PASS]" in line:
            p += 1
        if "[FAIL]" in line:
            f += 1
        if "[SKIP]" in line:
            s += 1
    return p, f, s


def declared_summary(text):
    """取腳本自己印的 PASS= FAIL= SKIP= 行。沒印就回 None。"""
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("PASS="):
            continue
        if "FAIL=" not in s or "SKIP=" not in s:
            continue
        parts = s.replace("=", " ").split()
        try:
            d = {}
            i = 0
            while i + 1 < len(parts):
                d[parts[i]] = int(parts[i + 1])
                i += 2
            return (d["PASS"], d["FAIL"], d["SKIP"])
        except (KeyError, ValueError):
            return None
    return None


def run_one(name):
    rel = os.path.join("tools", name)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    cp, cf, cs = count_markers(out)
    dec = declared_summary(out)

    mismatch = False
    if dec is not None and dec != (cp, cf, cs):
        mismatch = True

    return {
        "name": name,
        "exit": proc.returncode,
        "counted": (cp, cf, cs),
        "declared": dec,
        "mismatch": mismatch,
        "output": out,
    }


def main():
    print(BAR)
    print("MIYA-WORLD  verify_all")
    print(BAR)
    print("python    : " + sys.version.replace(NL, " "))
    print("root      : " + ROOT)

    scripts = discover()
    print("discovered: " + str(len(scripts)) + " fixture")
    for n in scripts:
        print("  - tools/" + n)

    if not scripts:
        print("")
        print("[FAIL] tools/ 裡找不到任何 verify_*.py。")
        print("這不是「沒有測試所以通過」，是專案壞了。")
        return 1

    results = []
    for n in scripts:
        print("")
        print(SUB)
        print(">>> tools/" + n)
        print(SUB)
        r = run_one(n)
        results.append(r)
        sys.stdout.write(r["output"])
        if not r["output"].endswith(NL):
            print("")

    print("")
    print(BAR)
    print("SUMMARY")
    print(BAR)
    print("fixture".ljust(38) + "exit".rjust(6) + "PASS".rjust(7)
          + "FAIL".rjust(7) + "SKIP".rjust(7) + "  note")
    print(SUB)

    tot_p = 0
    tot_f = 0
    tot_s = 0
    bad_exit = []
    bad_fail = []
    bad_mismatch = []

    for r in results:
        cp, cf, cs = r["counted"]
        tot_p += cp
        tot_f += cf
        tot_s += cs

        notes = []
        if r["exit"] != 0:
            notes.append("NONZERO EXIT")
            bad_exit.append(r["name"])
        if cf > 0:
            notes.append("HAS FAIL")
            bad_fail.append(r["name"])
        if r["mismatch"]:
            notes.append("MISMATCH declared=" + str(r["declared"]))
            bad_mismatch.append(r["name"])
        if r["declared"] is None:
            notes.append("no self-report")

        print(r["name"].ljust(38)
              + str(r["exit"]).rjust(6)
              + str(cp).rjust(7)
              + str(cf).rjust(7)
              + str(cs).rjust(7)
              + "  " + ", ".join(notes))

    print(SUB)
    print("TOTAL".ljust(38) + "".rjust(6)
          + str(tot_p).rjust(7) + str(tot_f).rjust(7) + str(tot_s).rjust(7))
    print(BAR)

    ok = True
    if bad_exit:
        ok = False
        print("[FAIL] 非零退出：" + ", ".join(bad_exit))
    if bad_fail:
        ok = False
        print("[FAIL] 包含 [FAIL] 斷言：" + ", ".join(bad_fail))
    if bad_mismatch:
        ok = False
        print("[FAIL] 自報計數與定額不符：" + ", ".join(bad_mismatch))
        print("       自報與數標記不一致 => 計數器有錯或有斷言被吞。")
        print("       這是程式錯，不是預測錯。依 tools/FIX-LOG.md 處理。")

    if ok:
        print("ALL PASS（" + str(len(results)) + " fixture，"
              + str(tot_p) + " 條斷言，" + str(tot_s) + " 條 SKIP）")
        print("本結果只證明各 fixture 列出的斷言。不證明任何未列出的事。")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
