# GA_Frog_ID_Data_Prep

This repository contains the Jupyter notebook-driven data-preparation pipeline used to robustly decode, normalize, and prepare frog audio recordings for feature extraction and model training.

## What this project does

- Downloads audio references (the notebook is set up to fetch from Supabase when credentials are provided).
- Robustly decodes various input formats (primary loader: `librosa`; fallback: system `ffmpeg`) to avoid failures on tricky MP3/MP4 files.
- Converts to mono, resamples to 22050 Hz, enforces a 10.0 s standardized duration (pad/trim), applies optional pre-emphasis and peak normalization, and writes 16-bit PCM WAVs.
- Handles Macaulay Library (ML) recordings with a conservative default leading offset to skip spoken intros and provides tools to generate per-file offset proposals.

## Important files & layout

- `notebooks/data_preperation.ipynb` — primary pipeline notebook. Contains utilities, robust loader, batch normalization, diagnostics, reprocess helpers, feature-extraction and preview cells, and optional VAD proposal cells.
- `data/processed/{species}/` — output directory for normalized WAV files produced by the notebook (mono, 22,050 Hz, 10 s, 16-bit PCM).
- `data/spectrograms/{species}/{base_filename}.npy` — log-mel spectrograms saved as float32 NumPy arrays (dB-scaled). These mirror the processed audio hierarchy.
- `data/spectrograms/preview/{species}/{base_filename}.png` — compact PNG previews of each spectrogram for quick visual checks.
- `metadata_train.csv`, `metadata_val.csv`, `metadata_test.csv` — stratified metadata splits produced by the feature-extraction cell (70/15/15 by default). Files are saved at the repository root.
- `data_preparation_report.md` — short report summarizing parameters, counts, and any notable issues found during feature extraction.
- `notebooks/metadata_processed_YYYYMMDD_HHMMSS.csv` — per-run metadata recorded by the normalization step (keeps a record of loader used, offsets applied).
- `notebooks/ml_vad_offset_proposals_*.csv` — (optional) VAD-generated per-file offset proposals when you run the VAD scanner cell.
- `requirements.txt`, `pyproject.toml`, `setup.cfg` — reproducible dependency files added to the repository; `webrtcvad` is included as an optional extra.
- `.env.example` — example environment variables (Supabase credentials) if you need to download files from a private store.

## Macaulay Library (ML) handling

- Default behavior: the pipeline applies a leading offset of 4.0 seconds for ML files to conservatively skip human voice intros. This is controlled by the `ML_OFFSET_SEC` constant in the notebook.
- Per-file overrides: the notebook supports an `offset_overrides` mapping (CSV import or manual edits) so you can fine-tune or disable the offset for individual recordings.

## WebRTC VAD and energy-based fallback

- The notebook includes a VAD-based scanner (uses `webrtcvad`) to propose more accurate per-file leading-trim offsets. This is optional.
- On Windows, installing `webrtcvad` typically requires Microsoft C++ Build Tools (MSVC). If you can't build it, the notebook also includes an energy-based scanner as a fallback to produce offset proposals.

Note from recent work in this repository: a full normalization run completed successfully in this workspace (1,400 files processed; metadata saved to `notebooks/metadata_processed_20251101_050842.csv`). The VAD proposal cell was added but its runtime requires `webrtcvad` (build may fail on Windows without MSVC). The energy-based scanner is available as an alternative.

## Prerequisites

- Python 3.8+ (3.9/3.10 recommended)
- System binary: `ffmpeg` (required for robust fallback decoding). On Windows you can install via `winget` (example: `winget install --id=Gyan.FFmpeg -e`) or add a prebuilt `ffmpeg` to your PATH. The notebook tries to detect `ffmpeg` on PATH and in the common winget install location.

Python packages (quick install):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Optional (VAD):
# python -m pip install webrtcvad
```

If `webrtcvad` fails to build on Windows, install the Microsoft C++ Build Tools or skip the VAD step and use the energy-based scanner.

## Quick run (notebook)

1. Copy `.env.example` -> `.env` and fill any required Supabase credentials (if you will download files).
2. Open `notebooks/data_preperation.ipynb` in Jupyter or VS Code.
3. Inspect and (optionally) adjust constants near the top of the notebook:
   - `ML_OFFSET_SEC` — default 4.0 seconds for ML recordings.
   - `TARGET_SR` — 22050 (target sample rate).
   - `TARGET_DURATION` — 10.0 (seconds)
4. To process the whole dataset in this environment, set `FULL_RUN = True` in the normalization batch cell and run that cell. The notebook will download (if needed), decode (librosa -> ffmpeg fallback), normalize, and save WAVs to `data/processed/` and a metadata CSV to `notebooks/`.

### Feature extraction (spectrograms + metadata)

After you've produced `data/processed/` you can run the feature-extraction cell (at the end of the notebook) which will:

- Walk `data/processed/**/*.wav` and compute log-mel spectrograms (defaults: n_mels=64, n_fft=1024, hop_length=512, power=2.0).
- Save dB-scaled spectrogram arrays as `.npy` under `data/spectrograms/{species}/` mirroring the processed audio tree.
- Save PNG previews under `data/spectrograms/preview/{species}/` for quick visual checks.
- Produce stratified train/val/test CSVs at the repo root: `metadata_train.csv`, `metadata_val.csv`, `metadata_test.csv` (70/15/15 by default). If stratified splitting fails because of tiny classes, the cell falls back to a random split and logs a note in `data_preparation_report.md`.

To run feature extraction: run the final notebook cell (it respects the constants at the top of the notebook; change `N_MELS`, `N_FFT`, `HOP_LENGTH` there if needed).

## Outputs and diagnostics

\- Normalized WAVs: `data/processed/{species}/{base_filename}.wav` (mono, 22,050 Hz, 10 s, 16-bit PCM).
\- Spectrograms: `data/spectrograms/{species}/{base_filename}.npy` (log-mel dB arrays, float32).
\- PNG previews: `data/spectrograms/preview/{species}/{base_filename}.png`.
\- Metadata CSVs (feature-split): `metadata_train.csv`, `metadata_val.csv`, `metadata_test.csv` (repo root).
\- Per-run normalization metadata: `notebooks/metadata_processed_YYYYMMDD_HHMMSS.csv`.
\- Diagnostics (when enabled): `notebooks/normalization_errors_ML_*.csv`, `notebooks/ml_decode_diagnostics_*.csv`, `notebooks/reprocess_ML_ffmpeg_results_*.csv`.

Additional modeling artifacts (generated by the helper scripts):

- Aggregated features: `data/features_aggregated.csv` — per-file aggregated features (MFCC means/std, spectral centroid/bandwidth/rolloff, RMS, ZCR) with a `provenance` field (run id + timestamp + git commit where available).
- Baseline model & report: `models/baseline/rf_baseline.joblib`, `models/baseline/report.md` — quick RandomForest baseline and a human-readable report of per-class metrics.
- Feature importances and permutation importance CSVs: `models/baseline/feature_importances.csv`, `models/baseline/permutation_importance_top10_per_class.csv`.
- Plots: `models/baseline/plots/` contains PNGs and SVGs for global feature importances and a combined multi-panel permutation-importance figure. Examples:
   - `global_top20_feature_importances.png` / `_highres.png` / `.svg`
   - `permutation_importance_all_classes.png` (multi-panel)
   - `one_slide_combined.png` / `_highres.png` (side-by-side composite for slides)
- Augmented sample (inspection-only): `data/augmented/sample/` (a small set of augmented WAVs created for underrepresented species) and `models/baseline/augmentation_sample.txt` listing them.
- Packaged deliverable: `release/modelers_package.zip` — a zip containing the processed data, spectrograms, aggregated features, metadata splits, and baseline report for handoff to modelers.

## Troubleshooting

- ffmpeg not found: add `ffmpeg` to PATH or install via winget. The notebook includes logic to detect a winget-installed ffmpeg on Windows.
- We get occasional decoding issues for some ML MP3s when using the Python loader; the `ffmpeg` fallback addresses most of these.
- `webrtcvad` build fails on Windows without MSVC — either install Microsoft C++ Build Tools or use the energy-based scanner.

## Next steps / suggestions

1. Run feature extraction (final notebook cell) to produce `data/spectrograms/` and metadata CSVs.
2. Review class counts in `metadata_train.csv` and produce augmentation strategies only for underrepresented species.
3. (Optional) If modelers want a single index file, create `metadata_all.csv` by concatenating the split CSVs and adding a `split` column.

If you'd like, I can add a single-line helper to the notebook to emit `metadata_all.csv`, or move spectrogram `.npy` files into `data/spectrograms/{split}/{species}/` if you prefer datasets physically partitioned by split.
