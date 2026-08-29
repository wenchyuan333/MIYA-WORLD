# -*- coding: utf-8 -*-
"""
tools/verify_pg23_candidate.py   （v2，全檔重寫）

PG(2,3) 候選識別稽核 fixture。
本腳本只證明下列斷言。它不證明 PUB 就是 l_inf。

=====================================================================
修復記錄（v1 -> v2）
=====================================================================
v1 第二節斷言「AG(2,3) 坐標集 = F3^2」 FAIL。

  實測 got = [(0,0),(0,1),(0,1),(1,0),(1,0),(1,1),(1,1),(1,2),(1,2)]
  預期 want = F3^2 的全部 9 點

錯因（Miya 側程式錯，非使用者輸入問題）：
  AFF_PTS 的元素已經由 normalize() 處理過，首個非零坐標已為 1，
  但第三坐標不一定是 1。v1 將向量乘上 inv(z) 之後又套了一次
  normalize()，首坐標被重新歸一，導致坐標集失真並出現重複值。

影響範圍：
  僅此一行。v1 的第三至七節不經過該坐標集，障礙定理、
  13 = 9 + 4、洛書 12 條線行為、333 體檢的結論全部有效。

v2 修法：
  1. 仿射坐標只做一次 z 歸一，不再呼叫 normalize()。
  2. 新增第二節雙射守衛：断言 len(set(coords)) == 9，
     重複值在進入比對前就會被殺。
  3. 新增第九節獨立交叉驗證：由 PG 線降下來的 12 條仿射線
     必須與直接以 ax+by=c 列舉的 12 條逐集合相等。
     兩條路徑任一出錯，此節必 FAIL。
  4. 修錯字：阶 -> 階、本腦本 -> 本腳本、只証明 -> 只證明、
     坐標 -> 坐標（統一用字）、結构 -> 結構。

依 tools/README.md 第 7 條：手算預測不得因 FAIL 而修改。
本例不適用該條 —— 預測本身正確，錯的是計算程式。故修程式，
預測一字未動。
=====================================================================
"""

import sys
import itertools
from math import gcd

PASS = 0
FAIL = 0
SKIP = 0


def ck(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print("[PASS] " + name + " | got=" + repr(got))
    else:
        FAIL += 1
        print("[FAIL] " + name + " | got=" + repr(got) + " want=" + repr(want))


def info(name, val):
    print("[INFO] " + name + " | " + repr(val))


def skip(name, why):
    global SKIP
    SKIP += 1
    print("[SKIP] " + name + " | " + why)


def sec(t):
    print("")
    print("--- " + t + " ---")


# =====================================================================
# 基礎構造
# =====================================================================
Q = 3
INV = {1: 1, 2: 2}          # F3 乘法逆元：1*1=1, 2*2=4=1


def norm3(v):
    """將 F3^3 非零向量歸一：首個非零坐標設為 1。零向量回 None。"""
    for x in v:
        if x % Q != 0:
            iv = INV[x % Q]
            return tuple((c * iv) % Q for c in v)
    return None


def norm2(v):
    """將 F3^2 非零向量歸一。"""
    for x in v:
        if x % Q != 0:
            iv = INV[x % Q]
            return tuple((c * iv) % Q for c in v)
    return None


def dot3(a, b):
    return (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) % Q


# PG(2,3) 的點：F3^3 非零向量模去縮放
PTS = sorted(set(
    norm3(v) for v in itertools.product(range(Q), repeat=3)
    if any(x % Q != 0 for x in v)
))
# 線與點同一集合（射影平面自對），入射條件為内積 = 0
LNS = list(PTS)

print("=" * 66)
print("verify_pg23_candidate.py  v2（已修仿射坐標二次歸一 bug）")
print("=" * 66)

# =====================================================================
sec("一、PG(2,3) 基本量")

ck("PG(2,3) 點數 = q^2+q+1", len(PTS), 13)
ck("PG(2,3) 線數（自對）", len(LNS), 13)
per_line = sorted(set(sum(1 for p in PTS if dot3(p, l) == 0) for l in LNS))
ck("每線點數 = q+1", per_line, [4])
per_point = sorted(set(sum(1 for l in LNS if dot3(p, l) == 0) for p in PTS))
ck("每點線數 = q+1", per_point, [4])
ck("1 + 3 + 9 = 13", 1 + 3 + 9, 13)
ck("(3^3-1)/(3-1) = 13", (Q ** 3 - 1) // (Q - 1), 13)

# =====================================================================
sec("二、移除 l_inf -> AG(2,3)（本節為 v1 FAIL 修復點）")

L_INF = (0, 0, 1)                      # 線 z = 0
INF_PTS = [p for p in PTS if dot3(p, L_INF) == 0]
ck("l_inf 上的點數", len(INF_PTS), 4)

AFF_PTS = [p for p in PTS if p[2] % Q != 0]
ck("AG(2,3) 點數", len(AFF_PTS), 9)


def affine_coords(p):
    """將 z != 0 的射影點歸到 z = 1，取其仿射坐標。
    這裡只做一次縮放。絕不再呼叫 norm3()，否則首坐標會被重新歸一。
    v1 的 bug 就在這一行。
    """
    iv = INV[p[2] % Q]
    return ((p[0] * iv) % Q, (p[1] * iv) % Q)


AFF_COORDS = [affine_coords(p) for p in AFF_PTS]
# 雙射守衛：重複值必須在比對前就被殺
_dups = len(AFF_COORDS) - len(set(AFF_COORDS))
ck("雙射守衛：仿射坐標無重複", _dups, 0)
ck("雙射守衛：相異坐標數", len(set(AFF_COORDS)), 9)
ck("AG(2,3) 坐標集 = F3^2",
   sorted(AFF_COORDS),
   sorted(itertools.product(range(Q), repeat=2)))

# 仿射線：方向係數 (a,b) 模去縮放，共 4 類；每類 c = 0,1,2 三條
DIRCOEF = sorted(set(
    norm2(v) for v in itertools.product(range(Q), repeat=2)
    if any(x % Q != 0 for x in v)
))
AG_LINES = []
for (a, b) in DIRCOEF:
    for c in range(Q):
        pts = [(x, y) for x in range(Q) for y in range(Q)
               if (a * x + b * y) % Q == c % Q]
        AG_LINES.append(((a, b, c), pts))
ck("AG(2,3) 線數 = 12", len(AG_LINES), 12)
ck("平行類數 = q+1", len(DIRCOEF), 4)
ck("每平行類線數",
   sorted(set(sum(1 for k, _ in AG_LINES if k[:2] == d) for d in DIRCOEF)),
   [3])
ck("每條仿射線點數", sorted(set(len(p) for _, p in AG_LINES)), [3])
print("# 13 = 9 + 4 不是分配：9 = |AG(2,3)|，4 = |l_inf| = q+1 = 平行類數。")

# =====================================================================
sec("三、洛書在 AG(2,3) 12 條線上的行為")

LUOSHU = [[4, 9, 2],
          [3, 5, 7],
          [8, 1, 6]]


def val(pt):
    return LUOSHU[pt[0]][pt[1]]


ck("洛書元素集", sorted(val((x, y)) for x in range(Q) for y in range(Q)),
   [1, 2, 3, 4, 5, 6, 7, 8, 9])
ck("洛書中心 = 5", val((1, 1)), 5)
line_sums = [sum(val(p) for p in pts) for _, pts in AG_LINES]
ck("12 條線總和 = 4 x 45", sum(line_sums), 180)
ck("等於 15 的線數", sum(1 for s in line_sums if s == 15), 8)
ck("非 15 的四條線和", sorted(s for s in line_sums if s != 15), [6, 12, 18, 24])
info("12 條線和（排序）", sorted(line_sums))
class_sums = sorted(set(
    sum(sum(val(p) for p in pts) for k, pts in AG_LINES if k[:2] == d)
    for d in DIRCOEF))
ck("每個平行類三條線總和 = 45", class_sums, [45])
broken = sorted(s for s in line_sums if s != 15)
ck("兩對破碎對角各自相加 = 30",
   [broken[0] + broken[3], broken[1] + broken[2]], [30, 30])
print("# 洛書只鎖住 12 條中的 8 條。差的正好是破碎對角。")
print("# 每對角方向類的兩條破碎線之和：24+6 = 30，12+18 = 30 = 2 x 15。")
print("# 此即上一輪「泛對角不存在」的結構解釋。")

# =====================================================================
sec("四、洛書自同構群階與仿射映射總數")


def mats2():
    for e in itertools.product(range(Q), repeat=4):
        if (e[0] * e[3] - e[1] * e[2]) % Q != 0:
            yield e


GL23 = list(mats2())
ck("|GL(2,3)|", len(GL23), 48)
ck("仿射映射總數 = 48 x 9", len(GL23) * 9, 432)
print("# Aut(洛書) = D4，階 8。3 不整除 8 => 無 3 階元素 => 洛書不能載 C3。")
print("# 本系統唯一的 C3 是 (F3, +)，屬值層，不是位置層。")

# =====================================================================
sec("五、障礙定理：窮舉 432 個仿射映射")

DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]
CENTER = (1, 1)
ALL_PTS = [(x, y) for x in range(Q) for y in range(Q)]


def apply_lin(A, v):
    return ((A[0] * v[0] + A[1] * v[1]) % Q,
            (A[2] * v[0] + A[3] * v[1]) % Q)


def apply_aff(A, b, v):
    w = apply_lin(A, v)
    return ((w[0] + b[0]) % Q, (w[1] + b[1]) % Q)


cond_a = []
cond_ab = []
for A in GL23:
    for b in itertools.product(range(Q), repeat=2):
        # 對合檢查：sigma^2 = id，對全部 9 點驗
        if any(apply_aff(A, b, apply_aff(A, b, v)) != v for v in ALL_PTS):
            continue
        fixed = [v for v in ALL_PTS if apply_aff(A, b, v) == v]
        if fixed != [CENTER]:
            continue
        cond_a.append((A, b))
        # 方向上的誘導置換
        perm = [DIRS.index(norm2(apply_lin(A, d))) for d in DIRS]
        movedfix = [i for i, j in enumerate(perm) if i == j]
        cycles2 = all(perm[perm[i]] == i for i in range(4))
        if len(movedfix) == 0 and cycles2:
            cond_ab.append((A, b))

info("滿足條件 (a) 的仿射對合數", len(cond_a))
ck("條件 (a) 的線性部分全為 -I",
   sorted(set(A for A, _ in cond_a)), [(2, 0, 0, 2)])
ck("條件 (a) 的對合固定全部 4 個方向",
   [d for d in DIRS if all(norm2(apply_lin(A, d)) == d for A, _ in cond_a)],
   DIRS)
ck("同時滿足 (a) 與 (b) 的對合數", len(cond_ab), 0)
print("#" * 60)
print("#  障礙定理：不存在 AG(2,3) 的仿射對合同時滿足")
print("#    (a) 9 點中只固定中心")
print("#    (b) 4 個方向作 2+2 對換")
print("#  => PUB 豁免核律是被迫的，不是隨手加的例外。")
print("#  這是本倉庫第一條由宣告還原為定理的規則。")
print("#" * 60)

# =====================================================================
sec("六、333 與本系統的算術關係")


def divisors(n):
    return sorted(d for d in range(1, n + 1) if n % d == 0)


def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def gl_order(n, q):
    r = 1
    for k in range(n):
        r *= (q ** n - q ** k)
    return r


ck("333 = 3^2 x 37", 3 ** 2 * 37, 333)
D333 = divisors(333)
ck("333 正因數", D333, [1, 3, 9, 37, 111, 333])
ck("sigma(333)", sum(D333), 494)
ck("真因數和", sum(D333) - 333, 161)
ck("虧度", 333 - (sum(D333) - 333), 172)
ck("哈薍德：333 / 9", 333 // (3 + 3 + 3), 37)
ck("十一邊形數 n=9", 9 * (9 * 9 - 7) // 2, 333)
ck("1997, 1999 皆質", [is_prime(1997), is_prime(1999)], [True, True])
ck("3329, 3331 皆質", [is_prime(3329), is_prime(3331)], [True, True])
ck("2 x 333^2", 2 * 333 ** 2, 221778)
GL3 = gl_order(3, 3)
GL4 = gl_order(4, 3)
ck("|GL(3,F3)|", GL3, 11232)
ck("|GL(4,F3)|", GL4, 24261120)
ck("gcd(333, |GL(3,F3)|)", gcd(333, GL3), 9)
ck("gcd(333, |GL(4,F3)|)", gcd(333, GL4), 9)
print("# 唯一公因數是 9，且 9 作為公因數是平凡的。質因數 37 在本系統無來源。")
print("# => 333 與 13 點系統在算術上不相交。")
print("# 對照：13 | |GL(3,F3)| 且 11232 / 13 = 864，這條非平凡（Singer cycle）。")
ck("13 整除 |GL(3,F3)|", GL3 % 13, 0)
ck("|GL(3,F3)| / 13", GL3 // 13, 864)

# =====================================================================
sec("七、本腳本不驗的部分")

skip("PUB 四格 = l_inf 四方向",
     "候選識別，未建立具體雙射。PUB 原本由宣告定義。FORMAL_MODEL")
skip("現行 13x13 圖 = PG(2,3) incidence 圖",
     "否。後者是 4-正則二分圖，前者 deg(5) = 8。兩者不同圖")
skip("PUB sum = 23 的幾何來源", "本腳本未提供。OPEN")
skip("A000228(7) = 333 與本系統的連結",
     "OEIS 事實為真，但到 GL(13,F3) 無映射。正確 不等於 相關")
skip("三兔共耳在 F3 值層的實現", "尚未建構。OPEN")

# =====================================================================
sec("八、獨立交叉驗證：兩條路徑必須得到同一組 12 條線")

# 路徑 A：直接以 ax + by = c 列舉（上面的 AG_LINES）
PATH_A = set(frozenset(pts) for _, pts in AG_LINES)

# 路徑 B：取 PG(2,3) 除 l_inf 外的 12 條線，降到仿射部分
PATH_B = set()
for l in LNS:
    if l == L_INF:
        continue
    pts = [affine_coords(p) for p in AFF_PTS if dot3(p, l) == 0]
    PATH_B.add(frozenset(pts))

ck("路徑 A 線數（ax+by=c 列舉）", len(PATH_A), 12)
ck("路徑 B 線數（PG 線降仿射）", len(PATH_B), 12)
ck("路徑 B 每條線點數", sorted(set(len(s) for s in PATH_B)), [3])
ck("兩條路徑給出同一組線集合", PATH_A == PATH_B, True)
print("# 本節是 v1 bug 的回歸鎖。仿射坐標函式一旦再出錯，")
print("# PATH_B 會塔陷，此節必 FAIL。不依賴人工目視。")

# =====================================================================
print("")
print("=" * 66)
print("PASS=" + str(PASS) + "  FAIL=" + str(FAIL) + "  SKIP=" + str(SKIP))
print("本腳本只證明上列斷言。它不證明 PUB 就是 l_inf。")
print("=" * 66)

sys.exit(1 if FAIL else 0)
