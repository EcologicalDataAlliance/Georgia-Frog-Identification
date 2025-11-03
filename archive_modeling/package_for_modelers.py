#!/usr/bin/env python3
"""Package modeling deliverables into a zip under release/ and write MODELERS_README.md"""
import shutil
from pathlib import Path

REPO = Path.cwd()
OUT = REPO / 'release' / 'modelers_package'
OUT.parent.mkdir(parents=True, exist_ok=True)

INCLUDE = [
    REPO / 'data' / 'processed',
    REPO / 'data' / 'spectrograms',
    REPO / 'data' / 'augmented',
    REPO / 'data' / 'features_aggregated.csv',
    REPO / 'metadata_train.csv',
    REPO / 'metadata_val.csv',
    REPO / 'metadata_test.csv',
    REPO / 'metadata_all.csv',
    REPO / 'models' / 'baseline' / 'report.md',
]

# create temp dir
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

for path in INCLUDE:
    if path.exists():
        if path.is_file():
            shutil.copy2(path, OUT / path.name)
        else:
            shutil.copytree(path, OUT / path.name)
    else:
        print('Warning: missing', path)

zip_path = shutil.make_archive(str(OUT), 'zip', root_dir=str(OUT))
print('Created zip:', zip_path)

# write README for modelers
readme = REPO / 'MODELERS_README.md'
readme.write_text("""
Modelers package
================

This archive contains:

- data/processed/  -- normalized WAVs (mono, 22050 Hz, 10s)
- data/spectrograms/ -- .npy log-mel spectrograms and previews
- data/augmented/ -- small sample of augmented audio (for inspection)
- data/features_aggregated.csv -- aggregated features (MFCC means/std, spectral stats)
- metadata_train.csv, metadata_val.csv, metadata_test.csv -- stratified splits
- metadata_all.csv -- combined index with paths and split column
- models/baseline/report.md -- baseline metrics and top features

Notes:
- Use `data/features_aggregated.csv` for quick classical ML baselines.
- For CNNs or training from spectrograms, use `data/spectrograms/` or re-run the feature-extraction cell.
- Augmentations are provided as a small sample only. Full augmentation should be applied on-the-fly in training.

Provenance:
- The CSVs and models include provenance in the `provenance` column or report files. If you need exact commit info, check git.

""")
print('Wrote', readme)
