from huggingface_hub import login
from datasets import load_dataset
import pandas as pd
import os

hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise RuntimeError("Set HF_TOKEN environment variable before running this script.")

login(token=hf_token)

print("Downloading ILDC CJPE dataset...")
ds = load_dataset("Exploration-Lab/IL-TUR", "cjpe")

print("\nDataset structure:")
print(ds)

print("\nAvailable splits:", list(ds.keys()))

# Save all splits
for split_name in ds.keys():
    df = ds[split_name].to_pandas()
    filename = f"ildc_{split_name}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {filename} → {len(df):,} rows | columns: {df.columns.tolist()}")

print("\nDone! All CSV files saved.")