import argparse
import json
import sys
import os
import pandas as pd
import numpy as np
import xgboost as xgb
import logging
import traceback

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_data_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', 'data', 'site_materials_usage.csv')

def get_mock_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=60)
    values = 100 + np.random.normal(0, 10, size=60)
    return pd.DataFrame({'date': dates, 'units_consumed': values})

def run_xgboost(site_id):
    csv_path = get_data_path()
    logging.info(f"[{pd.Timestamp.now()}] XGBoost: starting data load")
    if os.path.exists(csv_path):
        logging.info(f"[{pd.Timestamp.now()}] XGBoost: found CSV at {csv_path}")
        df = pd.read_csv(csv_path)
        logging.info(f"[{pd.Timestamp.now()}] XGBoost: loaded CSV, shape={df.shape}")
        if 'site_id' in df.columns:
            df = df[df['site_id'] == site_id]
            logging.info(f"[{pd.Timestamp.now()}] XGBoost: filtered by site_id={site_id}, rows={len(df)}")
    else:
        logging.warning(f"[{pd.Timestamp.now()}] XGBoost: CSV not found at {csv_path}, using mock data")
        df = get_mock_data()
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    # Prepare features for XGBoost (simple time series regression)
    df['dayofyear'] = df.index.dayofyear
    X = df[['dayofyear']].values
    y = df['units_consumed'].values
    model = xgb.XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
    try:
        logging.info(f"[{pd.Timestamp.now()}] XGBoost: starting model fit")
        model.fit(X, y)
        logging.info(f"[{pd.Timestamp.now()}] XGBoost: model fit complete")
    except Exception as e:
        logging.error(f"[{pd.Timestamp.now()}] XGBoost: exception during model fit")
        traceback.print_exc(file=sys.stderr)
        raise
    logging.info(f"[{pd.Timestamp.now()}] XGBoost: starting forecast generation")
    last_day = df.index[-1].dayofyear
    future_days = np.array([[last_day + i] for i in range(1, 8)])
    preds = model.predict(future_days)
    output = []
    for i, value in enumerate(preds):
        date_str = (df.index[-1] + pd.Timedelta(days=i+1)).strftime('%Y-%m-%d')
        output.append({
            "date": date_str,
            "value": round(float(value), 2)
        })
    logging.info(f"[{pd.Timestamp.now()}] XGBoost: forecast generation complete")
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--site_id', type=int, required=True)
    args = parser.parse_args()
    response = {
        "model": "xgboost",
        "forecast": [],
        "error": None
    }
    logging.info(f"[{pd.Timestamp.now()}] XGBoost: script started for site_id={args.site_id}")
    try:
        forecast_data = run_xgboost(args.site_id)
        response["forecast"] = forecast_data
        logging.info(f"[{pd.Timestamp.now()}] XGBoost: script completed successfully")
    except Exception as e:
        response["error"] = str(e)
        logging.error(f"[{pd.Timestamp.now()}] XGBoost: script failed with error: {e}")
    print(json.dumps(response))
