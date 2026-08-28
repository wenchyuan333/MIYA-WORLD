# tools/

可執行驗算脈本。**每一份可執行物須附 fixture**：能跑、能重現、失敗時非零隢出。

## 清單

| 脈本 | 驗何物 | 依賴 | 執行紀錄 |
| --- | --- | --- | --- |
| `verify_luoshu_constants.py` | `kernel/LUOSHU-CONSTANTS.md` K-01～K-13 | 零（純標準庫）| **EXECUTED_EXIT_0**（2026-08-29）— 見 §執行紀錄 |

## 執行方式

```
git checkout feature/tools-verify-luoshu-constants
python3 tools/verify_luoshu_constants.py
echo $?     # 0 = 全過；1 = 有失敗；2 = 找不到檔案
```

Termux 上相同（須 `pkg install python`）。不需網路。

⚠️ 本脈本並未在 `main` 上。未合併前須先切到上述分支，否則會得到 `No such file or directory`。

## 執行紀錄

### 2026-08-29｜Termux / Android｜`exit 0`

| 項目 | 內容 |
| --- | --- |
| 環境 | Termux（Android），Python 3 |
| 分支 | `feature/tools-verify-luoshu-constants` |
| 結果 | **隢出碼 0** — K-01～K-13 無 FAIL |
| 驗證來源 | **倉庫操作者在本機執行並回報隢出碼 0** |
| ⚠️ 限制 | **逐行 `[PASS]` 輸出未貼入本檔**。本紀錄的憑證強度是「隢出碼 0」，不是「逐條輸出已比對」 |
| ⚠️ 限制 | 本倉庫 **仍無 CI**。沒有自動化跑這支脈本，不保証未來修改後仍過 |

因此：

- K-01～K-13 的 `TESTED` 標記現在**有一次實際執行憑證**，而非僅手算。
- 但仍**不得**升至 `SUPPORTED`：驗證仍在本倉庫内部，無獨立外部証據。
- 若日後要將憑證強度提高，須貼入完整逐行輸出或接上 CI。

## ❗ 認清單

- K-14 / K-15 / K-16 / K-17 仍為 `[SKIP]`，**本次 exit 0 不涵蓋這四項**。稀有度分子 192 與 22272 的列舉依據仍不在本倉庫。
- exit 0 不代表 `canon/` 的原點場論得到任何驗證。兩者無關。
- 驗算的是洛書矩陣的算術與線代性質，**不是**任何詮释、物理或宇宙論主張。

## 新增脈本規則

1. 零外部依賴優先；需要依賴時須在此表明列。
2. 不得印固定的成功訊息。每一條 PASS 須對應一次真實運算。
3. 失敗須 exit 1，且列出得到值與預期值。
4. 不得讀取 secrets、token、個人資料。本目錄的脈本一律零網路。
5. 執行紀錄只能在有真實執行憑證時更新，且須註明憑證強度。
