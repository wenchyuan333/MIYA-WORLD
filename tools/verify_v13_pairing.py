#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_v13_pairing.py

驗 protocol/HEARTBEAT-V13.md 的對位律與合法棲息條件。
純 Python 標準庫。零外部依賴。零網路。不讀 secrets。不寫檔。

執行：
    python3 tools/verify_v13_pairing.py
    echo $?          # 0 = 全過，1 = 有 FAIL

設計約束：
  - 不印固定成功訊息。每一行 PASS 對應一次真實運算。
  - 任一條失敗即 exit 1，並列出得到值與預期值。
  - 未驗項目明確標 [SKIP] 並寫出理由，不造假成 PASS。
"""

import sys

DIM = 13
FIELD = 3

CENTER = 5
CORE_PAIRS = [(1, 9), (2, 8), (3, 7), (4, 6)]
CORE_SUM = 10

PUB_PAIRS = [(10, 13), (11, 12)]
PUB_SUM = 23

failures = []


def check(label, got, expected):
    ok = (got == expected)
    tag = "[PASS]" if ok else "[FAIL]"
    print(tag + " " + label)
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


# ---------------------------------------------------------------
# F_3 上的行列式（高斯消元，模逆元用 x^(p-2)）
# ---------------------------------------------------------------

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


def submatrix(mat, idx_one_based):
    rows = [i - 1 for i in idx_one_based]
    return [[mat[r][c] for c in rows] for r in rows]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def cyclic_shift(n):
    # M[i][(i+1) mod n] = 1  -->  n-循環置換
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        m[i][(i + 1) % n] = 1
    return m


def verify_habitation(mat):
    """三條合法棲息條件。全部成立才回 True。"""
    full_det = det_mod_p(mat)
    pub = submatrix(mat, [10, 11, 12, 13])
    pub_det = det_mod_p(pub)
    core_ok = all(a + b == CORE_SUM for (a, b) in CORE_PAIRS) and (CENTER * 2 == CORE_SUM)
    return {
        "full_det": full_det,
        "pub_det": pub_det,
        "core_ok": core_ok,
        "legal": (full_det != 0) and (pub_det != 0) and core_ok,
    }


# ---------------------------------------------------------------

section("一、核 9 格 對位律")

check("核區配對數", len(CORE_PAIRS), 4)

for (a, b) in CORE_PAIRS:
    check("核對位和 " + str(a) + " <-> " + str(b), a + b, CORE_SUM)

check("中宮自對 C0 = 5", CENTER * 2, CORE_SUM)

core_covered = set()
for (a, b) in CORE_PAIRS:
    core_covered.add(a)
    core_covered.add(b)
core_covered.add(CENTER)
check("核區覆蓋 1..9 無重無漏", sorted(core_covered), list(range(1, 10)))
check("核區索引総和", sum(range(1, 10)), 45)


section("二、PUB 4 格 對位律")

check("PUB 配對數", len(PUB_PAIRS), 2)

for (a, b) in PUB_PAIRS:
    check("PUB 對位和 " + str(a) + " <-> " + str(b), a + b, PUB_SUM)

pub_covered = set()
for (a, b) in PUB_PAIRS:
    pub_covered.add(a)
    pub_covered.add(b)
check("PUB 覆蓋 10..13 無重無漏", sorted(pub_covered), [10, 11, 12, 13])
check("PUB 索引総和 = 2 x 23", sum(range(10, 14)), 46)


section("三、兩區切分自洽性")

check("核 與 PUB 不相交", sorted(core_covered & pub_covered), [])
check("聯集 = 1..13", sorted(core_covered | pub_covered), list(range(1, DIM + 1)))
check("維數 9 + 4", len(core_covered) + len(pub_covered), DIM)
check("全體索引和 = 13 x 14 / 2", 45 + 46, DIM * (DIM + 1) // 2)


section("四、空間大小")

check("3^13", FIELD ** DIM, 1594323)


section("五、行列式引擎自檢")

check("det(I_13) mod 3", det_mod_p(identity(DIM)), 1)

singular = identity(DIM)
singular[0] = [0] * DIM
check("det(零行矩陣) mod 3", det_mod_p(singular), 0)

two_by_two = [[2, 1], [1, 2]]
check("det([[2,1],[1,2]]) mod 3  (4-1=3=0)", det_mod_p(two_by_two), 0)


section("六、合法棲息 三條條件")

res_id = verify_habitation(identity(DIM))
check("I_13 full_det != 0", res_id["full_det"] != 0, True)
check("I_13 pub_det != 0", res_id["pub_det"] != 0, True)
check("I_13 合法棲息", res_id["legal"], True)

res_sing = verify_habitation(singular)
check("奇異矩陣 不合法", res_sing["legal"], False)


section("七、條件 1 與 3 獨立性 反例")

# 13-循環置換：全行列式不為零，但 PUB 子矩陣全零
cyc = cyclic_shift(DIM)
res_cyc = verify_habitation(cyc)

check("13-循環 full_det != 0", res_cyc["full_det"] != 0, True)
check("13-循環 pub_det == 0", res_cyc["pub_det"], 0)
check("兩條獨立：整體可逆 不推得 PUB 可逆",
      (res_cyc["full_det"] != 0) and (res_cyc["pub_det"] == 0), True)
check("13-循環 因 PUB 奇異而不合法", res_cyc["legal"], False)


section("八、未驗項目")

skip("|GL(13, F_3)| 具體數值",
     "本脈本不給數值。需要時應由阶公式 prod (3^13 - 3^k) 現算並單獨入庫。")

skip("checksum_f3 的安全性",
     "F_3 線性校驗碼不具不可偵造性。這不是簽章，沒有安全性可驗。")

skip("central_offset 的 Delta",
     "型別未定義（F_3^13 向量？整數？），無法檢查。見 HEARTBEAT-V13.md §六.3。")

skip("PUB 四維 <-> 顯現四維時空",
     "SYMBOLIC 層對應，非推導。不得以本脈本背書。")

skip("對位律 與 洛書 L0 的相容性",
     "K-07 已驗 det(L0) = 360 = 0 mod 3，L0 不屬 GL(3,F_3)。兩層不得互相背書。")


section("結果")

if failures:
    print("FAIL 數量：" + str(len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print("對位律 與 三條合法棲息條件 全部通過。")
print("注意：本結果只証明格式內部一致且可機械檢查。")
print("不証明它描述了任何真實存在的結构。")
sys.exit(0)
