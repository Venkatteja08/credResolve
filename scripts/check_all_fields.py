import pandas as pd
import glob
import os

print("--- Inspecting fields in all tables ---")
for f in sorted(glob.glob("collections_30k_dataset/*.csv")):
    if "data_dictionary" in f: continue
    df = pd.read_csv(f, nrows=2)
    print(f"\n*** {os.path.basename(f)} ***")
    for col in df.columns:
        print(f"  {col}: {df[col].iloc[0]}")
