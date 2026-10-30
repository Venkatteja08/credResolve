import sqlite3
import pandas as pd
import glob
import os

DB_TEST = "test_sql_execution.db"
if os.path.exists(DB_TEST):
    os.remove(DB_TEST)

conn = sqlite3.connect(DB_TEST)

print("--- 1. LOADING STAGING TABLES ---")
# Load stg_ from CSVs
for f in sorted(glob.glob("collections_30k_dataset/*.csv")):
    bname = os.path.basename(f)
    if bname == "data_dictionary.csv": continue
    tbl = "stg_" + bname.replace(".csv", "")
    df = pd.read_csv(f, low_memory=False)
    df.to_sql(tbl, conn, if_exists="replace", index=False)
    print(f"Loaded {tbl}: {len(df)} rows")

print("\n--- 2. EXECUTING SQL SCRIPTS ---")
sql_files = [
    "sql/01_schema_staging.sql",
    "sql/02_data_cleaning.sql",
    "sql/03_entity_resolution.sql",
    "sql/04_transformations_dim_fact.sql",
    "sql/05_metric_calculations.sql"
]

for sfile in sql_files:
    print(f"Executing {sfile}...")
    with open(sfile, "r") as f:
        script = f.read()
    conn.executescript(script)
    print(f"  -> SUCCESS")

print("\n--- 3. VERIFYING KPI VIEWS ---")
df_bench = pd.read_sql_query("SELECT * FROM kpi_recovery_benchmark_monthly", conn)
print("kpi_recovery_benchmark_monthly:")
print(df_bench[['payment_month', 'calendar_days', 'raw_reported_recovery', 'raw_mom_growth_pct', 'net_settled_recovery', 'net_mom_growth_pct', 'daily_run_rate_recovery', 'daily_run_rate_mom_pct']])

df_voice = pd.read_sql_query("SELECT * FROM kpi_voice_operations_monthly", conn)
print("\nkpi_voice_operations_monthly:")
print(df_voice)

conn.close()
if os.path.exists(DB_TEST):
    os.remove(DB_TEST)
print("\nAll SQL scripts validated and reproducible!")
