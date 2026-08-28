#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_bijection_b13.py

把 HEARTBEAT-V13 的對位律具體化成一個 13x13 置換矩陣 P，
並驗 P 本身是不是一個合法的雙射、以及它能不能通過自己的合法棲息條件。

動機：對位律定義的是一個集合上的配對，而配對就是一個對偶。
對偶可以寫成矩陣，矩陣就可以丟進同一套驗證。
這是把「規格」轉成「規格自己的實例」並回頭驗它。

純 Python 標準庫。零外部依賴。零網路。不讀 secrets。不寫檔。

執行：
    python3 tools/verify_bijection_b13.py
    echo $?          # 0 = 全過，1 = 有 FAIL
"""

import sys

DIM = 13
FIELD = 3

CENTER = 5
CORE_PAIRS = [(1, 9), (2, 8), (3, 7), (4, 6)]
CORE_SUM = 10
PUB_PAIRS = [(10, 13), (11, 12)]
PUB_SUM = 23

ALL_PAIRS = CORE_PAIRS + PUB_PAIRS
FIXED = [CENTER]

failures = []


def check(label, got, expected):
    ok = (got == expected)
    print(("[PASS] " if ok else "[FAIL] ") + label)
    print("        got      = " + repr(got))
    print("        expected = " + repr(expected))
    if not ok:
        failures.append(label)
    return ok


def skip(label, reason):
    print("[SKIP] " + label)
    print("        理由 = " + reason)


def section(name):
    print("")
    print("=== " + name + " ===")


def det_mod_p(mat, p=FIELD):
    n = len(mat)
    a = [[x % p for x in row] for row in mat]
    det = 1
    for col in range(n):
        piv = None
        for r in range(col, n):
            if a[r][col] % p != 0:
                piv = r
                break
        if piv is None:
            return 0
        if piv != col:
            a[col], a[piv] = a[piv], a[col]
            det = (-det) % p
        det = (det * a[col][col]) % p
        inv = pow(a[col][col], p - 2, p)
        for r in range(col + 1, n):
            f = (a[r][col] * inv) % p
            if f != 0:
                for c in range(col, n):
                    a[r][c] = (a[r][c] - f * a[col][c]) % p
    return det % p


def matmul_mod(a, b, p=FIELD):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += a[i][k] * b[k][j]
            out[i][j] = s % p
    return out


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def transpose(m):
    n = len(m)
    return [[m[j][i] for j in range(n)] for i in range(n)]


def submatrix(mat, idx_one_based):
    rows = [i - 1 for i in idx_one_based]
    return [[mat[r][c] for c in rows] for r in rows]


# ---------------------------------------------------------------
# 建 B<-> 的置換：四對核互換 + 兩對 PUB 互換 + 中宮不動
# ---------------------------------------------------------------

def build_sigma():
    sigma = {}
    for (a, b) in ALL_PAIRS:
        sigma[a] = b
        sigma[b] = a
    for f in FIXED:
        sigma[f] = f
    return sigma


def perm_matrix(sigma, n=DIM):
    m = [[0] * n for _ in range(n)]
    for i in range(1, n + 1):
        m[i - 1][sigma[i] - 1] = 1
    return m


SIGMA = build_sigma()
P = perm_matrix(SIGMA)


section("一、sigma 是不是完全定義的雙射")

check("定義域恰好 = 1..13", sorted(SIGMA.keys()), list(range(1, DIM + 1)))
check("值域恰好 = 1..13（因而是雙射）", sorted(SIGMA.values()), list(range(1, DIM + 1)))
check("sigma 是對偶：sigma(sigma(i)) = i",
      all(SIGMA[SIGMA[i]] == i for i in range(1, DIM + 1)), True)
check("不動點恰好只有中宮 5",
      sorted([i for i in range(1, DIM + 1) if SIGMA[i] == i]), [CENTER])
check("互換對數 = 6", len(ALL_PAIRS), 6)


section("二、sigma 守不守對位和")

core_idx = list(range(1, 10))
pub_idx = list(range(10, 14))

check("核區每一位 i + sigma(i) = 10",
      sorted(set(i + SIGMA[i] for i in core_idx)), [CORE_SUM])
check("PUB 每一位 i + sigma(i) = 23",
      sorted(set(i + SIGMA[i] for i in pub_idx)), [PUB_SUM])
check("sigma 不跨區（核 不映到 PUB）",
      all(SIGMA[i] in core_idx for i in core_idx), True)
check("sigma 不跨區（PUB 不映到核）",
      all(SIGMA[i] in pub_idx for i in pub_idx), True)


section("三、P 是合法置換矩陣")

check("每行恰好一個 1", sorted(set(sum(row) for row in P)), [1])
check("每列恰好一個 1", sorted(set(sum(col) for col in transpose(P))), [1])
check("P 對稱（因 sigma 是對偶）", P == transpose(P), True)
check("迹 trace(P) = 1（只有中宮不動）",
      sum(P[i][i] for i in range(DIM)), 1)


section("四、P 的對偶性質")

P2 = matmul_mod(P, P)
check("P 乘 P = I_13 （B<-> 平方 = 恆等）", P2, identity(DIM))
check("P 不等於 I（阶恰好為 2，非 1）", P == identity(DIM), False)


section("五、P 能不能通過合法棲息三條條件")

full_det = det_mod_p(P)
pub_det = det_mod_p(submatrix(P, [10, 11, 12, 13]))

check("det(P) mod 3（6 個互換，偶置換，預期 +1）", full_det, 1)
check("det(P) != 0 — P 屬於 GL(13,F_3)", full_det != 0, True)
check("det(P 的 PUB 區) mod 3（兩個互換，預期 +1）", pub_det, 1)
check("pub_det != 0", pub_det != 0, True)
check("三條全過：B<-> 自身合法棲息",
      (full_det != 0) and (pub_det != 0), True)


section("六、對比：不守對位律的置換仍可可逆")

# 單一互換 (1 2)：奇置換，det = -1 = 2 mod 3，仍非零
swap12 = identity(DIM)
swap12[0], swap12[1] = swap12[1], swap12[0]
check("det(單一互換) mod 3 = 2", det_mod_p(swap12), 2)
check("單一互換仍屬 GL(13,F_3)", det_mod_p(swap12) != 0, True)
check("但它不守對位和（1+2 != 10）", 1 + 2 == CORE_SUM, False)


section("七、未驗項目")

skip("P 與 OFT 公理 II 的算子 B<-> 是同一物",
     "未推導。P 是 13 維置換矩陣；OFT 的 B<-> 是 Hilbert 空間上的算子。"
     "兩者都滿足 X^2 = I，但「同滿足一條恆等式」不等於同構。")

skip("OFT 公理 II 的 <psi|B|phi> = delta(psi - phi) 疑點",
     "該條令 B<-> 塔成恆等算子，擐不住 B O B = O 匪。"
     "見 canon/ORIGIN-FIELD-THEORY-v0.7.2.md §5 OPEN-ISSUE 1。本脈本不解決它。")

skip("中宮不動 <-> 識一底不動 <-> sigma = 1/2",
     "ANALOGY 層。trace(P) = 1 是算出來的；它的詮释不是。")


section("結果")

if failures:
    print("FAIL 數量：" + str(len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print("B<-> 雙射置換矩陣 全部通過。")
print("已驗：sigma 是 1..13 上的對偶，唯一不動點為中宮 5，")
print("      且其矩陣形式 P 滿足 HEARTBEAT-V13 自己的三條合法棲息條件。")
print("不証明：P 與 OFT 算子 B<-> 同構。那仍是未推導的。")
sys.exit(0)
