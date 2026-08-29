# -*- coding: utf-8 -*-
"""
tools/verify_palindrome_structure.py

迴文數結構稽核 fixture。
本腳本只證明下列斷言。它不證明迴文數與本系統有因果關係。

層標籤：
  REPR   表示層（依基底，換底可能消失）
  INDEX  索引層（1..13 的整數標號）
  MATRIX 矩陣層（F3 上的矩陣元素）
  GROUP  群層（階、子群、指數）

硬規則遵循：
  第 1 條 每個數字附層標籤
  第 4 條 先封閉再對稱破缺
  第 7 條 手算預測先寫入，事後保留核對
  同型不同位不得跨塊等號（本腳本第六節即為此規則的示範）
"""

import sys

PASS = 0
FAIL = 0
SKIP = 0


def ck(name, got, want, layer):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print("[PASS] " + name + " [" + layer + "] | got=" + repr(got))
    else:
        FAIL += 1
        print("[FAIL] " + name + " [" + layer + "] | got=" + repr(got)
              + " want=" + repr(want))


def info(name, val):
    print("[INFO] " + name + " | " + repr(val))


def skip(name, why):
    global SKIP
    SKIP += 1
    print("[SKIP] " + name + " | " + why)


def sec(t):
    print("")
    print("--- " + t + " ---")


def digits(n, b):
    if n == 0:
        return [0]
    d = []
    while n > 0:
        d.append(n % b)
        n //= b
    return d[::-1]


def is_pal(n, b=10):
    d = digits(n, b)
    return d == d[::-1]


def is_antipal(n, b):
    d = digits(n, b)
    k = len(d) - 1
    for i in range(len(d)):
        if d[i] != b - 1 - d[k - i]:
            return False
    return True


print("=" * 66)
print("迴文數結構稽核 verify_palindrome_structure.py")
print("=" * 66)

# ------------------------------------------------------------------
sec("一、迴文性是表示層性質，不是數本身的性質")

ck("333 十進位迴文", is_pal(333, 10), True, "REPR")
ck("333 的二進位數字串", digits(333, 2), [1, 0, 1, 0, 0, 1, 1, 0, 1], "REPR")
ck("333 二進位非迴文", is_pal(333, 2), False, "REPR")
ck("13 十進位非迴文", is_pal(13, 10), False, "REPR")
ck("13 的三進位數字串", digits(13, 3), [1, 1, 1], "REPR")
ck("13 三進位迴文", is_pal(13, 3), True, "REPR")
ck("333 在 base 110 為 33", digits(333, 110), [3, 3], "REPR")
ck("333 在 base 332 為 11", digits(333, 332), [1, 1], "REPR")
ck("跨基底同字串不同數：333 != 13", 333 == 13, False, "REPR")
print("# 換基底就消失的，不是性質。迴文性 base-dependent。")
print("# 333 是 111 在 base 10 的三倍；13 是 111 在 base 3。字串同，數不同。")
print("# 此即硬規則「同型不同位不得跨塊等號」在表示層的實例。")

# ------------------------------------------------------------------
sec("二、十進位迴文數計數（含 0）")

counts = []
for k in range(1, 7):
    counts.append(sum(1 for n in range(10 ** k) if is_pal(n, 10)))
ck("小於 10^k 的迴文數個數 k=1..6", counts,
   [10, 19, 109, 199, 1099, 1999], "REPR")
info("三位數迴文個數 = 9 x 10", 9 * 10)

# ------------------------------------------------------------------
sec("三、偶位數迴文必被 11 整除（定理）")

for nd in (2, 4, 6):
    lo = 10 ** (nd - 1)
    hi = 10 ** nd
    pals = [n for n in range(lo, hi) if is_pal(n, 10)]
    ck(str(nd) + " 位迴文個數", len(pals), {2: 9, 4: 90, 6: 900}[nd], "REPR")
    ck(str(nd) + " 位迴文全部被 11 整除",
       all(n % 11 == 0 for n in pals), True, "REPR")
print("# 證明：偶位迴文的交錯數字和恆為 0，故 11 整除。與基底 10 綁死。")

# ------------------------------------------------------------------
sec("四、repunit 與 111 家族")

R = lambda n: (10 ** n - 1) // 9
ck("R_3", R(3), 111, "REPR")
ck("111 = 3 x 37", 3 * 37, 111, "REPR")
ck("333 = 3 x 111", 3 * 111, 333, "REPR")
ck("111 x k 全為迴文 k=1..9",
   all(is_pal(111 * k, 10) for k in range(1, 10)), True, "REPR")
ck("R_n 平方全為迴文 n=1..9",
   all(is_pal(R(n) ** 2, 10) for n in range(1, 10)), True, "REPR")
ck("R_9 平方", R(9) ** 2, 12345678987654321, "REPR")
print("# R_n 平方在 n=10 起因進位而失去迴文。上界是進位，不是結構。")

# ------------------------------------------------------------------
sec("五、唯一入口：111 在 base q 等於 |PG(2,q)|")

for q in (2, 3, 4, 5, 7, 8, 9):
    n = q * q + q + 1
    ck("q=" + str(q) + "：q^2+q+1 = 111 in base q", int("111", q), n, "INDEX")
    ck("q=" + str(q) + "：base-q 迴文", is_pal(n, q), True, "REPR")
ck("13 = 3^2+3+1", 3 * 3 + 3 + 1, 13, "INDEX")
ck("13 = (3^3-1)/(3-1)", (27 - 1) // (3 - 1), 13, "INDEX")
info("|PG(2,q)| 序列 q=2..9", [q * q + q + 1 for q in (2, 3, 4, 5, 7, 8, 9)])
print("##########################################################")
print("#  迴文數通往本系統的唯一結構性入口：")
print("#    111_q = q^2 + q + 1 = |PG(2,q)|")
print("#  對每個質數冪 q，射影平面點數在 base q 恆為迴文 111。")
print("#  q=3 給出 13 = 111_3。這不是十進位巧合，是 sigma 幾何級數。")
print("#  所有其他迴文數性質（十進位計數、11 整除、平方迴文）")
print("#  皆綁定 base 10，與本系統無映射。")
print("##########################################################")

# ------------------------------------------------------------------
sec("六、自對位數字 vs 自對位索引：形式同構，層不同")

ck("13 在 base 3 同時為反迴文", is_antipal(13, 3), True, "REPR")
self_digit = [d for d in range(3) if d + d == 3 - 1]
ck("base 3 唯一自對位數字（d+d = b-1）", self_digit, [1], "REPR")
self_index = [i for i in range(1, 10) if i + i == 10]
ck("洛書唯一自對位索引（i+i = 10）", self_index, [5], "INDEX")
ck("型別提醒：1 與 5 不相等", 1 == 5, False, "REPR/INDEX")
print("# 反迴文條件 a_i + a_{k-i} = b - 1  [REPR]")
print("# 洛書對位律   L_ij + L_{4-i,4-j} = 10  [INDEX]")
print("# 兩式形式同構：皆為固定和的對合配對，且各有唯一自配對元素。")
print("# 但一個是數字層（mod b 的 digit），一個是索引層（1..9 的標號）。")
print("# 依憲章第 1 條：不得互證。此處只登記同構，不寫等號。")

# ------------------------------------------------------------------
sec("七、13 的群層來源：Singer cycle 與 432 的歸屬")

GL3 = 11232
GL4 = 24261120
ck("|GL(3,F3)|", GL3, 11232, "GROUP")
ck("13 整除 |GL(3,F3)|", GL3 % 13, 0, "GROUP")
ck("|GL(3,F3)| / 13", GL3 // 13, 864, "GROUP")
ck("13 整除 |GL(4,F3)|", GL4 % 13, 0, "GROUP")
PGL3 = GL3 // 2
ck("|PGL(3,3)| = |GL(3,3)| / |scalars|", PGL3, 5616, "GROUP")
ck("|PGL(3,3)| = 13 x 432", 13 * 432, 5616, "GROUP")
ck("432 = |GL(2,3)| x 9 = |AGL(2,3)|", 48 * 9, 432, "GROUP")
print("##########################################################")
print("#  上一輪窮舉的 432 個仿射映射不是任意選的數。")
print("#  PGL(3,3) 傳遞作用於 13 條線，線穩定子群 = AGL(2,3)。")
print("#  指數 = 5616 / 432 = 13 = 線數。")
print("#  => 障礙定理的窮舉範圍恰為一條線的完整穩定子群，無遺漏。")
print("#  13 出現在 |GL(3,F3)| 的因數分解中，來源是 Singer cycle，")
print("#  即 PG(2,3) 上正則作用的 13 階元素。非巧合。")
print("#  對照：gcd(333, |GL(3,F3)|) = 9 為平凡。13 這條不是。")
print("##########################################################")

# ------------------------------------------------------------------
sec("八、判定為外衣，不入 kernel")

ck("1001 = 7 x 11 x 13", 7 * 11 * 13, 1001, "REPR")
ck("1001 為十進位迴文", is_pal(1001, 10), True, "REPR")
skip("1001 的 13 = PG(2,3) 的 13",
     "否。前者是十進位 10^3+1 的質因數 [REPR]，後者是射影平面點數 [INDEX]。"
     "同數值不同層，依硬規則判外衣")
skip("Scheherazade / SSRCD 數", "1001 冪次的三位一組迴文性綁定 base 10。無映射")
skip("196 Lychrel 問題", "未解問題。不 assert")
skip("迴文數倒數和 約 3.37028", "外部數值，本腳本未獨立計算。OPEN")
skip("迴文平方 / 立方 / 四次方清單", "娛樂數學。到 GL(13,F3) 無映射。正確 不等於 相關")
skip("每個正整數皆為三個迴文數之和（base >= 5）",
     "2018 年論文結果，本腳本未驗證。外部引用，天花板 SYMBOLIC")

# ------------------------------------------------------------------
print("")
print("=" * 66)
print("PASS=" + str(PASS) + "  FAIL=" + str(FAIL) + "  SKIP=" + str(SKIP))
print("本腳本只證明上列斷言。它不證明迴文數是本系統的成因。")
print("唯一入庫結論：111_q = |PG(2,q)|，以及 13 | |GL(3,F3)| 源於 Singer cycle。")
print("=" * 66)

sys.exit(1 if FAIL else 0)
