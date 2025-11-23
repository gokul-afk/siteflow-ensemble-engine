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


setup-env:
	python -m venv $(PYTHON_ENV)
	@echo "Python venv created at $(PYTHON_ENV)"
	# Creates a Python virtual environment and prints its location.


activate-env:
	$(PIP_BIN) install -r requirements.txt
	@echo "Python dependencies installed from requirements.txt."
	# Installs Python dependencies using pip in the virtual environment.


setup-all:
	$(MAKE) setup-env
	$(MAKE) activate-env
	cd api-gateway && npm install
	@echo "All environments and dependencies are set up."
  # Runs Python venv setup, installs Python dependencies, and Node.js dependencies for API gateway.


transform-data:
	$(PYTHON_BIN) scripts$(SEP)transform_kaggle_dataset.py
	# Runs the Python script to transform the Kaggle dataset using the virtual environment's Python interpreter.


run:
	go run orchestrator/main.go orchestrator/executor.go orchestrator/aggregator.go
	# Runs the Go application by executing multiple source files.


gateway:
	node api-gateway/server.js
	# Starts the Node.js API gateway server.


run-prophet:
	$(PYTHON_BIN) models$(SEP)forecast_prophet.py --site_id 1
	# Runs the Prophet forecasting model for site_id 1 using Python from the virtual environment.


run-sarima:
	$(PYTHON_BIN) models$(SEP)forecast_sarima.py --site_id 1
	# Runs the SARIMA forecasting model for site_id 1 using Python from the virtual environment.


plot:
	$(PYTHON_BIN) models$(SEP)plot_ensemble_results.py --site_id 1
	# Plots the ensemble results for site_id 1 using Python from the virtual environment.