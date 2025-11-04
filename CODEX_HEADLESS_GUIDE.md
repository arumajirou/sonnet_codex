# Codex Headless Guide (CLI-only)

このガイドは **対話なし (headless)** で `codex exec` を用いて安全に開発を完走させるための最小手順を示します。

## One-line run
```bash
codex exec "
Use AGENTS.md. Implement the next task according to ./doc.
1) Apply minimal changes. 2) run: make verify 3) iterate until green.
If uncertain, update OPEN_POINTS.md and stop. Cite doc anchors in commit message."
```

## Typical tasks
- **Small API change**  
  「`doc/06_API_DESIGN_DETAILED.md#patch-users` を満たす PATCH `/api/v1/users` を追加。テスト更新後 `make verify`」

- **Config/Path**  
  「`NF_*` 環境変数を PathConfig で尊重し、artifacts を `nf_auto_runs/` に統一保存。ユニットテスト追加」

- **Prediction artifact**  
  「`doc/05_DATABASE_DESIGN_DETAILED.md` のスキーマに従い `predictions.csv` のヘッダ/型を検証するテストを追加」

## Review checklist (for humans)
- 最小差分か？
- コミット本文に **doc の参照アンカー**が列挙されているか？
- `make verify` の結果（緑）が記録されているか？
- 不明点は `OPEN_POINTS.md` に分離されているか？
