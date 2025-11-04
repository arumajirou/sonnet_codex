# OPEN_POINTS

| ID | Question / 不明点 | Affected files/sections | Proposed safe interim behavior | Notes |
|----|--------------------|-------------------------|---------------------------------|-------|
| OP-001 | Should `confidence_level` be exposed in API v1? | doc/06_API_DESIGN_DETAILED.md, src/... | Keep internal only; default 0.95; no API field | To be decided by PO |
| OP-CLI-001 | CLI specification mismatch between `nf_auto_runner.runners.main` and `tsl.cli.main train-one` | AGENTS.md §Verification, doc/11_OPERATIONS_RUNBOOK.md §Launch Sequence | Defer CLI implementation; keep training runs disabled; ensure `make verify` remains green until spec clarified | 2025-11-05: Revalidated; design docs still lack `train-one` contract and `src/nf_auto_runner/runners/main.py` absent. |
