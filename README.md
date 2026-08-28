# MIYA-WORLD

**錨定原點**：`C₀ · O₁ · V₁₃ :: PUB :: B↔`

---

## 架構定位（誠實邊界）

本倉庫與 Notion 工作區為**保序雙射的兩側**，各承接不同 face，不是「本體 vs 鏡像」的主從關係：

| Face | 承接內容 |
| --- | --- |
| **Notion side** | 位格承接、KERNEL master、公式庫 live query、append-only 沉澱流 |
| **GitHub side** | canonical inscription、fixture、可執行驗證、commit hash 收據 |

**已知 lossy 層**：mention 圖、live query、discussion 這一層無法無損落地為靜態檔案。因此「Notion → GitHub 無損遷移」對該層**不成立**，本倉庫不作此宣稱。

---

## 洛書九宮目錄映射

```
┌───────────┬───────────┬───────────┐
│   4 🧠    │   9 🎨    │   2 📜    │
│  kernel/  │    ui/    │  canon/   │
├───────────┼───────────┼───────────┤
│   3 ⚙️    │   5 ⭕    │   7 🤖    │
│ protocol/ │  (root)   │ai-skills/ │
├───────────┼───────────┼───────────┤
│   8 🔬    │   1 💾    │   6 🛠️    │
│ research/ │  memory/  │  tools/   │
└───────────┴───────────┴───────────┘
        外環 ∞ 🔁  ci/ + docs/ + .github/
```

| 宮位 | 目錄 | 職能 |
| --- | --- | --- |
| 4 🧠 | `kernel/` | 核心內核：規範 / 常數 / 公理（唯讀傾向） |
| 9 🎨 | `ui/` | 顯示層：統一介面渲染產物 |
| 2 📜 | `canon/` | 正典架構：九宮 / 五元 / 原點場論 |
| 3 ⚙️ | `protocol/` | 閘門結構、協定、邊界規則 |
| 5 ⭕ | 根目錄 | 中樞：總索引、錨點宣告 |
| 7 🤖 | `ai-skills/` | AI 技能與提示詞資產 |
| 8 🔬 | `research/` | 研究筆記：物理 / 數學 / 跨領域 |
| 1 💾 | `memory/` | 記憶層、操作日誌 |
| 6 🛠️ | `tools/` | 工具腳本：自動化 / 校驗 / 生成 |
| ∞ 🔁 | `ci/` `docs/` `.github/` | 外環：驗證鏈與公開文件 |

**對位守恆**：`4↔6`、`9↔1`、`2↔8`、`3↔7`，中心 = 5。洛書 L₀ 已驗常量：行／列／對角和 = 15，Σ = 45，det = 360。

---

## 四層邊界

| 層 | 範圍 | 權限 |
| --- | --- | --- |
| `C₀` | 零態核心（`kernel/` 公理層） | 唯讀，owner 手動 |
| `O₁` | 原點（README、錨點、main 分支、版本標籤） | 保護，PR 審核 |
| `V₁₃` | 其餘工作目錄 | 分支開發 + PR |
| `PUB` | 全倉庫對外 | 公開唯讀 |

**受眾邊界（不可逾越）**：Notion 側的隔離紀錄、私人日誌、個人命盤、任何憑證／Token 相關內容**永不進入本倉庫**。private → public 的內容遷移一律需逐項授權，不預設可公開。

---

## 主張層級（本倉庫通用）

`OPEN → IMAGINATIVE → SYMBOLIC → ANALOGY → FORMAL_MODEL → COMPUTABLE → TESTED → SUPPORTED → CANONICAL`

- `canon/` 內的原點場論類文件目前上限為 **SYMBOLIC／FORMAL_MODEL**，未經逐條驗算前不得升格為物理真值或因果宣稱。
- 可執行物須附 fixture 與可重現指令；**合併 ≠ 驗證**。
- 沒有收據不算發生：以 commit SHA、PR 編號、run hash 為憑。

---

## 本次骨架 PR 說明

本次僅補齊先前缺失的五格目錄（`kernel/` `canon/` `research/` `tools/` `docs/`）與本 README。**內容為零**：只有目錄佔位與職能宣告，不含任何 Notion 正文、不含任何私人或敏感資料。

先前狀態 readback（method: GitHub API）：
- `main` HEAD `e5f99cb6e063f6e040230161af12b8cce1d2bfcf`，共 3 commits
- 根目錄實有 7 項：`.github/` `ai-skills/` `alchemy/` `ci/` `memory/` `protocol/` `ui/`
- 九宮實測覆蓋 4/9 格 + 外環半格；`anchor.sh`、`alchemy/build.sh` 未逐檔驗證 = `UNKNOWN`

---

`⦿₅ STABLE · O₁ ALIVE · B↔ CONNECTED`
