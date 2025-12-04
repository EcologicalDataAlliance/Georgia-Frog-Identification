# Repeated Hold-Out Validation - Quick Start Guide

This guide explains how to run the `Final_Random_Forest_repeated_holdout.ipynb` notebook for comprehensive model validation.

## Prerequisites

1. **Backend environment setup**:
   ```bash
   cd services/frog-api
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Required files**:
   - `services/frog-api/rf_calibrated_model.joblib` (trained model)
   - `services/frog-api/scaler.joblib` (feature scaler)
   - `services/frog-api/feature_columns.json` (feature list)
   - `data/processed/features_aggregated.csv` (training data)

## Running the Notebook

### Option 1: VS Code Jupyter Extension
1. Open `notebooks/modeling/Final_Random_Forest_repeated_holdout.ipynb`
2. Click "Run All" or run cells sequentially (Shift+Enter)
3. Outputs automatically save to `reports/` and `reports/figures/`

### Option 2: Command Line
```bash
cd /Users/professornirvar/datacap/Georgia-Frog-Identification
cd services/frog-api
source .venv/bin/activate
jupyter notebook ../../notebooks/modeling/Final_Random_Forest_repeated_holdout.ipynb
```

## Notebook Structure (13 Steps)

| Step | Cell | Purpose |
|------|------|---------|
| 1 | Setup | Initialize paths and import libraries |
| 2 | Load Model | Load model, scaler, feature columns |
| 3 | Load Data | Load training data (features_aggregated.csv) |
| 4 | Prepare Features | Extract X (features) and y (labels) |
| 5 | Baseline | Single 80/20 split evaluation |
| 6 | Repeated Hold-Out | 10 iterations with different random seeds |
| 7 | Statistics & CI | Compute mean, std, 95% confidence intervals |
| 8 | Visualize | Plot metrics across iterations |
| 9 | Baseline CM | Generate baseline confusion matrix |
| 10 | Average CM | Compute and visualize averaged confusion matrix |
| 11 | Per-Class | Analyze performance per species |
| 12 | Export JSON | Save comprehensive metrics report |
| 13 | Summary | Print final summary and findings |
| 14 | Optional K-Fold | Run 5-fold cross-validation for comparison |

## Output Files

All outputs are automatically saved to:

### Visualizations (`reports/figures/`)
- `repeated_holdout_metrics.png` - Metrics across 10 iterations with CI bands
- `confusion_matrix_baseline_repeated_holdout.png` - Baseline confusion matrix
- `confusion_matrix_baseline_vs_average.png` - Comparison of baseline vs average
- `confusion_matrix_average_normalized.png` - Normalized average confusion matrix
- `per_class_performance_repeated_holdout.png` - Per-species metrics
- `validation_comparison_rhv_vs_kfold.png` - Repeated hold-out vs k-fold comparison

### Reports (`reports/`)
- `repeated_holdout_validation_report.json` - Complete metrics in JSON format
- `repeated_holdout_validation_summary.md` - Markdown summary with tables
- `kfold_validation_report.json` - K-fold validation results (if step 14 runs)

## Expected Results

### Baseline Metrics (from last run)
- Accuracy: ~0.78-0.82
- F1 Score: ~0.75-0.80

### Repeated Hold-Out (10 iterations)
- Accuracy: 0.78-0.82 ± 0.02 (typically lower variance than single split)
- F1 Score: 0.75-0.80 ± 0.02

### Challenging Species (typically lowest F1)
- Eastern Spadefoot Toad (confusion with American Toad)
- Fowler's Toad (similar to American Toad)

### Best Performing Species
- Spring Peeper (distinctive acoustic signature)
- Green Frog (clear spectral characteristics)

## Troubleshooting

### Error: "No such file or directory: data/processed/features_aggregated.csv"
**Solution**: Check that the CSV exists. The notebook searches for any CSV in `data/` as a fallback:
```bash
find /Users/professornirvar/datacap/Georgia-Frog-Identification/data -name "*.csv"
```

### Error: "joblib.load() failed"
**Solution**: Ensure the model and scaler files exist:
```bash
ls services/frog-api/*.joblib
```

### Visualization not showing
**Solution**: Ensure matplotlib is installed:
```bash
pip install matplotlib seaborn
```

### Out of memory
**Solution**: For large datasets, modify the notebook to process folds instead of all data at once. Contact the development team for guidance.

## Interpreting Results

### Confusion Matrix
- **Diagonal**: Correct predictions (higher is better)
- **Off-diagonal**: Misclassifications
- **Normalized version**: Shows percentage of each species correctly identified

### Per-Class Metrics
- **High variance in F1**: Model struggles with this species
- **Low precision, high recall**: Model over-predicts this species
- **High precision, low recall**: Model under-predicts this species

### Confidence Intervals
- **Narrow CI**: Model is stable across iterations
- **Wide CI**: Model performance varies with different data splits (potential instability)

## Next Steps

1. **Examine confusions**: Check per-class analysis for misclassified pairs
2. **Collect more data**: For low-performing species (F1 < 0.70)
3. **Feature engineering**: Consider additional acoustic features
4. **Model tuning**: Experiment with Random Forest hyperparameters
5. **External validation**: Test on new, unseen data from different sources

## Files Referenced

- Notebook: `notebooks/modeling/Final_Random_Forest_repeated_holdout.ipynb`
- Model: `services/frog-api/rf_calibrated_model.joblib`
- Scaler: `services/frog-api/scaler.joblib`
- Features: `services/frog-api/feature_columns.json`
- Training Data: `data/processed/features_aggregated.csv`
- Documentation: `notes.txt` (validation strategy options)

## Support

For issues or questions:
1. Check `reports/repeated_holdout_validation_summary.md` for quick reference
2. Review JSON report for detailed metrics: `reports/repeated_holdout_validation_report.json`
3. Consult the main README for project overview
