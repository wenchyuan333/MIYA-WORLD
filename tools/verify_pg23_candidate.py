# -*- coding: utf-8 -*-
# verify_pg23_candidate.py
# 驗証 PG(2,3) 候選識別與障礙定理
# 本腦本只証下列斷言。它不証明 PUB 就是 l_inf。
# 狀態：NOT_EXECUTED

import sys
import itertools

PASSES = 0
FAILS = 0
SKIPS = 0


def ok(name, got):
    global PASSES
    PASSES += 1
    print("[PASS] " + name + " | got=" + repr(got))


def bad(name, got, want):
    global FAILS
    FAILS += 1
    print("[FAIL] " + name + " | got=" + repr(got) + " want=" + repr(want))


def check(name, got, want):
    if got == want:
        ok(name, got)
    else:
        bad(name, got, want)


def info(name, got):
    print("[INFO] " + name + " | " + repr(got))


def skip(name, why):
    global SKIPS
    SKIPS += 1
    print("[SKIP] " + name + " | " + why)


INV3 = {1: 1, 2: 2}


def normalize(v):
    for c in v:
        if c % 3 != 0:
            m = INV3[c % 3]
            return tuple((x * m) % 3 for x in v)
    return None


def dot3(a, b):
    return sum(x * y for x, y in zip(a, b)) % 3


print("=" * 66)
print("verify_pg23_candidate.py")
print("=" * 66)

print("")
print("--- 一、PG(2,3) 基本量 ---")

PTS = sorted({normalize(v) for v in itertools.product(range(3), repeat=3)
              if normalize(v) is not None})
check("PG(2,3) 點數 = q^2+q+1", len(PTS), 13)

LNS = list(PTS)
check("PG(2,3) 線數（自對）", len(LNS), 13)

per_line = {len([p for p in PTS if dot3(p, L) == 0]) for L in LNS}
check("每線點數 = q+1", sorted(per_line), [4])

per_point = {len([L for L in LNS if dot3(p, L) == 0]) for p in PTS}
check("每點線數 = q+1", sorted(per_point), [4])

check("1 + 3 + 9 = 13", 1 + 3 + 9, 13)
check("(3^3-1)/(3-1) = 13", (27 - 1) // 2, 13)

print("")
print("--- 二、移除 l_inf -> AG(2,3) ---")

LINF = (0, 0, 1)
INF_PTS = [p for p in PTS if dot3(p, LINF) == 0]
check("l_inf 上的點數", len(INF_PTS), 4)

AFF_PTS = [p for p in PTS if dot3(p, LINF) != 0]
check("AG(2,3) 點數", len(AFF_PTS), 9)

AFF = sorted((p[0] % 3, p[1] % 3) for p in
             [normalize((p[0] * INV3[p[2] % 3], p[1] * INV3[p[2] % 3], 1))
              for p in AFF_PTS])
check("AG(2,3) 坐標集 = F3^2", AFF,
      sorted(itertools.product(range(3), repeat=2)))

AFF_LINES = [L for L in LNS if L != LINF]
check("AG(2,3) 線數 = 12", len(AFF_LINES), 12)

# 每條仿射線與 l_inf 交於唯一點，該點標記其平行類
classes = {}
for L in AFF_LINES:
    meet = [p for p in INF_PTS if dot3(p, L) == 0]
    if len(meet) != 1:
        bad("仿射線與 l_inf 交點數", len(meet), 1)
    else:
        classes.setdefault(meet[0], []).append(L)
check("平行類數 = q+1", len(classes), 4)
check("每平行類線數", sorted({len(v) for v in classes.values()}), [3])
print("# 13 = 9 + 4 不是分配：9 = |AG(2,3)|，4 = |l_inf| = q+1 = 平行類數。")

print("")
print("--- 三、洛書在 AG(2,3) 12 條線上的行為 ---")

L_SHU = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
check("洛書元素集", sorted(x for r in L_SHU for x in r), list(range(1, 10)))


def aff_line_cells(L):
    out = []
    for i in range(3):
        for j in range(3):
            if dot3((i, j, 1), L) == 0:
                out.append((i, j))
    return out


sums = []
for L in AFF_LINES:
    cells = aff_line_cells(L)
    if len(cells) != 3:
        bad("仿射線格數", len(cells), 3)
    sums.append(sum(L_SHU[i][j] for i, j in cells))

sums_sorted = sorted(sums)
check("12 條線總和 = 4 x 45", sum(sums), 180)
check("等於 15 的線數", sums.count(15), 8)
non15 = sorted(s for s in sums if s != 15)
check("非 15 的四條線和", non15, [6, 12, 18, 24])
info("12 條線和（排序）", sums_sorted)

for pt, lines in classes.items():
    cls_sum = sum(sum(L_SHU[i][j] for i, j in aff_line_cells(L)) for L in lines)
    if cls_sum != 45:
        bad("平行類總和", cls_sum, 45)
ok("每個平行類三條線總和 = 45", 45)
print("# 洛書只鎖住 12 條中的 8 條。差的正好是破碎對角。")
print("# 每對角方向類的兩條破碎線之和：24+6 = 30，12+18 = 30 = 2 x 15。")
print("# 此即上一輪「泛對角不存在」的結構解釋。")

print("")
print("--- 四、洛書自同構群阶 ---")


def gl2_elements():
    out = []
    for a, b, c, d in itertools.product(range(3), repeat=4):
        if (a * d - b * c) % 3 != 0:
            out.append((a, b, c, d))
    return out


GL2 = gl2_elements()
check("|GL(2,3)|", len(GL2), 48)
check("仿射映射總數 = 48 x 9", len(GL2) * 9, 432)
print("# Aut(洛書) = D4，阶 8。3 不整除 8 => 無 3 阶元素 => 洛書不能載 C3。")
print("# 本系統唯一的 C3 是 (F3, +)，屬值層，不是位置層。")

print("")
print("--- 五、障礙定理：窮舉 432 個仿射映射 ---")

DIRS = [(1, 0), (0, 1), (1, 1), (1, 2)]


def norm_dir(v):
    if v[0] % 3 != 0:
        m = INV3[v[0] % 3]
        return ((v[0] * m) % 3, (v[1] * m) % 3)
    if v[1] % 3 != 0:
        return (0, 1)
    return None


def apply_A(A, v):
    a, b, c, d = A
    return ((a * v[0] + b * v[1]) % 3, (c * v[0] + d * v[1]) % 3)


CENTER = (1, 1)

cond_a_maps = []
both_maps = []
for A in GL2:
    for bx, by in itertools.product(range(3), repeat=2):
        b = (bx, by)

        def sig(x, A=A, b=b):
            y = apply_A(A, x)
            return ((y[0] + b[0]) % 3, (y[1] + b[1]) % 3)

        if any(sig(sig(x)) != x
               for x in itertools.product(range(3), repeat=2)):
            continue
        fixed = [x for x in itertools.product(range(3), repeat=2)
                 if sig(x) == x]
        if fixed != [CENTER]:
            continue
        cond_a_maps.append((A, b))
        dimg = [norm_dir(apply_A(A, dv)) for dv in DIRS]
        moved = sum(1 for i, dv in enumerate(DIRS) if dimg[i] != dv)
        if moved == 4:
            both_maps.append((A, b))

info("滿足條件 (a) 的仿射對合數", len(cond_a_maps))
check("條件 (a) 的線性部分全為 -I",
      sorted({A for A, b in cond_a_maps}), [(2, 0, 0, 2)])

for A, b in cond_a_maps:
    dimg = [norm_dir(apply_A(A, dv)) for dv in DIRS]
    if dimg != DIRS:
        bad("-I 對方向的作用應為平凡", dimg, DIRS)
ok("條件 (a) 的對合固定全部 4 個方向", DIRS)

check("同時滿足 (a) 與 (b) 的對合數", len(both_maps), 0)
print("#" * 60)
print("#  障礙定理：不存在 AG(2,3) 的仿射對合同時滿足")
print("#    (a) 9 點中只固定中心")
print("#    (b) 4 個方向作 2+2 對換")
print("#  => PUB 豁免核律是被迫的，不是隨手加的例外。")
print("#  這是本倉庫第一條由宣告還原為定理的規則。")
print("#" * 60)

print("")
print("--- 六、333 與本系統的算術關係 ---")

import math

check("333 = 3^2 x 37", 9 * 37, 333)
check("333 正因數", [d for d in range(1, 334) if 333 % d == 0],
      [1, 3, 9, 37, 111, 333])
check("sigma(333)", (1 + 3 + 9) * (1 + 37), 494)
check("真因數和", 494 - 333, 161)
check("虧度", 333 - 161, 172)
check("哈沙德：333 / 9", 333 // 9, 37)
check("十一邊形數 n=9", 9 * (9 * 9 - 7) // 2, 333)


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


check("1997, 1999 皆質", [is_prime(1997), is_prime(1999)], [True, True])
check("3329, 3331 皆質", [is_prime(3329), is_prime(3331)], [True, True])
check("2 x 333^2", 2 * 333 * 333, 221778)

GL3 = 26 * 24 * 18
GL4 = 80 * 78 * 72 * 54
check("|GL(3,F3)|", GL3, 11232)
check("|GL(4,F3)|", GL4, 24261120)
check("gcd(333, |GL(3,F3)|)", math.gcd(333, GL3), 9)
check("gcd(333, |GL(4,F3)|)", math.gcd(333, GL4), 9)
print("# 唯一公因數是 9，且 9 作為公因數是平凡的。質因數 37 在本系統無來源。")
print("# => 333 與 13 點系統在算術上不相交。")

print("")
print("--- 七、本腦本不驗的部分 ---")
skip("PUB 四格 = l_inf 四方向",
     "候選識別，未建立具體雙射。PUB 原本由宣告定義。FORMAL_MODEL")
skip("現行 13x13 圖 = PG(2,3) incidence 圖",
     "否。後者是 4-正則二分圖，前者 deg(5) = 8。兩者不同圖")
skip("PUB sum = 23 的幾何來源", "本腦本未提供。OPEN")
skip("A000228(7) = 333 與本系統的連結",
     "OEIS 事實為真，但到 GL(13,F3) 無映射。正確 不等於 相關")
skip("三兔共耳在 F3 值層的實現", "尚未建構。OPEN")

print("")
print("=" * 66)
print("PASS=" + str(PASSES) + "  FAIL=" + str(FAILS) + "  SKIP=" + str(SKIPS))
print("本腦本只証明上列斷言。它不証明 PUB 就是 l_inf。")
print("=" * 66)

sys.exit(1 if FAILS else 0)
