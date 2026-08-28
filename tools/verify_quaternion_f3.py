#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_quaternion_f3.py

驗 PASTEABLE-FORMAL-V13.1 §[2] 裡那句「M_Q = a + bi + cj + dk, a,b,c,d 屬於 F3」。

這句話指定了一個具體物：以 F_3 為係數的四元數代數。
它是 4 維的，所以它就坐在 PUB 的 F_3^4 上。這一點是可算的。

但它有一個重要的、與直覺相反的結果：
在特征 3 下，四元數代數**不是**除環。它有零因子。
本腦本把這件事用兩種獨立方式算出來。

純 Python 標準庫（只用 math 算堆積密度）。零網路。不讀 secrets。不寫檔。

執行：
    python3 tools/verify_quaternion_f3.py
    echo $?
"""

import math
import sys
from itertools import product

P = 3

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


# ---------------------------------------------------------------
# F_3 四元數：(a, b, c, d) 代表 a + bi + cj + dk
# ---------------------------------------------------------------

ONE = (1, 0, 0, 0)
NEG_ONE = (2, 0, 0, 0)
I = (0, 1, 0, 0)
J = (0, 0, 1, 0)
K = (0, 0, 0, 1)
ZERO = (0, 0, 0, 0)


def qmul(p, q):
    a1, b1, c1, d1 = p
    a2, b2, c2, d2 = q
    a = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
    b = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
    c = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
    d = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
    return (a % P, b % P, c % P, d % P)


def qadd(p, q):
    return tuple((p[i] + q[i]) % P for i in range(4))


def qneg(p):
    return tuple((-p[i]) % P for i in range(4))


def qconj(p):
    return (p[0] % P, (-p[1]) % P, (-p[2]) % P, (-p[3]) % P)


def qnorm(p):
    return (p[0] * p[0] + p[1] * p[1] + p[2] * p[2] + p[3] * p[3]) % P


ALL = [tuple(t) for t in product(range(P), repeat=4)]


section("一、代數的大小與 PUB 的維度")

check("代數維度 = 4（係數 a,b,c,d）", len(ONE), 4)
check("元素總數 = 3^4", len(ALL), 81)
check("與 F_3^4 同大小（即 PUB 層）", len(ALL), P ** 4)


section("二、Q8 的乘法關係是不是真的成立")

check("i 平方 = -1", qmul(I, I), NEG_ONE)
check("j 平方 = -1", qmul(J, J), NEG_ONE)
check("k 平方 = -1", qmul(K, K), NEG_ONE)
check("ijk = -1", qmul(qmul(I, J), K), NEG_ONE)
check("ij = k", qmul(I, J), K)
check("ji = -k", qmul(J, I), qneg(K))
check("非交換：ij 不等於 ji", qmul(I, J) == qmul(J, I), False)

Q8 = set()
for x in [ONE, I, J, K]:
    Q8.add(x)
    Q8.add(qneg(x))

check("Q8 元素數 = 8", len(Q8), 8)
check("Q8 對乘法封閉",
      all(qmul(x, y) in Q8 for x in Q8 for y in Q8), True)
check("Q8 每個元素的範數都 = 1",
      sorted(set(qnorm(x) for x in Q8)), [1])


section("三、範數的乘法性（引擎自檢）")

multiplicative = True
for x in ALL:
    for y in ALL:
        if qnorm(qmul(x, y)) != (qnorm(x) * qnorm(y)) % P:
            multiplicative = False
            break
    if not multiplicative:
        break

check("N(xy) = N(x)N(y) 對全部 81 x 81 對成立", multiplicative, True)
check("x 乘 x的共軸 = N(x)，對全部 81 個成立",
      all(qmul(x, qconj(x)) == (qnorm(x), 0, 0, 0) for x in ALL), True)


section("四、它不是除環——零因子存在")

# 1 + i + j 的範數 = 1 + 1 + 1 = 3 = 0 mod 3
ZD = qadd(qadd(ONE, I), J)

check("取 q = 1 + i + j", ZD, (1, 1, 1, 0))
check("q 不是零", ZD == ZERO, False)
check("N(q) = 1+1+1 = 3 = 0 mod 3", qnorm(ZD), 0)
check("q的共軸 也不是零", qconj(ZD) == ZERO, False)
check("q 乘 q的共軸 = 0 —— 兩個非零元相乘得零",
      qmul(ZD, qconj(ZD)), ZERO)
check("因此 q 不可逆：不存在 r 使 q乘r = 1",
      any(qmul(ZD, r) == ONE for r in ALL), False)


section("五、單位群數量——分裂的直接證據")

units = [x for x in ALL if any(qmul(x, r) == ONE for r in ALL)]
nonunits = [x for x in ALL if x not in units]
norm_nonzero = [x for x in ALL if qnorm(x) != 0]

check("可逆元個數（窗與範數非零一致）", len(units), len(norm_nonzero))
check("可逆元個數 = 48", len(units), 48)
check("不可逆元個數 = 33", len(nonunits), 33)
check("48 + 33 = 81", len(units) + len(nonunits), 81)

# |GL(2,F_3)| = (9-1)(9-3) = 8 x 6 = 48
gl2_order = (P * P - 1) * (P * P - P)
check("|GL(2,F_3)| = (9-1)(9-3)", gl2_order, 48)
check("單位群阶 = |GL(2,F_3)|", len(units), gl2_order)

# 範數 = 非零坐標數 mod 3（因為 F_3 上 1^2 = 2^2 = 1）
by_weight = {}
for x in ALL:
    w = sum(1 for t in x if t != 0)
    by_weight[w] = by_weight.get(w, 0) + 1

check("按非零坐標數分布 = C(4,k) x 2^k",
      [by_weight.get(k, 0) for k in range(5)], [1, 8, 24, 32, 16])
check("N(x) = 0 恰好是 k 屬於 {0, 3} 那些（1 + 32）",
      len([x for x in ALL if qnorm(x) == 0]), 33)


section("六、堆積密度：V13.1 引的數字屬於哪一維")

eta_3d = math.pi / math.sqrt(18.0)
eta_2d = math.pi / math.sqrt(12.0)

check("pi / sqrt(18) 取五位 = 0.74048", round(eta_3d, 5), 0.74048)
check("pi / sqrt(18) 等於 pi / (3 sqrt2)（三維 FCC/HCP 值）",
      round(eta_3d, 12), round(math.pi / (3.0 * math.sqrt(2.0)), 12))
check("二維六角最密堆積 pi / sqrt(12) 取五位 = 0.9069",
      round(eta_2d, 4), 0.9069)
check("兩者不相等（因而「六角」須指明維度）",
      round(eta_3d, 5) == round(eta_2d, 5), False)


section("七、黑洞半徑的退化檢查（算術層，G = c = 1）")

def r_plus(mass, spin, charge):
    inner = mass * mass - spin * spin - charge * charge
    if inner < 0:
        return None
    return mass + math.sqrt(inner)

check("a = Q = 0 時 r_+ = 2M（取 M = 1）", r_plus(1.0, 0.0, 0.0), 2.0)
check("極限 a = M 時 r_+ = M", r_plus(1.0, 1.0, 0.0), 1.0)
check("超極限 a > M 時無實根（無視界）", r_plus(1.0, 1.5, 0.0), None)


section("八、未驗項目")

skip("M_Q → exp(Q) 屬於 SU(2) 的「連續化」",
     "型別錯置。exp 需要無窮級數與極限；F_3 是特征 3 的有限體，沒有極限概念，"
     "exp 在其上未定義。Q8 確實可以嵌入 SU(2)（作為 8 阶有限子群），"
     "但那是群的嵌入，與 F_3 係數無關。特征 3 與特征 0 不得混用。")

skip("F_3 四元數代數 同構於 M_2(F_3) 的完整同構式",
     "本腦本只算出兩條必要從屬：存在零因子（所以不是除環），"
     "且單位群阶 = 48 = |GL(2,F_3)|。這兩條強烈相容於分裂，但不等於已建構同構映射。")

skip("最密堆積 eta 與 核 9 格 對位和 10 的對應",
     "未推導。eta 是歐幾得空間的體積比；對位和是整數索引的加法。"
     "兩者之間無共同定義域。這是分配，不是映射。")

skip("黑洞 r_+ 與 六角晶格 的「六角黑洞」關係",
     "Kerr-Newman 外視界在球對稱坐標下是旋轉對稱的，不是六角形的。"
     "未見到任何推導支持「六角黑洞」這個詞。")

skip("閉環式 番_Luoshu zeta(s) Q M dr = 0",
     "型別錯置。被積函數混了：zeta(s) 是複數函數；Q 與 M 是特征 3 的代數物；"
     "dr 是實測度。F_3 上無極限、無測度、無積分。本式目前不是一個數學命題。")

skip("zeta 零點 對應 六角晶格最密堆積",
     "無已知結果支持。本腦本不實作、不背書、也不反駁——只記為未驗。")


section("結果")

if failures:
    print("FAIL 數量：" + str(len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print("F_3 四元數代數 全部通過。")
print("已驗三件事：")
print("  1. 它是 4 維、8 1 個元素，恰好坐在 PUB 的 F_3^4 上。")
print("  2. Q8 的乘法關係 i2 = j2 = k2 = ijk = -1 在 F_3 上真的成立。")
print("  3. 但它不是除環：1 + i + j 的範數為 0，是零因子。")
print("     單位群阶 48 = |GL(2,F_3)|。")
print("不詉明：連續化到 SU(2)、六角黑洞、zeta 閉環式。那三項仍是 SKIP。")
sys.exit(0)
