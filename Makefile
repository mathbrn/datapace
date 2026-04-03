# ╔══════════════════════════════════════╗
# ║        DataPace — Makefile           ║
# ╚══════════════════════════════════════╝

.PHONY: install test lint dashboard migrate clean help

# ── Setup ─────────────────────────────────
install: ## Installe les dependances
	pip install -r requirements.txt

# ── Database ──────────────────────────────
migrate: ## Migre les donnees Excel/JSON vers SQLite
	python migrate_to_db.py

# ── Dashboard ─────────────────────────────
dashboard: ## Genere le dashboard HTML
	python generate_dashboard.py

# ── Tests ─────────────────────────────────
test: ## Lance tous les tests
	python -m pytest tests/ -v --tb=short

test-cov: ## Lance les tests avec couverture
	python -m pytest tests/ -v --cov=datapace --cov-report=term-missing

# ── Quality ───────────────────────────────
lint: ## Verifie le style du code
	python -m py_compile datapace/config.py
	python -m py_compile datapace/models.py
	python -m py_compile datapace/database.py
	python -m py_compile generate_dashboard.py
	python -m py_compile migrate_to_db.py
	@echo "All files compile OK"

# ── Crawlers ──────────────────────────────
crawl-sporthive: ## Lance le crawler Sporthive
	python crawl_sporthive.py

crawl-tracx: ## Lance le crawler Tracx
	python crawl_tracx.py

crawl-athlinks: ## Lance le crawler Athlinks
	python crawl_athlinks.py

aggregate: ## Fusionne toutes les sources
	python aggregate_all.py

# ── Full pipeline ─────────────────────────
all: install test migrate dashboard ## Pipeline complet
	@echo "Pipeline complet termine."

# ── Clean ─────────────────────────────────
clean: ## Nettoie les fichiers temporaires
	rm -rf __pycache__ datapace/__pycache__ tests/__pycache__
	rm -rf .pytest_cache
	rm -f *.pyc

# ── Help ──────────────────────────────────
help: ## Affiche l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
