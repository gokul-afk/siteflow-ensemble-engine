

import argparse
import json
import sys
import os
import pandas as pd
import numpy as np
from prophet import Prophet
import logging
import traceback

# Configure logging to stderr so stdout remains pure JSON
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='[%(levelname)s] %(message)s')

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------
class SuppressStdout:
	"""Context manager to suppress Prophet's C++ logs"""
	def __enter__(self):
		self._original_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')

	def __exit__(self, exc_type, exc_val, exc_tb):
		sys.stdout.close()
		sys.stdout = self._original_stdout

# Disable Prophet's cmdstanpy logger
logger = logging.getLogger('cmdstanpy')
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.CRITICAL)

def get_data_path():
	"""Finds the CSV file relative to this script location"""
	# Get the directory where this script is located (models/)
	script_dir = os.path.dirname(os.path.abspath(__file__))
	# Go up one level and into data/ (../data/site_materials_usage.csv)
	return os.path.join(script_dir, '..', 'data', 'site_materials_usage.csv')

def get_mock_data():
	"""Fallback if CSV is missing"""
	dates = pd.date_range(end=pd.Timestamp.now(), periods=60)
	values = 100 + np.random.normal(0, 10, size=60)
	return pd.DataFrame({'ds': dates, 'y': values})

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------
def run_prophet(site_id):
	csv_path = get_data_path()
    
	if os.path.exists(csv_path):
		logging.info(f"Prophet: found CSV at {csv_path}")
		df = pd.read_csv(csv_path)
		logging.info(f"Prophet: loaded CSV, shape={df.shape}")
		# Rename columns for Prophet (ds, y)
		df = df.rename(columns={'date': 'ds', 'units_consumed': 'y'})
		# Filter by site_id if your CSV has it
		if 'site_id' in df.columns:
			df = df[df['site_id'] == site_id]
			logging.info(f"Prophet: filtered by site_id={site_id}, rows={len(df)}")
	else:
		logging.warning(f"Prophet: CSV not found at {csv_path}, using mock data")
		df = get_mock_data()

	# Train Model (Silence Output of Prophet internals)
	try:
		logging.info("Prophet: starting model fit")
		with SuppressStdout():
			m = Prophet(daily_seasonality=True, yearly_seasonality=False)
			m.fit(df)
			future = m.make_future_dataframe(periods=7)
			forecast = m.predict(future)
		logging.info(f"Prophet: model fit complete, forecast rows={len(forecast)}")
	except Exception as e:
		logging.error("Prophet: exception during model fit")
		traceback.print_exc(file=sys.stderr)
		raise

	# Format Output
	output = []
	# Take only the last 7 days (the future prediction)
	future_days = forecast.tail(7)
    
	for _, row in future_days.iterrows():
		output.append({
			"date": row['ds'].strftime('%Y-%m-%d'),
			"value": round(float(row['yhat']), 2)
		})

	return output

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--site_id', type=int, required=True)
	args = parser.parse_args()

	response = {
		"model": "prophet",
		"forecast": [],
		"error": None
	}

	try:
		forecast_data = run_prophet(args.site_id)
		response["forecast"] = forecast_data
	except Exception as e:
		# Ensure the error is logged to stderr (traceback already printed)
		response["error"] = str(e)

	# FINAL JSON OUTPUT
	print(json.dumps(response))
