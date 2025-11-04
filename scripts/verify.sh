#!/usr/bin/env bash
set -euo pipefail

echo "[verify] lint..."
ruff check .
black --check .
flake8
mypy --strict src

echo "[verify] tests..."
pytest -q --maxfail=1 --disable-warnings \
  --cov=src/nf_auto_runner --cov-report=term-missing \
  -k "not e2e and not slow"

echo "[verify] gpu smoke..."
python - <<'PY'
import torch
print("cuda_available:", torch.cuda.is_available())
if torch.cuda.is_available():
    x=torch.rand(1024,1024,device="cuda"); y=x@x; print("smoke:", float(y.norm().item()))
PY

echo "[verify] OK"
