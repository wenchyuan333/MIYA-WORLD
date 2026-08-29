# tools/CI-SETUP.md

MIYA-WORLD 接 CI 的手續。

## 為何需要

`tools/README.md` 明載：

```
仍無 CI；所有 exit 0 都是人工在協作者手機上跑出來的。
```

這代表綿燈的信任基礎是「有人記得跑」。接上 CI 之後，
基礎改成「每次 push 都跑」。

---

## 阿厄：Miya 推不了 workflow 檔

實測錯誤（verbatim）：

```
failed to create tree: POST /repos/wenchyuan333/MIYA-WORLD/git/trees
403 Resource not accessible by integration
```

原因：`.github/workflows/` 屬於獨立權限範圍。
fine-grained PAT 只勾 Contents Read/Write 不夠，還要 **Workflows Read/Write**。

這不是 bug。這是 GitHub 刻意的隔隷：
能寫檔案 != 能寫自動執行的程式。這個隔隷是對的，不要綁它。

所以 workflow 檔必須由倉庫擁有者亲自落地。下面是完整內容。

---

## 步驟一：建 workflow 檔

在本機：

```
cd ~/miya-check
mkdir -p .github/workflows
nano .github/workflows/verify.yml
```

貼入：

```yaml
name: verify

on:
  push:
    branches:
      - main
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  fixtures:
    name: fixtures
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "3.11"
          - "3.12"
          - "3.13"
    steps:
      - name: checkout
        uses: actions/checkout@v4

      - name: setup python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: python receipt
        run: python3 -VV

      - name: no third-party imports allowed
        run: |
          if grep -rnE "^[[:space:]]*(import|from)[[:space:]]+(numpy|scipy|sympy|pandas|numba|matplotlib)" tools/ ; then
            echo "FAIL: fixture must not depend on third-party packages."
            exit 1
          fi
          echo "OK: no third-party imports in tools/"

      - name: run all fixtures
        env:
          PYTHONIOENCODING: utf-8
          PYTHONUTF8: "1"
        run: python3 tools/verify_all.py
```

### 三版 Python matrix 的理由

所有 fixture 都是純標準庫的有限場與整數運算。
若結果隨 Python 版本漂移，那就不是數學結論，是實作巧合。
跑三版是在驗這一點。

### 第三方 import 閘的理由

`AUDIT V10-001` 的 V1 致命缺陷就是 `np.random.seed()` 管不到
`@njit` 的 Numba RNG。任何引入第三方隨機源或 JIT 的 fixture
都有同類風險。這道閘是把那次教訓寫成規則。

---

## 步驟二：推上去

⚠ `git push` 推 workflow 檔也需要 PAT 有 Workflows 權限。
若被拒，到 GitHub Settings -> Developer settings ->
Personal access tokens -> 選該 token -> Repository permissions ->
把 **Workflows** 設為 Read and write，存檔後重試。

```
cd ~/miya-check
git add .github/workflows/verify.yml
git commit -m "ci: enable fixture verification workflow"
git push origin main
```

---

## 步驟三：確認 Actions 已啟用

倉庫頁 -> Actions 分頁。若顯示停用，點 Enable。
首次執行應在 push 後數十秒内出現。

---

## 預期結果

目前已在 `main` 且已確認 exit 0 的 fixture：

| fixture | 使用者實測 |
| --- | --- |
| verify_luoshu_constants.py | exit 0 |
| verify_v13_pairing.py | exit 0 |
| verify_bijection_b13.py | exit 0 |
| verify_pg23_candidate.py | 47 PASS / 0 FAIL / 5 SKIP，exit 0 |
| verify_palindrome_structure.py | 51 PASS / 0 FAIL / 6 SKIP，exit 0 |
| verify_quaternion_f3.py | 0 FAIL / 6 SKIP，exit 0 |

全部已知綿。所以 CI 一上應當場就是綿的。

**先用必然成功的案例把通道打通，再回頭處理別人的紅燈。**
若 CI 第一次就紅，就不知道是環境錯還是 fixture 錯。

---

## 不在本文範圍

- branch protection（required status checks）—— 須 owner 在 UI 手動設，API 碰不到
- pre-push git hook（本機先跑再推）—— `.git/hooks/` 不在版控內，須手建
- integrity anchor（關鍵檔案的 blob SHA-1 pin）—— 可行但未建

這三項在 `wenchyuan333/luoshu-terminal` 已有實作（commit `d2f1097`、
`b47d23d`、`ab1962f`）。可直接移植，不需重新設計。
