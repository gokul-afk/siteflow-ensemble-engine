"""
Transform Kaggle Store Item Demand Forecasting Challenge CSV for SiteFlow

1. Download train.csv from Kaggle: https://www.kaggle.com/c/demand-forecasting-kernels-only/data
2. Rename columns:
   - store -> site_id
   - item -> material_id
   - sales -> units_consumed
3. Save as site_materials_usage.csv
"""
import pandas as pd
import sys



# Hardcoded file paths
input_csv = "data/raw/train.csv"
output_csv = "data/processed/site_materials_usage.csv"

# Read Kaggle CSV
df = pd.read_csv(input_csv)

# Rename columns
rename_map = {
    "store": "site_id",
    "item": "material_id",
    "sales": "units_consumed"
}
df = df.rename(columns=rename_map)

# Save to new CSV
df.to_csv(output_csv, index=False)
print(f"Saved transformed CSV to {output_csv}")
