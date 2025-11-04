.PHONY: setup lint test verify clean

PY=python
PIP=pip

setup:
	$(PIP) install -U pip

lint:
	ruff check .
	black --check .
	flake8
	mypy --strict src

test:
	pytest -q --maxfail=1 --disable-warnings \
	  --cov=src/nf_auto_runner --cov-report=term-missing \
	  -k "not e2e and not slow"

verify:
	./scripts/verify.sh

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
