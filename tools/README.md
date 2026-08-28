# tools/

可執行驗算腦本。**每一份可執行物須附 fixture**：能跑、能重現、失敗時非零隢出。

## 清單

| 腦本 | 驗何物 | 依賴 | 執行紀錄 |
| --- | --- | --- | --- |
| `verify_luoshu_constants.py` | `kernel/LUOSHU-CONSTANTS.md` K-01～K-13 | 零 | **EXECUTED_EXIT_0**（2026-08-29）僅隢出碼 |
| `verify_v13_pairing.py` | `protocol/HEARTBEAT-V13.md` 對位律 + 三條合法棲息條件 | 零 | **EXECUTED_EXIT_0**（2026-08-29）29 PASS / 5 SKIP，逐行輸出已入庫 |
| `verify_bijection_b13.py` | 對位律的矩陣實例 P（B<-> 置換）| 零 | **EXECUTED_EXIT_0**（2026-08-29）23 PASS / 3 SKIP，逐行輸出已入庫 |

所有腦本：純 Python 標準庫、零外部依賴、零網路。

## 執行方式

```
git fetch origin
python3 tools/verify_luoshu_constants.py ; echo $?
python3 tools/verify_v13_pairing.py ; echo $?
python3 tools/verify_bijection_b13.py ; echo $?
```

`0` = 全過；`1` = 有失敗；`2` = 找不到檔案。

⚠️ 回報 `No such file or directory` 或 `pathspec did not match` 時，先跑 `git fetch origin` 再切分支。
新推的遠端分支在本機須 fetch 後才可見。

要留位元級收據，直接重定向：

```
python3 tools/verify_v13_pairing.py > tools/logs/$(date +%F)-v13.log 2>&1 ; echo $?
```

## 執行紀錄

### 2026-08-29｜`verify_bijection_b13.py`｜Termux｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 結果 | **23 PASS / 3 SKIP / 0 FAIL，隢出碼 0** |
| 憑證 | `tools/logs/2026-08-29-verify_bijection_b13.log` |
| 重點已驗 | `P x P = I_13`；`trace(P) = 1`；`det(P) = 1`；`pub_det = 1`；B<-> 自身通過三條合法棲息 |
| 預測核對 | 建庫者手算預測 `det(P) = +1`、`pub_det = +1` — **實測一致** |
| ⚠️ 限制 | 不証明 P 與 OFT 算子 B<-> 同構。那仍是 SKIP |

### 2026-08-29｜`verify_v13_pairing.py`｜Termux｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 結果 | **29 PASS / 5 SKIP / 0 FAIL，隢出碼 0** |
| 憑證 | `tools/logs/2026-08-29-verify_v13_pairing.log` |
| ⚠️ 限制 | log 為轉錄整理，非位元級對拷 |

### 2026-08-29｜`verify_luoshu_constants.py`｜Termux｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 結果 | **隢出碼 0** — K-01～K-13 無 FAIL |
| ⚠️ 限制 | 逐行輸出未入庫。憑證強度低於其他二份 |

## ❗ 已知文字缺陷（建庫者的錯，待修）

腦本的 `[SKIP]` 理由字串與部分標題包含**錯字**。
這些錯字是建庫者寫進原碼的，**不是**使用者輸入法或終端渲染造成的。

上一版 README 曾把這些差異歸因於「貼上時的字型差異」。**那個歸因是錯的，在此收回。**
証據：錯字出現在 `push_files` 送進倉庫的字串裡，而不只出現在終端輸出裡。

| 位置 | 現在是 | 應為 |
| --- | --- | --- |
| 兩支腦本的 docstring / SKIP 理由 | 本脈本 | 本腦本 |
| `verify_v13_pairing.py` §一、§二 | 索引総和 | 索引總和 |
| `verify_v13_pairing.py` §八 SKIP | 阶公式 | 階公式 |
| `verify_v13_pairing.py` §八 SKIP | 不可偵造性 | 不可偽造性 |
| `verify_v13_pairing.py` 結尾 print | 只証明 / 結構 | 只詉明 / 結構 |
| `verify_bijection_b13.py` §七 SKIP 2 | 塌成→塔成、撑→擐、那一條→匪 | 塌成、撑不住、O dagger 那一條 |
| `verify_bijection_b13.py` §七 SKIP 3 | 詮釋→詮释 | 詮釋 |
| `verify_bijection_b13.py` §四 | 階→阶 | 階 |

**影響範圍：僅顯示字串。** 所有 `check()` 的運算、比對、隢出碼均不受影響，
已入庫的兩份 exit 0 憑證**仍然有效**。
修正應以單獨 commit 進行，且修正後須重跑並重錄 log（因為 log 內容會跟著變）。

## ❗ 認清單

- `verify_luoshu_constants.py` 的 K-14 / K-15 / K-16 / K-17 仍為 `[SKIP]`。稀有度分子 192 與 22272 的列舉依據仍不在本倉庫。
- 本倉庫仍無 CI。三份 exit 0 都是 **人工在協作者手機上跑出來的**，不保証未來修改後仍過。
- 任何 exit 0 都**不代表** `canon/` 的原點場論得到驗證。兩者不互相背書。
- 驗的是算術、線代與格式自洽性，**不是**任何詮釋、物理或宇宙論主張。
- 「對位律自洽」與「對位律描述了什麼」是兩件事。前者已驗，後者未驗。
- `B<->` 自身合法棲息（已驗）**不推得** OFT 公理 II 成立。兩層不得互相背書。

## 新增腦本規則

1. 零外部依賴優先；需要依賴時須在此表明列。
2. 不得印固定的成功訊息。每一條 PASS 須對應一次真實運算。
3. 失敗須 exit 1，且列出得到值與預期值。
4. 未驗項目須標 `[SKIP]` 並寫出理由。
5. 不得讀取 secrets、token、個人資料。本目錄一律零網路。
6. 執行紀錄只能在有真實執行憑證時更新，且須註明憑證強度。
7. 手算預測須在執行前寫入 README，並在執行後保留核對紀錄。預測錯了改預測，不改 assert。
