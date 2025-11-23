## Example Forecast Comparison

After running the ensemble plot script, a PNG image is saved in the `generated_forecasts` folder. You can display the latest generated image in your README like this:

```
![Forecast Comparison Example](generated_forecasts/forecast_comparisons_site_1_YYYYMMDD_HHMMSS.png)
```

Replace `YYYYMMDD_HHMMSS` with the actual timestamp from your generated file.

For example, if your file is `forecast_comparisons_site_1_20251123_153045.png`, use:

```
![Forecast Comparison Example](generated_forecasts/forecast_comparisons_site_1_20251123_153045.png)
```

This will embed the forecast comparison image directly in your README for demo or documentation purposes.

# SiteFlow Ensemble Engine

## Overview

A polyglot forecasting engine for construction sites, designed to showcase senior-level systems architecture and ensemble modeling. Built for Sitemate's "Jack of all trades" requirement, this project demonstrates how to combine Node.js, Go, and Python for a scalable, maintainable, and extensible solution.

---

## Architecture

```
siteflow-ensemble-engine/
├── api-gateway/        # Node.js API Gateway (The Face)
│   ├── server.js
│   └── package.json
├── orchestrator/       # Go Orchestrator (The Muscle)
│   ├── main.go
│   ├── executor.go
│   └── aggregator.go
├── models/             # Python Models (The Brain)
│   ├── forecast_prophet.py
│   ├── forecast_sarima.py
│   └── requirements.txt
├── data/               # Construction Data
│   └── site_materials_usage.csv
└── README.md
```

- **Node.js**: The Site Manager (friendly, speaks HTTP)
- **Go**: The Foreman (fast, coordinates workers)
- **Python**: The Specialist (smart, does the math)

---

## Workflow Visualization

1. **User/API** sends a forecast request to Node.js (`/api-gateway`).
2. **Node.js** forwards the request to Go orchestrator (`/orchestrator`).
3. **Go** launches Python model workers in parallel (`/models`).
4. **Python** scripts run forecasts and return JSON.
5. **Go** aggregates results (ensemble logic) and returns to Node.js.
6. **Node.js** responds to the user.

---

## Why This Architecture Wins

- **Migration-Friendly**: Keeps legacy Node.js, adds Go for orchestration, Python for AI.
- **Ensemble Modeling**: Runs multiple models (Prophet, SARIMA) and averages results for robustness.
- **Go Concurrency**: Uses goroutines and WaitGroup for parallel execution.
- **Extensible**: Easy to add new models or swap orchestration logic.

---

## Senior Engineer Defense

> "For this demo, I used shell execution for simplicity and isolation. In production, I'd refactor Python into a gRPC microservice, with Go sending protobuf messages to persistent Python workers—avoiding interpreter startup latency. This architecture demonstrates Go's concurrency and is easy to deploy for a proof-of-concept."

---

## Setup & Run

1. **Install Python dependencies:**
	```powershell
	python -m venv venv
	.\venv\Scripts\pip install -r models/requirements.txt
	```
2. **Run the orchestrator:**
	```powershell
	make run
	```
3. **Test the API:**
	```powershell
	curl "http://localhost:8080/forecast?site_id=1"
	```

---

## Data Format Example

```
date,material,units_consumed,site_id
2024-01-01,cement,500,1
2024-01-02,cement,520,1
...
```

---

## Extending the System

- Add new Python models to `/models` and update Go orchestrator to include them.
- Refactor Python scripts into a microservice for production.
- Add OpenAPI docs to Node.js gateway for better API usability.

---

## License

MIT
