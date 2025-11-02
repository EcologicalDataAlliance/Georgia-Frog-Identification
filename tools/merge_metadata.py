from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
OUTFILE = ROOT / "metadata_all.csv"

patterns = ["metadata_train.csv", "metadata_val.csv", "metadata_test.csv"]

dfs = []
for p in patterns:
    fp = NOTEBOOKS / p
    if not fp.exists():
        print(f"Warning: expected file not found: {fp}")
        continue
    df = pd.read_csv(fp)
    # determine split from filename
    if "train" in p:
        split = "train"
    elif "val" in p or "validation" in p:
        split = "val"
    elif "test" in p:
        split = "test"
    else:
        split = "unknown"
    if 'split' in df.columns:
        df['split'] = df['split'].fillna(split)
    else:
        df['split'] = split
    dfs.append(df)

if not dfs:
    print("No metadata files found. Nothing to do.")
    raise SystemExit(1)

all_df = pd.concat(dfs, ignore_index=True)
# optional: drop exact duplicates (same file path and same split)
if 'file' in all_df.columns:
    before = len(all_df)
    all_df = all_df.drop_duplicates(subset=['file', 'split'])
    after = len(all_df)
else:
    before = len(all_df)
    all_df = all_df.drop_duplicates()
    after = len(all_df)

all_df.to_csv(OUTFILE, index=False)
print(f"Wrote {OUTFILE} ({len(all_df)} rows).  Duplicates removed: {before-after}")
print(all_df['split'].value_counts().to_string())
