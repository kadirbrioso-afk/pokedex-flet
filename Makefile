.PHONY: install run test lint typecheck sync

install:
	uv sync

sync:
	uv sync

run:
	uv run python main.py

test:
	uv run pytest

lint:
	uv run ruff check .

typecheck:
	uv run mypy app