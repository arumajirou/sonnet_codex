# /mnt/e/env/ts/sonnet_codex/Makefile (optimized)
# -----------------------------------------------
# 使い方: `make` でヘルプ。CI は `make ci` 一発。

.DEFAULT_GOAL := help
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PROJECT_ROOT := $(abspath .)

# ---- Python/Tools ------------------------------------------------------------
VENV ?= .venv
PY ?= python3
PIP ?= $(PY) -m pip
ifneq ("$(wildcard $(VENV)/bin/python)","")
  PY := $(VENV)/bin/python
  PIP := $(VENV)/bin/pip
endif

PYTEST ?= pytest
RUFF ?= ruff
BLACK ?= black
FLAKE8 ?= flake8
MYPY ?= mypy

# ---- Flags -------------------------------------------------------------------
PYTEST_ARGS ?= -q --maxfail=1 --disable-warnings \
               -k "not e2e and not slow" \
               --cov=src/nf_auto_runner --cov-report=term-missing
MYPY_ARGS ?= --strict src
RUFF_ARGS ?= check .
BLACK_ARGS ?= --check .

# ---- Optional: NF smoke ------------------------------------------------------
NF_SMOKE ?= 1
NF_SMOKE_ENTRY ?= nf_auto_runner_full.py

# ---- Codex（ヘッドレス運用） ---------------------------------------------------
CODEX ?= codex
CODEX_MODEL ?= gpt-5-codex
CODEX_SANDBOX ?= danger-full-access   # ネット許可含む
CODEX_APPROVAL ?= never
CODEX_INCLUDE_PLAN ?= true
CODEX_PROMPT ?= $(PROJECT_ROOT)/codex_prompt.txt

# Codex の状態/キャッシュ/データ書き先はワークスペース内に固定
CODEX_HOME       := $(PROJECT_ROOT)/.home
CODEX_STATE_HOME := $(PROJECT_ROOT)/.state
CODEX_CACHE_HOME := $(PROJECT_ROOT)/.cache
CODEX_DATA_HOME  := $(PROJECT_ROOT)/.data
CODEX_OUT_DIR    := $(PROJECT_ROOT)/.codex
CODEX_LAST       := $(CODEX_OUT_DIR)/last.txt

# ---- Targets -----------------------------------------------------------------
.PHONY: setup deps fmt lint typecheck lint-all test coverage verify ci smoke clean clean-all \
        help venv codex-setup codex-run codex-resume codex-tail codex-debug-net

help: ## 利用可能ターゲットを表示
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## ' $(MAKEFILE_LIST) | sed -e 's/:.*##/: /' | sort

venv: ## 仮想環境($(VENV))を作成し最低限のツール導入
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	$(PIP) install -U pip wheel setuptools
	$(PIP) install -U ruff black flake8 mypy pytest pytest-cov

setup: ## pip / setuptools / wheel の安全アップグレード
	$(PIP) install -U pip wheel setuptools

deps: ## 開発系依存（ruff/black/flake8/mypy/pytest/coverage）を導入
	$(PIP) install -U ruff black flake8 mypy pytest pytest-cov

fmt: ## 自動整形（ruff --fix + black）
	$(RUFF) check --fix .
	$(BLACK) .

lint: ## 静的検査（ruff + black --check）
	$(RUFF) $(RUFF_ARGS)
	$(BLACK) $(BLACK_ARGS)

typecheck: ## 型検査（mypy --strict）
	$(MYPY) $(MYPY_ARGS)

lint-all: lint typecheck ## ruff/black + mypy + flake8
	$(FLAKE8)

test: ## ユニットテスト（速い・カバレッジ表示）
	$(PYTEST) $(PYTEST_ARGS)

coverage: ## カバレッジの XML/HTML レポート生成
	$(PYTEST) -q --cov=src/nf_auto_runner --cov-report=xml --cov-report=html
	@echo "coverage: coverage.xml / htmlcov/index.html を確認"

verify: ## プロジェクト独自の検証
	@export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1; \
	 export PYTEST_ADDOPTS="-p pytest_cov"; \
	 ./scripts/verify.sh

ci: ## CIゲート（lint→test→verify）
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) verify

smoke: ## (任意) NF最小スモーク。ファイルが無ければスキップ
	@if [ "$(NF_SMOKE)" = "1" ] && [ -f "$(NF_SMOKE_ENTRY)" ]; then \
		echo "[NF] smoke: $(PY) $(NF_SMOKE_ENTRY)"; \
		$(PY) $(NF_SMOKE_ENTRY); \
	else \
		echo "[NF] smoke: skipped (NF_SMOKE=$(NF_SMOKE), entry=$(NF_SMOKE_ENTRY))"; \
	fi

# ---- Codex 操作用ユーティリティ ----------------------------------------------
codex-setup: ## Codex の作業用ディレクトリ作成（HOME/XDG をワークスペースへ固定）
	mkdir -p "$(CODEX_HOME)" "$(CODEX_STATE_HOME)" "$(CODEX_CACHE_HOME)" "$(CODEX_DATA_HOME)" "$(CODEX_OUT_DIR)"

codex-run: codex-setup ## Codex 新規実行（ヘッドレス・全自動）
	@env HOME="$(CODEX_HOME)" \
	    XDG_STATE_HOME="$(CODEX_STATE_HOME)" \
	    XDG_CACHE_HOME="$(CODEX_CACHE_HOME)" \
	    XDG_DATA_HOME="$(CODEX_DATA_HOME)" \
	$(CODEX) -s $(CODEX_SANDBOX) -a $(CODEX_APPROVAL) \
	  -c include_plan_tool=$(CODEX_INCLUDE_PLAN) \
	  -C "$(PROJECT_ROOT)" \
	  exec --full-auto -m $(CODEX_MODEL) \
	  --json --output-last-message "$(CODEX_LAST)" \
	  - < "$(CODEX_PROMPT)"

codex-resume: codex-setup ## Codex 直前セッションを再開（ヘッドレス）
	@env HOME="$(CODEX_HOME)" \
	    XDG_STATE_HOME="$(CODEX_STATE_HOME)" \
	    XDG_CACHE_HOME="$(CODEX_CACHE_HOME)" \
	    XDG_DATA_HOME="$(CODEX_DATA_HOME)" \
	printf '続行' | $(CODEX) \
	  -s $(CODEX_SANDBOX) -a $(CODEX_APPROVAL) \
	  -C "$(PROJECT_ROOT)" \
	  exec resume --last

codex-tail: ## Codex 最終メッセージを tail
	@test -f "$(CODEX_LAST)" || { echo "no $(CODEX_LAST)"; exit 1; }
	tail -f "$(CODEX_LAST)"

codex-debug-net: ## seatbelt 越しにネット到達をチェック（HTTPコード表示）
	$(CODEX) debug seatbelt --full-auto -- bash -lc "curl -sS -o /dev/null -w '%{http_code}\n' https://api.openai.com"

clean: ## キャッシュとカバレッジ成果物の掃除
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov

clean-all: clean ## 追加で NF/Codex 一時成果を掃除
	rm -rf nf_auto_runs/tmp || true
	rm -rf "$(CODEX_HOME)" "$(CODEX_STATE_HOME)" "$(CODEX_CACHE_HOME)" "$(CODEX_DATA_HOME)" "$(CODEX_OUT_DIR)" || true
# 追記例
.PHONY: codex-auth
codex-auth:
	@test -n "$$OPENAI_API_KEY" || { echo "OPENAI_API_KEY が未設定"; exit 1; }
	$(CODEX) login --api-key "$$OPENAI_API_KEY"

