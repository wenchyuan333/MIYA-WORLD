# tools/

可執行驗算脈本。**每一份可執行物須附 fixture**：能跑、能重現、失敗時非零隢出。

## 清單

| 脈本 | 驗何物 | 依賴 | 本倉庫執行紀錄 |
| --- | --- | --- | --- |
| `verify_luoshu_constants.py` | `kernel/LUOSHU-CONSTANTS.md` K-01～K-13 | 零（純標準庫）| **NOT_EXECUTED** |

## 執行方式

```
python3 tools/verify_luoshu_constants.py
echo $?     # 0 = 全過；1 = 有失敗
```

Termux 上相同（須 `pkg install python`）。不需網路。

## ❗ 認清單

- 上表「本倉庫執行紀錄」欄一律 `NOT_EXECUTED`。本倉庫目前沒有 CI 跑過任何脈本。
- 要把某一行改成已執行，須附上真實的執行輸出與日期，且在 PR 中貼出。沒有憑證不得改。
- 脈本內的 `[SKIP]` 項是故意保留的：上游依據未驗時宁可跳過，也不造假成 PASS。

## 新增脈本規則

1. 零外部依賴優先；需要依賴時須在此表明列。
2. 不得印固定的成功訊息。每一條 PASS 須對應一次真實運算。
3. 失敗須 exit 1，且列出得到值與預期值。
4. 不得讀取 secrets、token、個人資料。本目錄的脈本一律零網路。
