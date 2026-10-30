import sqlite3
import pandas as pd
import glob
import os

conn = sqlite3.connect("golden_collections.db")

print("--- 1. LOADING STAGING TABLES INTO GOLDEN_COLLECTIONS.DB ---")
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

conn.commit()
conn.close()
print("\nAll staging, clean, and KPI tables successfully synchronized in golden_collections.db!")

