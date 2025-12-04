# Scripts

Utility scripts for training, evaluation, and data processing.

## Available Scripts

### `svm_train.py`
**Purpose**: Sanity check and validation script for processed audio data.

**What it does**:
- Checks for existence of `processed/` and `spectrogram/` CSV files
- Prints data shape and distribution statistics
- Validates feature engineering pipeline outputs

**Usage**:
```bash
python scripts/svm_train.py
```

**Dependencies**: pandas, numpy

---

### `generate_confusion_matrix.py`
**Purpose**: Generate publication-ready confusion matrices with clear class labels.

**What it does**:
- Loads trained model and scaler
- Generates predictions on test data
- Creates both count-based and normalized confusion matrices
- Properly formats species names (e.g., "Fowler's Toad", "Cope's Gray Treefrog")
- Saves high-resolution (300 DPI) images
- Generates detailed classification report (precision/recall/F1)

**Usage**:
```bash
# Basic usage with test data CSV
python scripts/generate_confusion_matrix.py --data data/processed/test_set.csv

# Custom output and figure size
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --output reports/figures/poster_cm.png \
    --figsize 16 14 \
    --fontsize 12

# Normalized matrix only
python scripts/generate_confusion_matrix.py --data data/test.csv --normalize
```

**Dependencies**: numpy, pandas, matplotlib, seaborn, scikit-learn, joblib

**Documentation**: See `scripts/CONFUSION_MATRIX_GUIDE.md` for detailed usage

---

### `evaluate_rf.py` (Proposed)
**Purpose**: Automated evaluation of the Random Forest model.

**Status**: Template provided in `POSTER_SUMMARY.md`, not yet implemented. Consider using `generate_confusion_matrix.py` for evaluation needs.

---

## Adding New Scripts

When adding utility scripts:

1. **Document purpose clearly** - Add description here
2. **Include usage examples** - Show command-line invocation
3. **List dependencies** - Specify required packages
4. **Follow naming conventions** - Use descriptive snake_case names
5. **Add argparse** - Accept command-line arguments for flexibility
6. **Return exit codes** - Use `sys.exit(0)` for success, non-zero for errors

## Script Categories

- **Training**: Model training pipelines
- **Evaluation**: Metric computation and reporting
- **Data Processing**: Feature extraction, preprocessing
- **Utilities**: Helper functions, validation checks

## Best Practices

- Keep scripts focused on a single task
- Make them idempotent where possible
- Log progress and errors clearly
- Use absolute paths or path resolution (e.g., `pathlib`)
- Include `if __name__ == "__main__":` guard
