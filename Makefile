# Makefile for SiteFlow Ensemble Engine data commands
# This Makefile automates environment setup, data transformation, and running services for a multi-language project.

.PHONY: setup-env activate-env download-data
# .PHONY declares targets that aren't actual files, ensuring commands always run.


# PYTHON_ENV variable defines the name of the Python virtual environment directory.
PYTHON_ENV=venv

# Detect OS and set Python executable path
ifeq (,$(findstring Windows_NT,$(OS)))
	PYTHON_BIN=$(PYTHON_ENV)/bin/python
	PIP_BIN=$(PYTHON_ENV)/bin/pip
	ACTIVATE=. $(PYTHON_ENV)/bin/activate
	SEP=/
else
	PYTHON_BIN=$(PYTHON_ENV)\Scripts\python.exe
	PIP_BIN=$(PYTHON_ENV)\Scripts\pip.exe
	ACTIVATE=$(PYTHON_ENV)\Scripts\activate
	SEP=\
endif
endif


setup-env:
	python -m venv $(PYTHON_ENV)
	@echo "Python venv created at $(PYTHON_ENV)"


activate-env:
	$(PIP_BIN) install -r requirements.txt
	@echo "Python dependencies installed from requirements.txt."


setup-all:
	$(MAKE) setup-env
	$(MAKE) activate-env
	cd api-gateway && npm install
	cd orchestrator && go mod tidy
	@echo "All environments and dependencies are set up."


transform-data:
	$(PYTHON_BIN) scripts$(SEP)transform_kaggle_dataset.py


run:
	go run orchestrator/main.go orchestrator/executor.go orchestrator/aggregator.go


gateway:
	node api-gateway/server.js


run-prophet:
	$(PYTHON_BIN) models$(SEP)forecast_prophet.py --site_id 1


run-sarima:
	$(PYTHON_BIN) models$(SEP)forecast_sarima.py --site_id 1


plot:
	$(PYTHON_BIN) models$(SEP)plot_ensemble_results.py --site_id 1