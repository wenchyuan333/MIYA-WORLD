# tools/

可執行驗算脈本。**每一份可執行物須附 fixture**：能跑、能重現、失敗時非零隢出。

## 清單

| 脈本 | 驗何物 | 依賴 | 執行紀錄 |
| --- | --- | --- | --- |
| `verify_luoshu_constants.py` | `kernel/LUOSHU-CONSTANTS.md` K-01～K-13 | 零 | **EXECUTED_EXIT_0**（2026-08-29）隢出碼只 |
| `verify_v13_pairing.py` | `protocol/HEARTBEAT-V13.md` 對位律 + 三條合法棲息條件 | 零 | **EXECUTED_EXIT_0**（2026-08-29）29 PASS / 5 SKIP，逐行輸出已入庫 |
| `verify_bijection_b13.py` | 對位律的矩陣實例 P（B<-> 置換）| 零 | **NOT_EXECUTED** |

所有脈本：純 Python 標準庫、零外部依賴、零網路。

## 執行方式

```
git fetch origin
python3 tools/verify_luoshu_constants.py ; echo $?
python3 tools/verify_v13_pairing.py ; echo $?
python3 tools/verify_bijection_b13.py ; echo $?
```

`0` = 全過；`1` = 有失敗；`2` = 找不到檔案。

⚠️ 回報 `No such file or directory` 或 `pathspec did not match` 時，先跑 `git fetch origin` 再切分支。
新推的分支在本機須 fetch 後才可見。

要留位元級收據，直接重定向：

```
python3 tools/verify_v13_pairing.py > tools/logs/$(date +%F)-v13.log 2>&1 ; echo $?
```

## 執行紀錄

### 2026-08-29｜`verify_v13_pairing.py`｜Termux｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 環境 | Termux（Android），Python 3，分支 `feature/protocol-heartbeat-v13` |
| 結果 | **29 PASS / 5 SKIP / 0 FAIL，隢出碼 0** |
| 憑證 | 逐行輸出已入庫：`tools/logs/2026-08-29-verify_v13_pairing.log` |
| 憑證強度 | 逐條 `got` / `expected` 可比對（高於只有隢出碼）|
| ⚠️ 限制 | log 為 **轉錄整理**，非位元級對拷。字形差異未逐字核對 |
| ⚠️ 限制 | 本倉庫仍無 CI。不保証未來修改後仍過 |

### 2026-08-29｜`verify_luoshu_constants.py`｜Termux｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 結果 | **隢出碼 0** — K-01～K-13 無 FAIL |
| ⚠️ 限制 | 逐行輸出未入庫。憑證強度 = 「隢出碼 0」，低於 V13 那份 |

### `verify_bijection_b13.py`｜**尚未執行**

建庫者無執行環境。未經執行前，**不得宣稱 B<-> 置換矩陣已驗**。

建庫者的手算預測（**尚未機器確認**）：6 個互換為偶置換，所以 `det(P) = +1`；PUB 區兩個互換也是偶，所以 `pub_det = +1`。
若實際跑出不同，**是我算錯了**，改的是預測不是 assert。

## ❗ 認清單

- `verify_luoshu_constants.py` 的 K-14 / K-15 / K-16 / K-17 仍為 `[SKIP]`。稀有度分子 192 與 22272 的列舉依據仍不在本倉庫。
- 任何 exit 0 都**不代表** `canon/` 的原點場論得到驗證。兩者不互相背書。
- 驗的是算術、線代與格式自洽性，**不是**任何詮释、物理或宇宙論主張。
- 「對位律自洽」與「對位律描述了什麼」是兩件事。前者已驗，後者未驗。

## 新增脈本規則

1. 零外部依賴優先；需要依賴時須在此表明列。
2. 不得印固定的成功訊息。每一條 PASS 須對應一次真實運算。
3. 失敗須 exit 1，且列出得到值與預期值。
4. 未驗項目須標 `[SKIP]` 並寫出理由。
5. 不得讀取 secrets、token、個人資料。本目錄一律零網路。
6. 執行紀錄只能在有真實執行憑證時更新，且須註明憑證強度。
