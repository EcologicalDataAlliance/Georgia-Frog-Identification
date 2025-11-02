import pandas as pd
from pathlib import Path

NOTEBOOKS = Path(__file__).resolve().parents[1] / 'notebooks'

files = {
    'train': NOTEBOOKS / 'metadata_train.csv',
    'val': NOTEBOOKS / 'metadata_val.csv',
    'test': NOTEBOOKS / 'metadata_test.csv'
}

for name, fp in files.items():
    if not fp.exists():
        print(f"Missing {name} file: {fp}")
        continue
    df = pd.read_csv(fp)
    total = len(df)
    species_counts = df['species'].value_counts().sort_values(ascending=False)
    unique = species_counts.size
    top = species_counts.head(5)
    print(f"--- {name.upper()} ---")
    print(f"rows: {total}, unique species: {unique}")
    print("top 5 species counts:")
    print(top.to_string())
    print()

# Combined check
present = [p for p in files.values() if p.exists()]
if present:
    dfs = [pd.read_csv(p) for p in present]
    all_df = pd.concat(dfs, ignore_index=True)
    print('--- COMBINED SUMMARY ---')
    print(f"total rows combined: {len(all_df)}")
    print('species distribution across combined:')
    print(all_df['species'].value_counts().sort_values(ascending=False).head(20).to_string())
