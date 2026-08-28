# tools/

可執行驗算脈本。**每一份可執行物須附 fixture**：能跑、能重現、失敗時非零隢出。

## 清單

| 脈本 | 驗何物 | 依賴 | 執行紀錄 |
| --- | --- | --- | --- |
| `verify_luoshu_constants.py` | `kernel/LUOSHU-CONSTANTS.md` K-01～K-13 | 零（純標準庫）| **EXECUTED_EXIT_0**（2026-08-29）|
| `verify_v13_pairing.py` | `protocol/HEARTBEAT-V13.md` 對位律 + 三條合法棲息條件 | 零（純標準庫）| **NOT_EXECUTED** |

## 執行方式

```
python3 tools/verify_luoshu_constants.py ; echo $?
python3 tools/verify_v13_pairing.py ; echo $?
```

`0` = 全過；`1` = 有失敗；`2` = 找不到檔案（通常是分支不對）。

Termux 上相同（須 `pkg install python`）。不需網路。

⚠️ 脈本未必已在 `main` 上。若回報 `No such file or directory`，先確認所在分支。

## 執行紀錄

### 2026-08-29｜`verify_luoshu_constants.py`｜Termux / Android｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 環境 | Termux（Android），Python 3 |
| 結果 | **隢出碼 0** — K-01～K-13 無 FAIL |
| 驗證來源 | 倉庫 owner 在本機執行並回報隢出碼 0 |
| ⚠️ 限制 | 逐行 `[PASS]` 輸出未貼入本檔。憑證強度 = 「隢出碼 0」，非「逐條輸出已比對」 |
| ⚠️ 限制 | 本倉庫仍無 CI。不保証未來修改後仍過 |

### `verify_v13_pairing.py`｜**尚未執行**

建庫者無執行環境，也不能設定 Actions 使其自動跑（那是 owner 手動閘口）。

未經執行前，**不得宣稱 HEARTBEAT-V13 的對位律已驗**。

## ❗ 認清單

- `verify_luoshu_constants.py` 的 K-14 / K-15 / K-16 / K-17 仍為 `[SKIP]`，exit 0 不涵蓋這四項。稀有度分子 192 與 22272 的列舉依據仍不在本倉庫。
- 任何 exit 0 都**不代表** `canon/` 的原點場論得到驗證。兩者不互相背書。
- 驗的是算術、線代與格式自洽性，**不是**任何詮释、物理或宇宙論主張。

## 新增脈本規則

1. 零外部依賴優先；需要依賴時須在此表明列。
2. 不得印固定的成功訊息。每一條 PASS 須對應一次真實運算。
3. 失敗須 exit 1，且列出得到值與預期值。
4. 未驗項目須標 `[SKIP]` 並寫出理由。
5. 不得讀取 secrets、token、個人資料。本目錄一律零網路。
6. 執行紀錄只能在有真實執行憑證時更新，且須註明憑證強度。
