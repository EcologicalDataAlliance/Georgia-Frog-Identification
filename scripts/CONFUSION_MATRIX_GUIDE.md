# Confusion Matrix Generator

## Quick Start

Generate a clear confusion matrix from your trained model:

```bash
cd /Users/professornirvar/datacap/Georgia-Frog-Identification

# With test data CSV (features + species label in last column)
python scripts/generate_confusion_matrix.py --data data/processed/test_set.csv
```

## Features

✅ **Clear Species Names** - Proper capitalization and apostrophes  
✅ **Dual Output** - Both count and normalized (percentage) matrices  
✅ **High Resolution** - 300 DPI for publication quality  
✅ **Readable Labels** - Rotated and sized appropriately  
✅ **Classification Report** - Precision/recall/F1 metrics saved to text

## Usage Examples

### Basic Usage (with test data)
```bash
python scripts/generate_confusion_matrix.py \
    --data data/processed/test_set.csv
```

Output:
- `reports/figures/confusion_matrix_clear.png` (count-based)
- `reports/figures/confusion_matrix_clear_normalized.png` (percentage-based)
- `reports/classification_report.txt` (metrics)

### Custom Model Path
```bash
python scripts/generate_confusion_matrix.py \
    --model models/my_model.joblib \
    --scaler models/my_scaler.joblib \
    --data data/test.csv
```

### Normalized Only
```bash
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --normalize
```

### Custom Output Location
```bash
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --output reports/figures/poster_cm.png \
    --figsize 16 14 \
    --fontsize 11
```

### Larger Figure for Presentation
```bash
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --figsize 18 16 \
    --fontsize 12
```

## Input Data Format

The script expects a CSV file with:
- **Columns 1 to N-1:** Feature values (must match training features)
- **Column N (last):** Species labels (e.g., `american_bullfrog`, `spring_peeper`)

Example CSV structure:
```csv
centroid_mean,bandwidth_mean,rolloff_mean,...,species
2431.72,1540.15,5983.40,...,american_bullfrog
1823.45,1120.33,4200.11,...,spring_peeper
```

## Preparing Test Data

If you need to export test data from a notebook:

```python
import pandas as pd

# After train_test_split
X_test_df = pd.DataFrame(X_test, columns=feature_columns)
X_test_df['species'] = y_test

# Save to CSV
X_test_df.to_csv('data/processed/test_set.csv', index=False)
```

## Species Name Mapping

The script automatically formats species names:
- `american_bullfrog` → American Bullfrog
- `fowlers_toad` → Fowler's Toad
- `copes_gray_treefrog` → Cope's Gray Treefrog

Handles underscores, possessives, and compound names properly.

## Output Files

### confusion_matrix_clear.png
- **Format:** Count-based heatmap
- **Colors:** Green scale (darker = more samples)
- **Size:** 14×12 inches @ 300 DPI
- **Use for:** Seeing actual sample counts

### confusion_matrix_clear_normalized.png
- **Format:** Percentage-based heatmap
- **Colors:** Blue scale
- **Normalization:** By row (recall perspective)
- **Use for:** Comparing performance across imbalanced classes

### classification_report.txt
- Per-class precision, recall, F1-score
- Support (sample count per class)
- Overall accuracy
- Macro/weighted averages

## Customization Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `services/frog-api/rf_calibrated_model.joblib` | Path to trained model |
| `--scaler` | `services/frog-api/scaler.joblib` | Path to feature scaler |
| `--data` | (required) | Test data CSV |
| `--output` | `reports/figures/confusion_matrix_clear.png` | Output image path |
| `--normalize` | False | Generate normalized matrix only |
| `--figsize` | `14 12` | Figure size (width height) |
| `--fontsize` | `10` | Label font size |
| `--report` | `reports/classification_report.txt` | Report output path |

## Troubleshooting

### "No test data provided"
Provide a CSV file using `--data`:
```bash
python scripts/generate_confusion_matrix.py --data data/processed/test_set.csv
```

### "Model file not found"
Check paths or specify explicitly:
```bash
python scripts/generate_confusion_matrix.py \
    --model path/to/model.joblib \
    --scaler path/to/scaler.joblib \
    --data data/test.csv
```

### Labels cut off in image
Increase figure size:
```bash
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --figsize 16 14
```

### Font too small/large
Adjust font size:
```bash
python scripts/generate_confusion_matrix.py \
    --data data/test.csv \
    --fontsize 12
```

## Dependencies

Required Python packages (install via `pip` in your environment):
```bash
pip install numpy pandas matplotlib seaborn scikit-learn joblib
```

Or use the existing backend environment:
```bash
cd services/frog-api
source .venv/bin/activate
python ../../scripts/generate_confusion_matrix.py --data ../../data/test.csv
```

## Example Workflow

1. **Train model** in notebook (save model.joblib, scaler.joblib)
2. **Export test set** to CSV with features + labels
3. **Run script:**
   ```bash
   python scripts/generate_confusion_matrix.py --data data/processed/test_set.csv
   ```
4. **Check outputs:**
   - View `reports/figures/confusion_matrix_clear.png`
   - Review `reports/classification_report.txt`
   - Use normalized version for class-balanced analysis

## Related Files

- **Training notebook:** `notebooks/modeling/Final_Random_Forest.ipynb`
- **Production model:** `services/frog-api/rf_calibrated_model.joblib`
- **Feature spec:** `services/frog-api/feature_columns.json`
- **Existing matrix:** `reports/figures/confusion_matrix_Random_Forest_Smote_Tuned.png`
