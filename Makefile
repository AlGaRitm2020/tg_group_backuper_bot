# В README как пользоваться

VENV = .venv

# === Локальная разработка ===

.PHONY: venv
venv:
	uv venv $(VENV)

.PHONY: sync
sync:
	uv sync

.PHONY: dev
dev: venv sync
	$(VENV)/bin/python -m app.main

# === Docker ===

.PHONY: build
build:
	docker compose build

.PHONY: up
up:
	docker compose up -d

.PHONY: down
down:
	docker compose down

.PHONY: logs
logs:
	docker compose logs -f

# === Другое ===

.PHONY: clean
clean:
	rm -rf $(VENV) .ruff_cache
