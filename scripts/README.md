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

### `evaluate_rf.py` (Proposed)
**Purpose**: Automated evaluation of the Random Forest model.

**What it would do**:
- Load trained `rf_calibrated_model.joblib` and `scaler.joblib`
- Load test dataset (X_test, y_test)
- Compute accuracy, F1 scores, classification report
- Generate and save confusion matrix to `reports/`
- Export metrics as JSON for CI/CD integration

**Expected usage**:
```bash
python scripts/evaluate_rf.py --model services/frog-api/rf_calibrated_model.joblib --data data/X_test.npy
```

**Status**: Template provided in `POSTER_SUMMARY.md`, not yet implemented

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
