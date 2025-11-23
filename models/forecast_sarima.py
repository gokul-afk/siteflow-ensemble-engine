

import argparse
import json
import sys
import os
import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
import logging
import traceback

warnings.filterwarnings("ignore")

# Configure logging to stderr so stdout remains pure JSON
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='[%(levelname)s] %(message)s')

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------
def get_data_path():
	script_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(script_dir, '..', 'data', 'site_materials_usage.csv')

def get_mock_data():
	dates = pd.date_range(end=pd.Timestamp.now(), periods=60)
	values = 100 + np.random.normal(0, 10, size=60)
	return pd.DataFrame({'date': dates, 'units_consumed': values})

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------
def run_sarima(site_id):
	csv_path = get_data_path()
    
	if os.path.exists(csv_path):
		logging.info(f"SARIMA: found CSV at {csv_path}")
		df = pd.read_csv(csv_path)
		logging.info(f"SARIMA: loaded CSV, shape={df.shape}")
		if 'site_id' in df.columns:
			df = df[df['site_id'] == site_id]
			logging.info(f"SARIMA: filtered by site_id={site_id}, rows={len(df)}")
	else:
		logging.warning(f"SARIMA: CSV not found at {csv_path}, using mock data")
		df = get_mock_data()

	# Prepare Data
	df['date'] = pd.to_datetime(df['date'])
	df = df.set_index('date')
    
	# Train Model (SARIMAX)
	# Using fixed order for speed. In real life, use auto_arima offline to find params.
	model = SARIMAX(df['units_consumed'], 
					order=(1, 1, 1), 
					seasonal_order=(1, 1, 1, 7)) # Weekly seasonality
    
	try:
		logging.info("SARIMA: starting model fit")
		results = model.fit(disp=False)
		logging.info("SARIMA: model fit complete")
	except Exception as e:
		logging.error("SARIMA: exception during model fit")
		traceback.print_exc(file=sys.stderr)
		raise

	# Predict next 7 days
	forecast_result = results.get_forecast(steps=7)
	predicted_mean = forecast_result.predicted_mean
    
	output = []
	for i, value in enumerate(predicted_mean):
		# Get the date from predicted_mean.index if possible, else fallback to today + i
		idx = predicted_mean.index[i]
		if hasattr(idx, 'strftime'):
			date_str = idx.strftime('%Y-%m-%d')
		else:
			# Fallback: treat as offset from last date in df
			try:
				last_date = df.index[-1]
				if hasattr(last_date, 'to_pydatetime'):
					last_date = last_date.to_pydatetime()
				date_str = (last_date + pd.Timedelta(days=i+1)).strftime('%Y-%m-%d')
			except Exception:
				date_str = str(idx)
		output.append({
			"date": date_str,
			"value": round(float(value), 2)
		})
	return output

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--site_id', type=int, required=True)
	args = parser.parse_args()

	response = {
		"model": "sarima",
		"forecast": [],
		"error": None
	}

	try:
		forecast_data = run_sarima(args.site_id)
		response["forecast"] = forecast_data
	except Exception as e:
		response["error"] = str(e)

	# FINAL JSON OUTPUT
	print(json.dumps(response))
