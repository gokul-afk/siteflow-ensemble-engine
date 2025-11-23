# SiteFlow Ensemble Engine


# SiteFlow Ensemble Engine

## Example Forecast Comparison

![Forecast Comparison Example](generated_forecasts/sample.png)

## Overview

SiteFlow Ensemble Engine is a polyglot forecasting system for construction sites, designed to showcase senior-level architecture and ensemble modeling. Built for Sitemate’s “Jack of all trades” requirement, it demonstrates how to combine Node.js, Go, and Python for scalable, maintainable, and extensible solutions.

## Features

- **Polyglot Architecture:** Node.js API Gateway, Go Orchestrator, Python Models.
- **Ensemble Modeling:** Combines Prophet, SARIMA, and XGBoost forecasts for robust predictions.
- **Concurrency:** Go orchestrator runs Python models in parallel for speed.
- **Extensibility:** Easily add new models or swap orchestration logic.
- **Demo-Ready Visualization:** Automatically generates and saves forecast comparison plots.

## Production Readiness & Trade-offs

Current Approach (MVP): This demo uses shell execution (exec.Command) to spawn Python processes. This was chosen for simplicity, isolation, and ease of deployment—aligning with the "make it work" phase of startup engineering.

Production Strategy (Scaling): In a high-load production environment, spawning a new Python interpreter for every request introduces unacceptable latency. To scale this, I would refactor the architecture:

Persistent Workers: Convert the Python scripts into a long-running gRPC Microservice.

Protocol Buffers: Use Protobuf for strictly typed, high-performance communication between the Go Orchestrator and Python Workers.

Message Queue: Introduce RabbitMQ or SQS if the forecasting jobs become long-running/async tasks.

## Architecture

```
siteflow-ensemble-engine/
├── api-gateway/        # Node.js API Gateway
│   ├── server.js
│   └── package.json
├── orchestrator/       # Go Orchestrator
│   ├── main.go
│   ├── executor.go
│   └── aggregator.go
├── models/             # Python Models
│   ├── forecast_prophet.py
│   ├── forecast_sarima.py
│   ├── forecast_xgboost.py
│   ├── plot_ensemble_results.py
│   └── requirements.txt
├── data/               # Construction Data
│   └── site_materials_usage.csv
├── generated_forecasts/ # Saved forecast comparison images
│   └── forecast_comparisons_site_1_YYYYMMDD_HHMMSS.png
└── README.md
```

## How It Works

1. **User/API** sends a forecast request to Node.js (`/api-gateway`).
2. **Node.js** forwards the request to Go orchestrator (`/orchestrator`).
3. **Go** launches Python model workers in parallel (`/models`).
4. **Python** scripts run forecasts and return JSON.
5. **Go** aggregates results (ensemble logic) and returns to Node.js.
6. **Node.js** responds to the user.

## Quickstart

## Supported Operating Systems

This project is cross-platform and works on Windows, Linux, and macOS. The Makefile automatically detects your OS and sets up paths accordingly.

## Go Dependency Installation

Go dependencies are installed automatically when you run:

```powershell
make setup-all
```
This runs `go mod tidy` in the `orchestrator` directory to fetch all required Go modules.

## Troubleshooting

- **Makefile errors:** Ensure you are using GNU Make (not nmake or other variants). If you see 'missing endif' or 'extraneous else', check for stray lines or encoding issues at the top of the Makefile.
- **Missing dependencies:** Always run `make setup-all` before running other targets to ensure all Python, Node.js, and Go dependencies are installed.
- **Plot image not showing in README:** Make sure the image file exists in `generated_forecasts/` and the path in the README matches the latest file name.

## Updating the Plot Image in README

After running `make plot`, a new PNG image is saved in the `generated_forecasts` folder. To display the latest image in your README, update the image link to match the newest file name, e.g.:

```markdown
![Forecast Comparison Example](generated_forecasts/forecast_comparisons_site_1_YYYYMMDD_HHMMSS.png)
```

## Key Makefile Commands

Use these Makefile targets for a fast, repeatable workflow:

- **setup-all**: Sets up Python venv, installs Python dependencies, and Node.js dependencies for the API gateway.
	```powershell
	make setup-all
	```
- **run**: Runs the Go orchestrator (executes all models and ensemble logic).
	```powershell
	make run
	```
- **gateway**: Starts the Node.js API gateway server.
	```powershell
	make gateway
	```
- **plot**: Generates and saves the ensemble forecast comparison plot for site_id 1.
	```powershell
	make plot
	```

### 1. Install Python dependencies

```powershell
python -m venv venv
.\venv\Scripts\pip install -r models/requirements.txt
```

### 2. Run the Go orchestrator

```powershell
make run
```

### 3. Start the API Gateway

```powershell
cd api-gateway
npm install
node server.js
```

### 4. Request a forecast

```powershell
curl "http://localhost:3000/forecast?site_id=1"
```

### 5. Generate and view forecast comparison plot

```powershell
venv\Scripts\python models/plot_ensemble_results.py --site_id 1
```
Find the generated image in `generated_forecasts/`.


## OpenAPI Documentation

The API gateway exposes a `/forecast` endpoint for ensemble forecasting. The OpenAPI specification is provided in `openapi.yaml`.

You can view and interact with the API documentation using tools like [Swagger Editor](https://editor.swagger.io/) or [Redoc](https://redocly.com/):

1. Open `openapi.yaml` in Swagger Editor or Redoc.
2. Try out the `/forecast` endpoint by providing a `site_id` query parameter.

**Example OpenAPI Spec:**

```yaml
openapi: 3.0.0
info:
	title: SiteFlow Ensemble Engine API
	version: 1.0.0
	description: API for ensemble forecasting of construction sites.
servers:
	- url: http://localhost:3000
paths:
	/forecast:
		get:
			summary: Get ensemble forecast for a construction site
			parameters:
				- name: site_id
					in: query
					required: true
					schema:
						type: integer
					description: Site ID for which to generate the forecast
			responses:
				'200':
					description: Successful forecast response
					content:
						application/json:
							schema:
								type: object
								properties:
									site_id:
										type: integer
									forecasts:
										type: array
										items:
											type: object
											properties:
												model:
													type: string
												prediction:
													type: number
									ensemble:
										type: number
				'400':
					description: Invalid request
				'500':
					description: Internal server error
```
## Data Format Example

```
date,material,units_consumed,site_id
2024-01-01,cement,500,1
2024-01-02,cement,520,1
...
```

## License

MIT

