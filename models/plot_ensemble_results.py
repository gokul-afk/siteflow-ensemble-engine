import json
import os
import matplotlib.pyplot as plt

# Helper to load model results from JSON files or direct output

def load_model_forecast(model_name, site_id):
    # Try to load from a file, fallback to running the model script
    script_path = os.path.join(os.path.dirname(__file__), f"forecast_{model_name}.py")
    import subprocess
    # Use absolute path to venv Python executable
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    python_exe = os.path.join(workspace_dir, 'venv', 'Scripts', 'python.exe')
    result = subprocess.run([
        python_exe, script_path, "--site_id", str(site_id)
    ], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data.get("error"):
            print(f"{model_name} error: {data['error']}")
            return None
        return data["forecast"]
    except Exception as e:
        print(f"Failed to parse {model_name} output: {e}")
        return None

def plot_ensemble(site_id):
    models = ["prophet", "sarima", "xgboost"]
    forecasts = {}
    for model in models:
        forecasts[model] = load_model_forecast(model, site_id)
    # Aggregate ensemble (average per date)
    dates = None
    ensemble = []
    for model, forecast in forecasts.items():
        if forecast:
            if dates is None:
                dates = [pt["date"] for pt in forecast]
    if not dates:
        print("No valid forecasts to plot.")
        return
    # Build per-model series
    import datetime
    plt.figure(figsize=(10,6))
    for model, forecast in forecasts.items():
        if forecast:
            values = [pt["value"] for pt in forecast]
            plt.plot(dates, values, marker='o', label=model)
    # Ensemble: average
    for i in range(len(dates)):
        vals = [forecasts[m][i]["value"] for m in models if forecasts[m]]
        if vals:
            ensemble.append(sum(vals)/len(vals))
        else:
            ensemble.append(None)
    plt.plot(dates, ensemble, marker='x', linestyle='--', color='black', label='ensemble')
    plt.xlabel('Date')
    plt.ylabel('Forecast Value')
    plt.title(f'Forecasts for Site {site_id}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Export to file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = "generated_forecasts"
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, f"forecast_comparisons_site_{site_id}_{timestamp}.png")
    plt.savefig(file_path)
    print(f"Plot saved to {file_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--site_id', type=int, required=True)
    args = parser.parse_args()
    plot_ensemble(args.site_id)
