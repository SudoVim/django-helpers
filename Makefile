POETRY_RUN = poetry run

.PHONY: pyright
pyright:
	$(POETRY_RUN) basedpyright --warnings

.PHONY: ruff-check
ruff-check:
	$(POETRY_RUN) ruff check

.PHONY: lint
lint: ruff-check pyright

.PHONY: format
format:
	$(POETRY_RUN) ruff check --select I
	$(POETRY_RUN) ruff format

.PHONY: ci
ci: format lint
