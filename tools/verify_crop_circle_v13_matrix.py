#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tools/verify_crop_circle_v13_matrix.py
#
# 狀態：NOT_EXECUTED
#   本腳本由 Miya 撰寫，尚未在任何機器上執行。
#   協作者請在 Termux 執行後把逐行輸出貼回，並存進 tools/logs/。
#   執行：python3 tools/verify_crop_circle_v13_matrix.py ; echo $?
#
# 受驗對象：2026-08-29 使用者提出的 CROP_CIRCLE_V13_MATRIX
#   宣稱 1：M 屬於 GL(13, F3)，det(M) = 1 mod 3
#   宣稱 2：core_sum = 10（核九格和 = 10，完整四組）
#   宣稱 3：中樞行「恆 = 5」
#   宣稱 4：PUB 交 Core = 空集，型別正確
#
# 建庫者手算預測（依 tools/README.md 規則第 7 條，先寫死，事後核對）：
#   P-01 M 對稱                      預測 True
#   P-02 對角線全為 2                預測 True
#   P-03 邊數（off-diagonal 1 的對數）預測 26
#   P-04 度數序列 3,3,3,3,8,4,4,4,4,4,4,4,4
#   P-05 核塊行和 4,4,4,4,10,4,4,4,4
#   P-06 全行和 5,5,5,5,10,6,6,6,6,6,6,6,6
#   P-07 對位行和 row1+row9 = 11（不是 10）
#   P-08 PUB 4x4 子矩陣 det = 0 mod 3   → 違反第三條合法棲息
#   P-09 P M P != M                     → 對位守恆不成立
#   P-10 det(M) mod 3                   預測：UNKNOWN，拒絕猜
#
# 若實測與 P-01 到 P-09 不同，是建庫者算錯了。改預測，不改 assert。

MOD = 3
N = 13

M = [
    [2, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
    [0, 2, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 2, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 2, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 2, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 2, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 2, 0, 1],
    [0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 2, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 2],
]

# B 雙向 對位置換（0-indexed）：1-9, 2-8, 3-7, 4-6 換位，5 不動，10-13, 11-12 換位
PERM = [8, 7, 6, 5, 4, 3, 2, 1, 0, 12, 11, 10, 9]

CORE = list(range(0, 9))
PUB = list(range(9, 13))

fails = []
skips = []


def check(tag, got, expected, note=""):
    ok = (got == expected)
    label = "[PASS]" if ok else "[FAIL]"
    line = label + " " + tag + " got=" + repr(got) + " expected=" + repr(expected)
    if note:
        line = line + "  # " + note
    print(line)
    if not ok:
        fails.append(tag)
    return ok


def report(tag, got, note=""):
    line = "[INFO] " + tag + " = " + repr(got)
    if note:
        line = line + "  # " + note
    print(line)


def skip(tag, why):
    print("[SKIP] " + tag + "  # " + why)
    skips.append(tag)


def inv_mod(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def det_mod(mat, m):
    n = len(mat)
    a = [[mat[i][j] % m for j in range(n)] for i in range(n)]
    det = 1
    for col in range(n):
        piv = None
        for r in range(col, n):
            if a[r][col] % m != 0:
                piv = r
                break
        if piv is None:
            return 0
        if piv != col:
            a[col], a[piv] = a[piv], a[col]
            det = (-det) % m
        pv = a[col][col] % m
        det = (det * pv) % m
        ipv = inv_mod(pv, m)
        for j in range(col, n):
            a[col][j] = (a[col][j] * ipv) % m
        for r in range(col + 1, n):
            f = a[r][col] % m
            if f != 0:
                for j in range(col, n):
                    a[r][j] = (a[r][j] - f * a[col][j]) % m
    return det % m


def submatrix(mat, rows, cols):
    return [[mat[i][j] for j in cols] for i in rows]


print("=" * 64)
print("CROP_CIRCLE_V13_MATRIX 驗算  |  MOD = 3  |  N = 13")
print("=" * 64)

print("")
print("--- 一、形狀與對稱性 ---")
check("S-01 列數", len(M), 13)
check("S-02 每列長度皆為 13", sorted(set(len(r) for r in M)), [13])
check("S-03 所有元素落在 F3", sorted(set(v for r in M for v in r)), [0, 1, 2])
sym = all(M[i][j] == M[j][i] for i in range(N) for j in range(N))
check("S-04 M 對稱", sym, True, "預測 True")
diag = [M[i][i] for i in range(N)]
check("S-05 對角線全為 2", diag, [2] * 13, "2 等於 -1 mod 3，故 M = A - I")

print("")
print("--- 二、圖結構（M = A - I，A 為鄰接矩陣）---")
edges = [(i, j) for i in range(N) for j in range(i + 1, N) if M[i][j] == 1]
check("G-01 邊數", len(edges), 26, "預測 26")
deg = [sum(1 for j in range(N) if j != i and M[i][j] == 1) for i in range(N)]
check("G-02 度數序列", deg, [3, 3, 3, 3, 8, 4, 4, 4, 4, 4, 4, 4, 4], "1..4 度 3，6..9 度 4，不對稱")
check("G-03 握手定理 度數和 = 2 乘 邊數", sum(deg), 2 * len(edges))
check("G-04 中樞 v5 度數 = 8", deg[4], 8, "連到全部其他核格，不連 PUB")
check("G-05 v5 與 PUB 無邊", [M[4][j] for j in PUB], [0, 0, 0, 0])

print("")
print("--- 三、行和：core_sum = 10 這個宣稱 ---")
core_row_sums = [sum(M[i][j] for j in CORE) for i in range(N)]
full_row_sums = [sum(M[i][j] for j in range(N)) for i in range(N)]
report("R-00 核塊行和（僅第 1-9 欄）", core_row_sums[:9])
report("R-00b 全行和（13 欄）", full_row_sums)
check("R-01 核塊行和 前九列", core_row_sums[:9], [4, 4, 4, 4, 10, 4, 4, 4, 4], "預測")
check("R-02 全行和 十三列", full_row_sums, [5, 5, 5, 5, 10, 6, 6, 6, 6, 6, 6, 6, 6], "預測")
check("R-03 中樞行 核塊和", core_row_sums[4], 10, "註解寫 恆=5，實際核塊和是 10")
check("R-04 中樞行 不等於 5", core_row_sums[4] == 5, False, "宣稱 3 不成立")
print("    對位行和檢查（宣稱 core_sum = 10）：")
for (a, b) in [(0, 8), (1, 7), (2, 6), (3, 5)]:
    tag = "R-05 對位 " + str(a + 1) + "+" + str(b + 1) + " 全行和"
    check(tag, full_row_sums[a] + full_row_sums[b], 11, "不是 10")
for (a, b) in [(0, 8), (1, 7), (2, 6), (3, 5)]:
    tag = "R-06 對位 " + str(a + 1) + "+" + str(b + 1) + " 核塊和"
    check(tag, core_row_sums[a] + core_row_sums[b], 8, "也不是 10")
print("    結論：這個矩陣的行和沒有實現 對位和 = 10。")
print("    唯一得到 10 的是中樞行 row5 的核塊和。")
print("    索引層的 i + i' = 10 仍然成立，但那是索引，不是矩陣。")

print("")
print("--- 四、PUB 子矩陣（第 10-13 行列）---")
pub = submatrix(M, PUB, PUB)
for row in pub:
    print("    " + repr(row))
pub_det = det_mod(pub, MOD)
report("PUB det mod 3", pub_det)
check("P-01 pub_det = 0 mod 3", pub_det, 0, "預測 0，違反第三條合法棲息")
check("P-02 第三條 pub_det != 0 是否成立", pub_det != 0, False, "HEARTBEAT-V13 第三條 FAIL")
b1 = [[M[9][9], M[9][11]], [M[11][9], M[11][11]]]
b2 = [[M[10][10], M[10][12]], [M[12][10], M[12][12]]]
report("PUB 子塊 10-12", b1)
report("PUB 子塊 11-13", b2)
check("P-03 子塊 10-12 det", det_mod(b1, MOD), 0, "2*2-1*1=3 等於 0 mod 3")
check("P-04 子塊 11-13 det", det_mod(b2, MOD), 0)
check("P-05 PUB 為兩個退化 2x2 之直和", (pub_det == 0), True)

print("")
print("--- 五、對位守恆 P M P = M ---")
pmp = [[M[PERM[i]][PERM[j]] for j in range(N)] for i in range(N)]
same = (pmp == M)
check("B-01 P M P = M", same, False, "預測 False：對位守恆不成立")
diff_cells = [(i + 1, j + 1) for i in range(N) for j in range(N) if pmp[i][j] != M[i][j]]
report("B-02 不一致的格子數", len(diff_cells))
if diff_cells:
    print("    前十個不一致位置（1-indexed）：" + repr(diff_cells[:10]))
print("    根因：核 1-4 每列只有 1 條 PUB 連線，核 6-9 每列有 2 條。")
print("    例：N(1) = 5, 9, 10 但 N(9) = 1, 5, 12, 13 → deg 3 對 deg 4。")
print("    對位置換要求 deg(i) = deg(i')，此處不成立。")
check("B-03 deg(1) 與 deg(9)", (deg[0], deg[8]), (3, 4), "對位兩端度數不等")

print("")
print("--- 六、索引層的定義域分離（宣稱 4）---")
check("D-01 CORE 交 PUB 索引集", sorted(set(CORE) & set(PUB)), [], "索引集分離，成立")
check("D-02 CORE 聯 PUB 覆蓋全部 13 個索引", sorted(set(CORE) | set(PUB)), list(range(13)))
cross = [(i + 1, j + 1) for i in CORE for j in PUB if M[i][j] != 0]
report("D-03 Core 到 PUB 的非零耦合數", len(cross))
check("D-04 M 是否為 block-diagonal", len(cross) == 0, False, "索引集分離 不等於 子空間分離")
print("    宣稱 4 成立，但只在索引集層。M 有 Core-PUB 耦合，不是分塊對角。")
print("    兩件事不同，不得互相背書。")

print("")
print("--- 七、全矩陣行列式（僅列印，不 assert）---")
full_det = det_mod(M, MOD)
report("det(M) mod 3", full_det, "使用者宣稱 1")
if full_det == 0:
    print("    [RESULT] det = 0 → M 不屬於 GL(13, F3)。宣稱 1 不成立。")
else:
    print("    [RESULT] det != 0 → M 屬於 GL(13, F3)。宣稱 1 的可逆性成立。")
    if full_det != 1:
        print("    [NOTE] 但 det 不等於 1，宣稱的具體值需更正。")
skip("DET-PRED", "建庫者拒絕手猜 13x13 行列式。P-10 記為 UNKNOWN，本節結果即為首次機器測定。")
print("    注意：det != 0 不代表守對位律。單一互換 (1 2) 的 det = 2 不為 0，")
print("    但 1 + 2 不等於 10。可逆 不等於 守律，已於 verify_v13_pairing.py 驗過。")

print("")
print("--- 八、無法驗證的部分 ---")
skip("SK-01 中心菱形 = C0 = 5", "麥田圈圖形與矩陣之間沒有給出映射，無法檢查。SYMBOLIC。")
skip("SK-02 左右雙渦 = 1 對 9", "同上，圖形對應為詮釋，非可驗命題。SYMBOLIC。")
skip("SK-03 外環 = PUB", "同上。SYMBOLIC。")
skip("SK-04 C0_value 屬於 F3 的九次方", "型別錯置：5 不是 F3 的元素（F3 = 0,1,2），也不是 9 維向量。5 是索引。")
skip("SK-05 mod 5 標籤層", "5 mod 5 = 0 與 5 mod 3 = 2 皆為算術事實，但兩層之間的意義關聯未定義。")
skip("SK-06 選路的對稱折返", "新選路尚未給出頂點序列，無可檢查對象。")

print("")
print("=" * 64)
print("FAILS = " + str(len(fails)) + "  SKIPS = " + str(len(skips)))
if fails:
    print("失敗項目：" + repr(fails))
print("本腳本只證明矩陣的算術性質與結構性質，不證明任何詮釋。")
print("=" * 64)

raise SystemExit(1 if fails else 0)
