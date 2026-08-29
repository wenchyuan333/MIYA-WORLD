#!/usr/bin/env python3
# conifold 的 Z2xZ2 軌形（方格晶格 dimer 2x2 擴胞）與洛書標號的相容範圍
# 手算預測（先寫入，事後核對；tools/README.md 第 7 條）
#   P-01 完美匹配數 = 24
#   P-02 重數表 = [[1,2,1],[2,12,2],[1,2,1]]
#   P-03 sum m*L = 120
#   P-04 共線三元組 = 128（過中心 120，不過中心 8）
#   P-05 全 +1 行列式 |係數| 和 = 16 != 24
#   P-06 B = mK 在 F=3 下 Euler 界給 m <= 3
#   P-07 [im(3K):im(6K)] = 4
from itertools import permutations, combinations
from collections import Counter
from math import gcd
P = 0; FA = 0; SK = 0
def ok(msg, cond):
    global P, FA
    if cond: P += 1; print("[PASS] " + msg)
    else: FA += 1; print("[FAIL] " + msg)
def eq(msg, got, want):
    ok(msg + " | got=" + repr(got) + " want=" + repr(want), got == want)
def skip(msg):
    global SK
    SK += 1; print("[SKIP] " + msg)
def det3(A):
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
          - A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
          + A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))
def smith3(A):
    d1 = 0
    for row in A:
        for x in row: d1 = gcd(d1, abs(x))
    mm = [A[r0][c0]*A[r1][c1]-A[r0][c1]*A[r1][c0]
          for r0,r1 in combinations(range(3),2)
          for c0,c1 in combinations(range(3),2)]
    D2 = 0
    for x in mm: D2 = gcd(D2, abs(x))
    return (d1, D2//d1 if d1 else 0, abs(det3(A))//D2 if D2 else 0)

print("--- 一、2x2 擴胞完美匹配枚舉 ---")
VS = [(0,0),(0,1),(1,0),(1,1)]
cnt = Counter()
for s in permutations(VS):
    a = sum(1 for i,v in enumerate(VS) if v[0]==1 and s[i][0]==0)
    b = sum(1 for i,v in enumerate(VS) if v[1]==1 and s[i][1]==0)
    cnt[(a,b)] += 1
m = [[cnt[(x,y)] for y in (0,1,2)] for x in (0,1,2)]
tot_m = sum(cnt.values())
eq("圖為 K4,4，完美匹配數", tot_m, 24)
eq("重數表 m", m, [[1,2,1],[2,12,2],[1,2,1]])
eq("角點重數（extremal matching 唯一性）", [m[0][0],m[0][2],m[2][0],m[2][2]], [1,1,1,1])
eq("邊中點重數（邊界二項式係數）", [m[0][1],m[1][0],m[1][2],m[2][1]], [2,2,2,2])
eq("內點重數", m[1][1], 12)
eq("a 邊際分佈", [sum(r) for r in m], [4,16,4])
eq("b 邊際分佈", [sum(m[i][j] for i in range(3)) for j in range(3)], [4,16,4])
ok("m 中心對稱", all(m[i][j]==m[2-i][2-j] for i in range(3) for j in range(3)))

print("--- 二、全 +1 行列式不是匹配數 ---")
c1 = [1,-2,1]
dm = [[c1[i]*c1[j] for j in range(3)] for i in range(3)]
eq("det(F tensor G) = (1-z)^2(1-w)^2 係數", dm, [[1,-2,1],[-2,4,-2],[1,-2,1]])
absum = sum(abs(dm[i][j]) for i in range(3) for j in range(3))
eq("|係數| 和", absum, 16)
ok("16 != 24：缺 Kasteleyn 定向", absum != tot_m)
eq("中心抵消量", m[1][1] - abs(dm[1][1]), 8)
ok("邊界八格未被污染（|det| 係數 = 枚舉重數）",
   all(abs(dm[i][j]) == m[i][j] for i in range(3) for j in range(3) if (i,j) != (1,1)))

print("--- 三、洛書標號耦合 ---")
L = [[4,9,2],[3,5,7],[8,1,6]]
sml = sum(m[i][j]*L[i][j] for i in range(3) for j in range(3))
eq("sum m*L", sml, 120)
ok("sum m*L = 5 * sum m", sml == 5*tot_m)
w2 = [[7,3,7],[5,101,5],[7,3,7]]
ok("任意中心對稱權重也給平均 5 => 此式只驗對稱性，不驗重數",
   sum(w2[i][j]*L[i][j] for i in range(3) for j in range(3)) == 5*sum(sum(r) for r in w2))

print("--- 四、共線三元組計數 ---")
LN = [[(0,0),(0,1),(0,2)],[(1,0),(1,1),(1,2)],[(2,0),(2,1),(2,2)],
      [(0,0),(1,0),(2,0)],[(0,1),(1,1),(2,1)],[(0,2),(1,2),(2,2)],
      [(0,0),(1,1),(2,2)],[(0,2),(1,1),(2,0)]]
eq("幻方線數", len(LN), 8)
ok("八條線 L 和皆為 15", all(sum(L[i][j] for i,j in ln)==15 for ln in LN))
pr = []
for ln in LN:
    p = 1
    for i,j in ln: p *= m[i][j]
    pr.append(p)
eq("逐線重數積", pr, [2,48,2,2,48,2,12,12])
eq("共線三元組總數", sum(pr), 128)
thru = sum(p for ln,p in zip(LN,pr) if (1,1) in ln)
eq("過中心四線", thru, 120)
eq("不過中心四線", sum(pr)-thru, 8)

print("--- 五、Newton 多邊形 [0,2]^2 ---")
pts = [(x,y) for x in range(3) for y in range(3)]
inn = [p for p in pts if 0<p[0]<2 and 0<p[1]<2]
bnd = [p for p in pts if p not in inn]
eq("內點數 I", len(inn), 1)
eq("邊界格點數 B", len(bnd), 8)
ar = len(inn) + len(bnd)/2 - 1
eq("Pick 面積 A", ar, 4.0)
eq("正規化面積 N = 規範群數", int(2*ar), 8)
ok("反身 I=1 => N = B，是定理不是巧合", len(inn)==1 and int(2*ar)==len(bnd))
eq("支撐集 = 全部 9 格點", sorted(cnt.keys()), sorted(pts))
ok("匹配數 >= 規範群數", tot_m >= int(2*ar))

print("--- 六、h(v) = L(v) - 5 ---")
h = [[L[i][j]-5 for j in range(3)] for i in range(3)]
eq("h", h, [[-1,4,-3],[-2,0,2],[3,-4,1]])
ok("h 為奇函數", all(h[i][j] == -h[2-i][2-j] for i in range(3) for j in range(3)))
ok("等價於對位律 L(v)+L(-v)=10", all(L[i][j]+L[2-i][2-j]==10 for i in range(3) for j in range(3)))
eq("h(0)", h[1][1], 0)
ok("全 8 條線 sum h = 0（不限過原點）", all(sum(h[i][j] for i,j in ln)==0 for ln in LN))

print("--- 七、洛書矩陣層 ---")
tr = sum(L[i][i] for i in range(3))
e2 = sum(L[a][a]*L[b][b]-L[a][b]*L[b][a] for a,b in combinations(range(3),2))
dt = det3(L)
eq("tr", tr, 15); eq("二階主子式和", e2, 24); eq("det", dt, 360)
ok("char poly t^3 - 15t^2 + 24t - 360 = (t-15)(t^2+24)", (tr,e2,dt)==(15,24,360))
ok("15 * 24 = det（成立當且僅當非 Perron 譜和為 0）", 15*24 == dt)
eq("Smith(L)", smith3(L), (1,1,360))
ok("循環，不是 Z/6 + Z/60", smith3(L) == (1,1,360))
Bm = [[L[i][j]-L[j][i] for j in range(3)] for i in range(3)]
KK = [[0,1,-1],[-1,0,1],[1,-1,0]]
ok("B = M - M^T = 6K", Bm == [[6*KK[i][j] for j in range(3)] for i in range(3)])
eq("det B", det3(Bm), 0)
eq("B (1,1,1)^T", [sum(Bm[i]) for i in range(3)], [0,0,0])
ok("ker B 含 (1,1,1) <=> 逐位行和 = 列和（半幻方條件，非 Perron 神秘性）",
   all(sum(L[i]) == sum(L[k][i] for k in range(3)) for i in range(3)))

print("--- 八、dimer NO-GO ---")
for mm, exp in ((1,False),(2,True),(3,True),(6,False)):
    Ec = 3*mm; Vc = Ec - 3
    eq("B = " + str(mm) + "K  E=" + str(Ec) + " V=" + str(Vc) + " Euler+valence", (Ec <= 9) and (Vc >= 1), exp)
ok("dP0 (3K) 恰飽和 E = 3F = 9", 3*3 == 9)
ok("6K 超界一倍 E = 18 = 2 * 3F", 3*6 == 18)
eq("先前記錄的 45 應為 18（sum |B_ij|）", sum(abs(6*KK[i][j]) for i,j in [(0,1),(0,2),(1,2)]), 18)
eq("Smith(3K)", smith3([[3*KK[i][j] for j in range(3)] for i in range(3)]), (3,3,0))
eq("Smith(6K)", smith3([[6*KK[i][j] for j in range(3)] for i in range(3)]), (6,6,0))
eq("[im(3K):im(6K)]（rank 2 上乘 2）", (6*6)//(3*3), 4)

print("--- 九、W(8 節點) 拓樸自檢 ---")
Vd, Ed, Fd = 8, 16, 8
eq("超勢項數 V", Vd, 8); eq("場數 E", Ed, 16)
eq("規範群數 F = 正規化面積", Fd, int(2*ar))
eq("Euler V - E + F", Vd - Ed + Fd, 0)
ok("E <= 3F（16 <= 24）", Ed <= 3*Fd)
eq("平均頂點度 2E/V", 2*Ed//Vd, 4)

skip("W 逐項閉圈檢查：需要 W 全文，本 session 未取得")
skip("R-charge 對應 HOLD：9 格點 vs 16 邊 vs 4 角點(sum a_i = 2)，三個指標集皆不匹配")
skip("四個 8：N=B 已證為反身定理；8 條幻方線與 V=8 屬獨立來源")
skip("洛書 <-> 鏡像對稱 REJECT：組合對稱不傳遞到 Hodge 數")
skip("det 360 <-> anomaly REJECT：未註冊觀測量")
skip("F3 迴文向量子空間（dim 7 / 6）與 full_det mod 3 = 2 的關係仍 OPEN")
print("")
print("PASS=" + str(P) + " FAIL=" + str(FA) + " SKIP=" + str(SK))
raise SystemExit(1 if FA else 0)
