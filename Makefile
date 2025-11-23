
# Makefile for SiteFlow Ensemble Engine data commands

.PHONY: setup-env activate-env download-data

PYTHON_ENV=venv

setup-env:
	python -m venv $(PYTHON_ENV)
	@echo "Python venv created at $(PYTHON_ENV)"

activate-env:
	powershell -ExecutionPolicy Bypass -File activate_and_install.ps1

transform-data:
	$(PYTHON_ENV)\Scripts\python scripts/transform_kaggle_dataset.py

run:
	go run orchestrator/main.go orchestrator/executor.go orchestrator/aggregator.go

run-prophet:
	$(PYTHON_ENV)\Scripts\python models/forecast_prophet.py --site_id 1

run-sarima:
	$(PYTHON_ENV)\Scripts\python models/forecast_sarima.py --site_id 1