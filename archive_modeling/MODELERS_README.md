
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
 - models/baseline/report.md -- baseline metrics and top features
 - models/baseline/plots/permutation_importance_all_classes.png -- combined multi-panel permutation importance plot (top features per class)
 - models/baseline/plots/permutation_importance_all_classes.png -- combined multi-panel permutation importance plot (top features per class)
 - models/baseline/plots/global_top20_feature_importances_highres.png -- high-resolution global RF importances
 - models/baseline/plots/global_top20_feature_importances.svg -- SVG of global RF importances
 - models/baseline/plots/one_slide_combined.png -- side-by-side one-slide PNG combining global RF importances and the multi-panel permutation importance figure
 - models/baseline/plots/one_slide_combined_highres.png -- high-resolution version of the one-slide PNG

Notes:
- Use `data/features_aggregated.csv` for quick classical ML baselines.
- For CNNs or training from spectrograms, use `data/spectrograms/` or re-run the feature-extraction cell.
- Augmentations are provided as a small sample only. Full augmentation should be applied on-the-fly in training.

Visuals:
- The folder `models/baseline/plots/` contains PNGs: a global RF feature-importance plot and a combined multi-panel permutation-importance figure (`permutation_importance_all_classes.png`) that shows the top-permuted features that most reduce per-class F1 when randomized. These are useful for targeted augmentation or per-class feature analysis.

Provenance:
- The CSVs and models include provenance in the `provenance` column or report files. If you need exact commit info, check git.

