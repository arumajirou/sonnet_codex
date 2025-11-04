# AGENTS.md — Headless Codex Playbook (JP/EN)

## Mission / 目的
- Run **non-interactively** (headless) via `codex exec` and finish without human prompts.
- Obey docs under `./doc/` as the **single source of truth**.
- Never guess requirements. If uncertain, **do not implement**; record in `OPEN_POINTS.md`.

## Repository Contracts / リポの前提
- Source: `src/`, Tests: `tests/`, Docs: `doc/`, Artifacts: `nf_auto_runs/`（models/logs/artifacts/checkpoints, plots）.
- PathConfig/env: `NF_OUTPUT_DIR`, `NF_LOG_DIR`, `NF_MODEL_DIR`, `NF_ARTIFACT_DIR`, `NF_CHECKPOINT_DIR`, `NF_PLOT_DIR`.
- Python 3.11, CUDA 13, Torch 2.10 dev (GPU available). Prefer `accelerator=auto`.

## Verification — the **only acceptance** / 検証（唯一の合格基準）
Run these exactly (locally or in CI). If green, the task is **done**:
```bash
make setup          # optional when first run
make lint           # ruff/black/flake8/mypy (pylint optional)
make test           # pytest (unit+selected integration), coverage gate
make verify         # wraps lint+test and fast GPU smoke
```
- Coverage gates: unit ≥ 90% for `src/nf_auto_runner` (see `tests/unit`).
- Logs and artifacts must be written under `nf_auto_runs/` with run_id.

## Change Policy / 変更方針
- **Minimal diffs only**. No unrelated refactors or reformat-only commits.
- Keep backward compatibility. For API/DB, use **versioning** and **expand → migrate → contract**.
- Commit messages: Conventional Commits + short rationale, and **doc citation** lines, e.g.:
  - `Refs: doc/06_API_DESIGN_DETAILED.md#PATCH-users`
  - `Impact: no schema change`

## When Uncertain / 不明点の扱い
- Do not implement speculative behavior.
- Append to `OPEN_POINTS.md`:
  - **Question**, **Related files/sections**, **Safe interim behavior** (default-off, no-op, or explicit error).

## GPU / メモリ・GPU
- Prefer `accelerator="auto"`; keep batch sizes conservative in smoke tests.
- Do **not** change global CUDA env. For memory pressure, use per-run knobs (precision=16, gradient_accumulation).

## Security / セキュリティ
- Never introduce new secrets or outbound network usage.
- PII must not be logged. Use structured logs under `nf_auto_runs/logs`.

## Done Definition / 完了の定義
- `make verify` green.
- Minimal diff, rationale in commit body, docs cross-reference.
- If anything blocked: `OPEN_POINTS.md` updated and linked from commit body.
