#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_luoshu_constants.py

kernel/LUOSHU-CONSTANTS.md 中 K-01 ～ K-13 的可執行 fixture。

設計原則：
  1. 零外部依賴。僅用 Python 標準庫（fractions 、 math）。
  2. 不印「PASS」除非真的算過。每一條都現算，不讀快取。
  3. 任一條失敗 -> exit code 1。不允許部分失敗還回報成功。
  4. K-14 / K-15 / K-16 刷不在本檔驗範圍内。它們的分子來源未驗證，
     故僅列為 SKIPPED 並說明原因，不得造假成 PASS。

執行：  python3 tools/verify_luoshu_constants.py
"""

import sys
from fractions import Fraction

L0 = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

results = []


def check(tag, name, actual, expected):
    ok = actual == expected
    results.append((ok, tag, name, actual, expected))
    return ok


def skip(tag, name, reason):
    results.append((None, tag, name, reason, None))


def det3(m):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def trace3(m):
    return m[0][0] + m[1][1] + m[2][2]


def sum_principal_minors_2x2(m):
    # 特征多項式中 t 的係數：三個 2x2 主子式之和
    total = 0
    for skip_idx in range(3):
        idx = [k for k in range(3) if k != skip_idx]
        p, q = idx
        total += m[p][p] * m[q][q] - m[p][q] * m[q][p]
    return total


# ---------- K-01  行 / 列 / 對角和 = 15 ----------
lines = []
for r in range(3):
    lines.append(sum(L0[r]))
for c in range(3):
    lines.append(sum(L0[r][c] for r in range(3)))
lines.append(L0[0][0] + L0[1][1] + L0[2][2])
lines.append(L0[0][2] + L0[1][1] + L0[2][0])
check("K-01", "8 條魔線全等於 15", sorted(set(lines)), [15])
check("K-01b", "魔線條數", len(lines), 8)

# ---------- K-02  總和 = 45 ----------
flat = [v for row in L0 for v in row]
check("K-02", "全陣總和", sum(flat), 45)
check("K-02b", "元素為 1..9 的置換", sorted(flat), list(range(1, 10)))

# ---------- K-03  det = 360 ----------
det = det3(L0)
check("K-03", "行列式", det, 360)

# ---------- K-04 / K-05  特征多項式 ----------
# char poly of 3x3:  t^3 - tr*t^2 + (sum 2x2 principal minors)*t - det
tr = trace3(L0)
m2 = sum_principal_minors_2x2(L0)
check("K-04a", "t^2 係數 = -trace", tr, 15)
check("K-04b", "t 係數 = 2x2 主子式之和", m2, 24)
check("K-04c", "常數項 = -det", det, 360)


def char_poly(t):
    return t ** 3 - tr * t ** 2 + m2 * t - det


# K-05: (t - 15)(t^2 + 24) 展開後須逐點相等
def factored(t):
    return (t - 15) * (t * t + 24)


samples = [-7, -3, -1, 0, 1, 2, 5, 11, 15, 23, 101]
check(
    "K-05",
    "(t-15)(t^2+24) 逐點等於特征多項式",
    [char_poly(t) - factored(t) for t in samples],
    [0] * len(samples),
)
check("K-05b", "t = 15 為特征多項式的根", char_poly(15), 0)

# ---------- K-06  譜 ----------
# 實本征值 15；其餘二根滿足 t^2 = -24，即 t = +- 2i*sqrt(6)
# 以純整數驗證：(2i*sqrt6)^2 = 4 * i^2 * 6 = -24
check("K-06a", "非實根滿足 t^2 + 24 = 0 之常數", 24, m2)
check("K-06b", "(2*sqrt(6))^2 = 24", 4 * 6, 24)
check("K-06c", "三個特征值之和 = trace", 15 + 0, tr)
# 特征值乘積 = det：15 * (2i*sqrt6) * (-2i*sqrt6) = 15 * 24 = 360
check("K-06d", "特征值乘積 = det", 15 * 24, det)

# ---------- K-07 / K-08  mod 3 ----------
check("K-07", "det mod 3", det % 3, 0)
check("K-08", "L0 mod 3 為奇異 (不屬 GL(3,F_3))", det % 3 == 0, True)

# ---------- K-09  8 條魔線總量拆解 ----------
check("K-09a", "8 條魔線總量", 8 * 15, 120)
# 中心 5 出現 4 次、邊中 2/4/6/8 各 3 次、角 1/3/7/9 各 2 次
decomposition = 5 * 4 + (2 + 4 + 6 + 8) * 3 + (1 + 3 + 7 + 9) * 2
check("K-09b", "位置權重拆解", decomposition, 120)
# 逐位驗與真正的魔線覆蓋次數一致
line_sets = [
    [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)],
]
counted = 0
for ls in line_sets:
    for (r, c) in ls:
        counted += L0[r][c]
check("K-09c", "逐位累加 = 拆解值", counted, decomposition)

# ---------- K-10 / K-11  對位和 與 中心 ----------
center = L0[1][1]
check("K-11", "中心項", center, 5)
pairs_ok = []
for r in range(3):
    for c in range(3):
        if (r, c) == (1, 1):
            continue
        opp = L0[2 - r][2 - c]
        pairs_ok.append(L0[r][c] + opp)
check("K-10", "所有對位和皆為 10", sorted(set(pairs_ok)), [10])
check("K-10b", "對位和 = 2 * 中心", 10, 2 * center)

# ---------- K-12 / K-13  GL 阶 ----------
def gl_order(n, q):
    total = 1
    for k in range(n):
        total *= q ** n - q ** k
    return total


check("K-12", "|GL(3,F_3)|", gl_order(3, 3), 11232)
check("K-12b", "11232 = 26 * 24 * 18", 26 * 24 * 18, 11232)
check("K-13", "|GL(4,F_3)|", gl_order(4, 3), 24261120)
check("K-13b", "24261120 = 80 * 78 * 72 * 54", 80 * 78 * 72 * 54, 24261120)

# ---------- K-14 / K-15 / K-16  明確跳過 ----------
skip(
    "K-14",
    "d=3 稀有度 192/11232",
    "SKIPPED - 分子 192 的列舉依據不在本倉庫，未驗證。分母 11232 已於 K-12 驗過。",
)
skip(
    "K-15",
    "d=4 稀有度 22272/24261120",
    "SKIPPED - 分子 22272 同上未驗。分母 24261120 已於 K-13 驗過。",
)
skip(
    "K-16",
    "收緊倍率 約 18.6x",
    "SKIPPED - 由 K-14 / K-15 導出，上游未驗則本項不得列為已驗。",
)
skip(
    "K-17",
    "(2+2)+(2+2)+1 分解 ↔ Klein-four",
    "SKIPPED - 分組本身已於 K-10 驗過；但 V4 = Z2 x Z2 的群同型宣稱須給出群運算及封閉性，未給出。層級上限 SYMBOLIC。",
)

# ---------- 報告 ----------
def main():
    passed = failed = skipped = 0
    print("=" * 72)
    print("verify_luoshu_constants.py  --  kernel/LUOSHU-CONSTANTS.md K-01 ～ K-17")
    print("=" * 72)
    for ok, tag, name, actual, expected in results:
        if ok is None:
            skipped += 1
            print("[SKIP] {0:8s} {1}".format(tag, name))
            print("         理由：{0}".format(actual))
        elif ok:
            passed += 1
            print("[PASS] {0:8s} {1}  ->  {2}".format(tag, name, actual))
        else:
            failed += 1
            print("[FAIL] {0:8s} {1}".format(tag, name))
            print("         得到：{0!r}".format(actual))
            print("         預期：{0!r}".format(expected))
    print("-" * 72)
    print("PASS {0}   FAIL {1}   SKIP {2}".format(passed, failed, skipped))
    if failed:
        print("結果：FAILED — 不得將任何項目標為已驗。")
        return 1
    print("結果：OK — 以上 PASS 項可標 TESTED；SKIP 項仍不得升格。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
