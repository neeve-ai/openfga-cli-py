SHELL  := /bin/bash
.DEFAULT_GOAL := help

# ── Paths ──────────────────────────────────────────────────────────────────
VENV      := .venv
PRECOMMIT := $(VENV)/bin/pre-commit

.PHONY: help setup install quality

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { \
		printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ── setup ────────────────────────────────────────────────────────────

setup: $(PRECOMMIT) ## Create .venv with pre-commit
	@echo "✓ All tools ready  [pre-commit]"

$(PRECOMMIT):
	@echo "→ Creating virtualenv and installing pre-commit..."
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet pre-commit
	@echo "✓ pre-commit ready"

# ── install ──────────────────────────────────────────────────────────

install: setup ## Install pre-commit hooks and package
	$(PRECOMMIT) install
	$(PRECOMMIT) install --hook-type prepare-commit-msg
	@echo "✓ pre-commit hooks installed"
	$(VENV)/bin/pip install setuptools wheel setuptools-download pytest
	$(VENV)/bin/pip install . --no-build-isolation
	@echo "✓ package installed"

# ── quality ──────────────────────────────────────────────────────────

quality: install ## Run tests and build wheel
	$(VENV)/bin/fga version
	$(VENV)/bin/fga help
	$(VENV)/bin/pip install --quiet pytest
	$(VENV)/bin/pytest tests/
	$(VENV)/bin/pip wheel --no-deps --no-build-isolation --wheel-dir dist .
