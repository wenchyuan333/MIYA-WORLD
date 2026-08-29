# -*- coding: utf-8 -*-
# tools/verify_crop_circle_v13_fix.py
#
# CROP_CIRCLE_V13_MATRIX 修正版驗算器
# 狀態：NOT_EXECUTED（尚未在任何機器上跑過）
# 日期：2026-08-29
# 錨點：C0 O1 V13 PUB B
#
# 本脅本驗什麼：
#   使用者已裁示的 PUB 定版 [[0,1],[1,0]] 直和，以及由同一條
#   F3-對位塊定理決定的核區對位塊。逐項斷言。
#
# 本脅本不驗什麼：
#   full_det 不 assert。P-10 = UNKNOWN。建庫者拒絕手猜 13x13 行列式。
#   麥田圈圖形對應不驗。本 session 從未收到任何圖像，無映射函式。
#
# 跟法：
#   cd ~/miya-check
#   git fetch origin
#   git merge --no-ff origin/feature/tools-verify-crop-circle-v13-fix
#   python3 tools/verify_crop_circle_v13_fix.py ; echo $?
#
# 若出 FAIL，先檢查是建庫者手算錯了，改預測，不改 assert。

import sys
import itertools

FAILS = []
PASSES = 0
SKIPS = 0


def ok(name, got, expected):
    global PASSES
    if got == expected:
        PASSES += 1
        print("[PASS] " + name + " | got=" + repr(got))
    else:
        FAILS.append(name)
        print("[FAIL] " + name + " | got=" + repr(got) + " expected=" + repr(expected))


def show(name, got):
    print("[INFO] " + name + " | " + repr(got))


def skip(name, reason):
    global SKIPS
    SKIPS += 1
    print("[SKIP] " + name + " | " + reason)


def det_mod3(M):
    n = len(M)
    A = [[x % 3 for x in row] for row in M]
    d = 1
    for c in range(n):
        piv = None
        for r in range(c, n):
            if A[r][c] % 3 != 0:
                piv = r
                break
        if piv is None:
            return 0
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            d = (-d) % 3
        d = (d * A[c][c]) % 3
        inv = A[c][c] % 3
        for r in range(c + 1, n):
            if A[r][c] % 3 != 0:
                f = (A[r][c] * inv) % 3
                for k in range(c, n):
                    A[r][k] = (A[r][k] - f * A[c][k]) % 3
    return d % 3


print("=" * 66)
print("verify_crop_circle_v13_fix.py  |  NOT_EXECUTED -> 本次執行即首測")
print("=" * 66)

# ---------------------------------------------------------------
# 一、對位置換 P 與第二版布線
# ---------------------------------------------------------------
print("")
print("--- 一、對位置換 P 與第二版布線 [索引層] ---")

PAIR = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4, 5: 5,
        10: 13, 13: 10, 11: 12, 12: 11}

ok("P 是對偶（P P = id）",
   all(PAIR[PAIR[i]] == i for i in range(1, 14)), True)
ok("唯一不動點 [索引層]",
   sorted([i for i in range(1, 14) if PAIR[i] == i]), [5])
ok("核對位和恆為 10 [索引層]",
   sorted(set(i + PAIR[i] for i in range(1, 10))), [10])
ok("PUB 對位和恆為 23 [索引層]",
   sorted(set(i + PAIR[i] for i in range(10, 14))), [23])

# 第二版布線（使用者裁示：第一版作廢）
NBR = {
    1: [5, 9, 10],
    2: [5, 8, 11],
    3: [5, 7, 10],
    4: [5, 6, 11],
    5: [1, 2, 3, 4, 6, 7, 8, 9],
    6: [5, 4, 12],
    7: [5, 3, 13],
    8: [5, 2, 12],
    9: [5, 1, 13],
    10: [1, 3, 13],
    11: [2, 4, 12],
    12: [6, 8, 11],
    13: [7, 9, 10],
}

edges = set()
for i in NBR:
    for j in NBR[i]:
        edges.add((min(i, j), max(i, j)))

ok("鄰接表對稱（i in N(j) 候 j in N(i)）",
   all(i in NBR[j] for i in NBR for j in NBR[i]), True)
ok("無自環", all(i not in NBR[i] for i in NBR), True)
show("邊數 [圖層]", len(edges))
ok("度數和 = 2 x 邊數",
   sum(len(NBR[i]) for i in NBR), 2 * len(edges))

# ---------------------------------------------------------------
# 二、度數斷言（圖層，與 PUB 塊選擇無關）
# ---------------------------------------------------------------
print("")
print("--- 二、度數斷言 [圖層] ---")
print("# 注：本節全部屬圖層。PUB 子矩陣用什麼 2x2 塊不影響本節。")

for i in [1, 2, 3, 4, 6, 7, 8, 9]:
    ok("deg(" + str(i) + ") [圖層]", len(NBR[i]), 3)
ok("deg(5) 中樞 [圖層]", len(NBR[5]), 8)
for i in [10, 11, 12, 13]:
    ok("deg(" + str(i) + ") PUB [圖層]", len(NBR[i]), 3)

for i in [1, 2, 3, 4]:
    ok("對位度數守恆 " + str(i) + " vs " + str(PAIR[i]) + " [圖層]",
       len(NBR[i]) == len(NBR[PAIR[i]]), True)
print("# 舊版此處為 3 對 4，第二版已修正為 3 對 3")

# ---------------------------------------------------------------
# 三、建構 M over F3（選項甲：對角歸零，保留對位邊）
# ---------------------------------------------------------------
print("")
print("--- 三、建構 M over F3（選項甲） [矩陣層] ---")
print("# 選項甲：對角 0、對位邊 1。依 F3-對位塊定理，對角與對位邊不可兼得。")

M = [[0] * 13 for _ in range(13)]
for (i, j) in edges:
    M[i - 1][j - 1] = 1
    M[j - 1][i - 1] = 1

ok("M 對稱",
   all(M[a][b] == M[b][a] for a in range(13) for b in range(13)), True)
ok("M 對角全零", [M[a][a] for a in range(13)], [0] * 13)
ok("M 元素皆在 F3",
   sorted(set(M[a][b] for a in range(13) for b in range(13))), [0, 1])

# ---------------------------------------------------------------
# 四、P M P = M 逐格檢（169 格全檢，不只看度數）
# ---------------------------------------------------------------
print("")
print("--- 四、P M P = M 逐格檢 [矩陣層] ---")

bad = []
for a in range(1, 14):
    for b in range(1, 14):
        if M[PAIR[a] - 1][PAIR[b] - 1] != M[a - 1][b - 1]:
            bad.append((a, b))
ok("P M P = M 全 169 格", bad, [])
show("不符格數", len(bad))

# ---------------------------------------------------------------
# 五、F3-對位塊定理：窮舉全部 9 種 [[a,b],[b,a]]
# ---------------------------------------------------------------
print("")
print("--- 五、F3-對位塊定理窮舉 [矩陣層] ---")
print("# 定理：P 不變 2x2 必為 [[a,b],[b,a]]，det = a^2 - b^2。")
print("# 若 a b 皆非零，則在 F3 上必為奇異。")

invertible = []
both_nonzero_singular = True
for a in range(3):
    for b in range(3):
        d = det_mod3([[a, b], [b, a]])
        tag = "invertible" if d != 0 else "SINGULAR"
        print("    a=" + str(a) + " b=" + str(b) +
              "  det=" + str(d) + "  " + tag)
        if d != 0:
            invertible.append((a, b, d))
        if a != 0 and b != 0 and d != 0:
            both_nonzero_singular = False

ok("定理：a b 皆非零 => 必奇異", both_nonzero_singular, True)
ok("P 不變且可逆的 2x2 恰有 4 種", len(invertible), 4)
ok("可逆清單", sorted(invertible),
   sorted([(0, 1, 2), (0, 2, 2), (1, 0, 1), (2, 0, 1)]))
ok("[[2,1],[1,2]] 退化不是筆誤而是必然",
   det_mod3([[2, 1], [1, 2]]), 0)

# ---------------------------------------------------------------
# 六、PUB 五版本對決：det 與 P 不變雙條件
# ---------------------------------------------------------------
print("")
print("--- 六、PUB 五版本對決 [矩陣層] ---")
print("# 序為 (10, 11, 12, 13)。P 在此序下是反轉：10<->13, 11<->12。")
print("# 兩條必須同時成立：det != 0 mod 3  AND  P 不變。")

J4 = [3, 2, 1, 0]


def p_invariant_4(B):
    for a in range(4):
        for b in range(4):
            if B[J4[a]][J4[b]] % 3 != B[a][b] % 3:
                return False
    return True


VERSIONS = [
    ("A_zero", [[2, 0, 1, 0], [0, 0, 0, 0], [1, 0, 2, 1], [0, 1, 0, 1]]),
    ("A_orig", [[2, 0, 1, 0], [0, 2, 0, 1], [1, 0, 2, 1], [0, 1, 1, 2]]),
    ("B", [[1, 1, 0, 0], [1, 2, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]),
    ("C", [[2, 0, 0, 1], [0, 2, 1, 0], [0, 1, 0, 0], [1, 0, 0, 1]]),
    ("J_pair", [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]),
]

verdicts = {}
for (name, B) in VERSIONS:
    d = det_mod3(B)
    pv = p_invariant_4(B)
    zero_row = any(all(x % 3 == 0 for x in row) for row in B)
    verdict = "PASS" if (d != 0 and pv) else "FAIL"
    verdicts[name] = (d, pv, verdict)
    print("    " + name.ljust(8) +
          " det=" + str(d) +
          "  P不變=" + str(pv) +
          "  零行=" + str(zero_row) +
          "  -> " + verdict)

ok("A_zero 含零行 => det = 0", verdicts["A_zero"][0], 0)
ok("A_orig det = 2", verdicts["A_orig"][0], 2)
ok("B det = 2", verdicts["B"][0], 2)
ok("C det = 2", verdicts["C"][0], 2)
ok("J_pair det = 1", verdicts["J_pair"][0], 1)

ok("A_zero 非 P 不變", verdicts["A_zero"][1], False)
ok("A_orig 非 P 不變", verdicts["A_orig"][1], False)
ok("B 非 P 不變", verdicts["B"][1], False)
ok("C 非 P 不變", verdicts["C"][1], False)
ok("J_pair 是 P 不變", verdicts["J_pair"][1], True)

ok("唯一 PASS 版本",
   sorted([k for k in verdicts if verdicts[k][2] == "PASS"]), ["J_pair"])

# 直和用乘法，不用加法
da = det_mod3([[0, 1], [1, 0]])
db = det_mod3([[0, 1], [1, 0]])
ok("兩塊各自 det = 2", (da, db), (2, 2))
ok("det 直和用乘法：2 x 2 = 4 = 1 mod 3", (da * db) % 3, 1)
show("若誤用加法會得 [錯路徑]", (da + db) % 3)
print("# 上行展示加法為何危險：此例加法得 1、乘法也得 1，差別被掩蔽。")
show("反例 det=1 與 det=2：加法 [錯]", (1 + 2) % 3)
show("反例 det=1 與 det=2：乘法 [正]", (1 * 2) % 3)
print("# 加法得 0 會誤判 FAIL，乘法得 2 才是真 PASS。")

# ---------------------------------------------------------------
# 七、核塊行和實算（揭示「中樞行恆 5」不成立）
# ---------------------------------------------------------------
print("")
print("--- 七、行和實算 [矩陣層] ---")

core_row_sums = [sum(M[i][j] for j in range(9)) for i in range(9)]
full_row_sums = [sum(M[i][j] for j in range(13)) for i in range(13)]
show("核塊行和 1..9 [矩陣層]", core_row_sums)
show("全行和 1..13 [矩陣層]", full_row_sums)

ok("row5 核塊和 = 8（不是 5，也不是 10）", core_row_sums[4], 8)
print("# 重要：5 是索引、是不動點編號，不是任何行和。")
print("# 舊矩陣 row5 核塊和為 10（含對角 2），本版對角歸零故為 8。")
print("# 兩者都不等於 5。core_sum = 10 只在索引層成立。")

ok("對位全行和守恆（row_i = row_P(i)）",
   all(full_row_sums[i - 1] == full_row_sums[PAIR[i] - 1]
       for i in range(1, 14)), True)
print("# 這一條舊版 FAIL（row1+row9 = 11），本版因 P 不變而自動成立。")

# ---------------------------------------------------------------
# 八、塊對角性：揭示 PUB ∩ Core = ∅ 只在索引層成立
# ---------------------------------------------------------------
print("")
print("--- 八、塊對角性檢查 ---")

cross = [(i, j) for i in range(1, 10) for j in range(10, 14)
         if M[i - 1][j - 1] != 0]
ok("索引層：Core 交 PUB = 空集",
   sorted(set(range(1, 10)) & set(range(10, 14))), [])
show("矩陣層：Core-PUB 非零耦合數", len(cross))
ok("M 非塊對角（故矩陣層不分離）", len(cross) > 0, True)
print("# 結語：PUB 交 Core = 空集 僅在索引層成立且屬平側。")
print("# 矩陣層 M 並非塊對角，不得以前者主張後者。")

# 檢 Core-PUB 耦合在 P 下對稱
cross_img = sorted(set((PAIR[i], PAIR[j]) for (i, j) in cross))
ok("Core-PUB 耦合在 P 下對稱", cross_img, sorted(set(cross)))

# ---------------------------------------------------------------
# 九、pub_det 與 full_det
# ---------------------------------------------------------------
print("")
print("--- 九、pub_det 與 full_det ---")

PUB_sub = [[M[i][j] for j in range(9, 13)] for i in range(9, 13)]
pub_det = det_mod3(PUB_sub)
show("PUB 子矩陣（行列 10..13）", PUB_sub)
ok("pub_det = 1 mod 3", pub_det, 1)

full_det = det_mod3(M)
print("")
print("    ############################################################")
print("    #  P-10 = UNKNOWN。以下數值不 assert。")
print("    #  建庫者未手算 13x13 F3 行列式，也未宣稱任何值。")
print("    #  本行印出即首次機器測定。請將此行貼回入庫。")
print("    ############################################################")
print("    full_det mod 3 = " + str(full_det))
print("    ############################################################")
print("")

if full_det == 0:
    print("[INFO] full_det = 0 => M 不屬 GL(13,F3)。第一條合法棲息 FAIL。")
    print("[INFO] 等價於：1 是鄰接矩陣在 F3 上的特徵值。需重布線。")
else:
    print("[INFO] full_det != 0 => M 屬 GL(13,F3)。第一條合法棲息 PASS。")

skip("三條合法棲息綜合判定",
     "需 full_det 實測值入庫後才能結案，本脅本不代替裁示")

# ---------------------------------------------------------------
# 十、不驗的部分，明文列出
# ---------------------------------------------------------------
print("")
print("--- 十、本脅本不驗的部分 ---")

skip("矩陣對應麥田圈圖形",
     "本 session 從未收到任何圖像，無圖形到 1..13 的映射函式。SYMBOLIC")
skip("eta = pi / sqrt(18) 為本系統上界",
     "無 13 維 F3 線性代數到三維球堆積的橋。二維六角是 pi/sqrt(12)。OPEN")
skip("∮ zeta Q M dr = 0",
     "路徑、測度、zeta 與 M 的乘法皆未定義。SYMBOLIC")
skip("checksum_f3 防偽能力",
     "模算校驗和不是簽章。Ed25519 金鑰對尚未產生，公鑰未入庫。")
skip("C0_value 型別",
     "5 不屬於 F3 = {0,1,2}，且不是 9 維向量。待拆為 C0_index 與 C0_residue")

ok("5 mod 3 = 2 [F3 層]", 5 % 3, 2)
ok("5 mod 5 = 0 [標籤層]", 5 % 5, 0)
ok("10 mod 3 = 1 [F3 層]", 10 % 3, 1)
print("# mod 3 與 mod 5 不得互證。使用者自訂禁令，已升為 canonical。")

# ---------------------------------------------------------------
print("")
print("=" * 66)
print("PASS=" + str(PASSES) + "  FAIL=" + str(len(FAILS)) + "  SKIP=" + str(SKIPS))
if FAILS:
    print("FAILED:")
    for f in FAILS:
        print("  - " + f)
print("本脅本只證明上列斷言。它不證明麥田圈、不證明物理、不證明意義。")
print("=" * 66)

sys.exit(1 if FAILS else 0)
