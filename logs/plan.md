# Codex Auto Plan — 2025-11-05

## Context Reviewed
- `doc/04_CLASS_DESIGN_DETAILED.md#L1180`–`#L1579` — ModelSelectionConfig specification & test contract.
- `doc/04_CLASS_DESIGN_DETAILED.md#L1587`–`#L2069` — ConfigLoader responsibilities and behaviours.
- Existing implementations: `src/nf_auto_runner/config/{base,execution,path}.py` and unit tests under `tests/unit/config/`.
- Open points: none blocking (checked `sonnet_codex_headless_pack/OPEN_POINTS.md`).

## Task Breakdown
1. **ModelSelectionConfig implementation**
   - Create `src/nf_auto_runner/config/model_selection.py` per spec (env parsing, validation, helper accessors).
   - Expose in `src/nf_auto_runner/config/__init__.py`.
   - Add targeted unit coverage (`tests/unit/config/test_model_selection.py`).

2. **ConfigLoader orchestration**
   - Implement loader utility that materialises Path/Execution/ModelSelection configs from env or JSON.
   - Support `load_all`, `load_from_file`, `merge_configs`, `validate_all`, `get`, `save_all`.
   - Add comprehensive tests (`tests/unit/config/test_loader.py`) mirroring doc expectations.

3. **Verification & documentation**
   - Run `make lint`, `make test`, `make verify`; capture outcomes.
   - Update `logs/summary.md` with changes, doc anchors, and follow-ups.
