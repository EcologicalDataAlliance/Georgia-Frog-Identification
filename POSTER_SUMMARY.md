# Georgia Frog Identification — Poster-Ready Summary

## Data Collection
- Sources: Supabase Storage/Catalog for species media; user recordings saved to private bucket `frog-user-recordings`.
- Feedback Loop: `predictions` and `feedback` tables capture outputs and user corrections (see `services/frog-api/supabase_schema.sql`).
- Live Metrics: SQL view `prediction_accuracy` and function `get_model_stats()` summarize volumes, accuracy rate proxy, and confidence.

## Audio Preprocessing
- Mono conversion; silence trimming (`top_db=30`).
- Find best 10 s window via 1 s RMS scanning; resample to 22,050 Hz; pad/trim to exact 10 s.
- Optional pre-emphasis (0.97); peak-normalize to 0.98.
- Implementation of the above lives in `services/frog-api/main.py` (`normalize_audio`).

## Feature Engineering (26-D)
- Spectral: `centroid_mean`, `bandwidth_mean`, `rolloff_mean`.
- MFCC: means for `mfcc1`–`mfcc13`.
- MFCC stdevs: `mfcc1`, `mfcc3`, `mfcc4`, `mfcc5`, `mfcc7`, `mfcc8`, `mfcc12`.
- Energy/Temporal: `zcr_mean`, `rms_mean`, `rms_std`.
- Exact order enforced by `services/frog-api/feature_columns.json`; mapping in `features_dict_to_array()`.

## Model
- Deployed: Calibrated Random Forest Classifier (scikit-learn) with optional `StandardScaler`.
- Classes (15): American Bullfrog, Barking Treefrog, Bird-voiced Treefrog, Brimley’s Chorus Frog, Cope’s Gray Treefrog, Fowler’s Toad, Green Treefrog, Greenhouse Frog, Little Grass Frog, Northern Cricket Frog, Pig Frog, Pine Barrens Treefrog, Southern Chorus Frog, Southern Leopard Frog, Spring Peeper. See `services/frog-api/README.md`.

## API & MVP Flow
- FastAPI service (`services/frog-api/main.py`):
  - `POST /predict-audio`: file → preprocess → features → scale → predict → top-3 with confidences; background save to Supabase.
  - `POST /predict`: 26-D feature vector → predict (for batch/testing).
  - `GET /audio/{filename}`, `GET /signed-url/{filename}`, `POST /feedback`, `GET /health`.
- Frontend (Vite + React) with Node/Express proxy (`frontend/server/index.js`):
  - `POST /classify` → FastAPI `/predict-audio`; enriches predictions with species image URLs from Supabase catalogs.
  - Media utilities: `/species-media-batch`, storage listings, health checks.

## Evidence & Results (from repository artifacts)
- RF evaluation notebooks generate a confusion matrix image at `reports/confusion_matrix_rf.png` (not committed); see:
  - `Final_Random_Forest.ipynb` and `Random_Forest (1).ipynb` cells calling `classification_report(...)` and saving the heatmap (`plt.savefig("reports/confusion_matrix_rf.png")`).
- Training logs (CNN experimentation in `modeling_updates.ipynb`):
  - Best validation accuracy milestones observed: 0.4619 → 0.5286 → 0.5714 → 0.5762 (see lines around the repeated "New best validation accuracy:" prints).
  - Snapshot report: `Training Accuracy: 0.5714`, `Validation Accuracy: 0.5714`.
- Target performance (project goal, from `README.md`): Top-1 > 85%, Top-3 > 95%.

## How To Reproduce Metrics Locally
- Evaluate RF notebook:
  1) Open `Final_Random_Forest.ipynb` or `Random_Forest (1).ipynb` and run the evaluation section (cells that import `classification_report` / `confusion_matrix`).
  2) Confirm `reports/confusion_matrix_rf.png` is generated; capture printed accuracy/F1 and class-wise report.
- Or query live usage in Supabase (once predictions/feedback exist):
  - Use `get_model_stats()` from `services/frog-api/supabase_schema.sql`:
    ```sql
    select * from get_model_stats();
    ```
  - Inspect `prediction_accuracy` view for per-class volumes and average confidences.

## Example Prediction (shape)
- FastAPI returns top-3 predictions with confidences (see `services/frog-api/README.md` and test scripts `services/frog-api/test_api.py`, `test_audio.py`).

## Provenance (files to cite on the poster)
- Preprocessing & features: `services/frog-api/main.py`, `services/frog-api/feature_columns.json`.
- API endpoints & usage: `services/frog-api/README.md`, `frontend/OVERVIEW.md`, `frontend/server/index.js`.
- Notebooks with metrics/plots: `Final_Random_Forest.ipynb`, `Random_Forest (1).ipynb`, `modeling_updates.ipynb`.
- Supabase schema & analytics: `services/frog-api/supabase_schema.sql`.

## Current Verified Numbers vs Targets
| Category | Verified Value (Repo Artifacts) | Source | Target (README) |
|----------|---------------------------------|--------|-----------------|
| RF Confusion Matrix | Generated (image path `reports/confusion_matrix_rf.png` referenced, not committed) | RF notebooks | N/A |
| RF Overall Metrics | Not captured in committed outputs (code computes `accuracy`, `classification_report`) | RF notebooks | Top-1 >85%, Top-3 >95% |
| CNN Validation Accuracy | Progress milestones: 0.4619 → 0.5286 → 0.5714 → 0.5762 | `modeling_updates.ipynb` printed logs | Improve toward RF target |
| Snapshot Train/Val Accuracy | 0.5714 / 0.5714 (single run) | `modeling_updates.ipynb` | N/A |
| Live Accuracy Proxy | Function `get_model_stats()` (accuracy_rate = 1 - feedback/predictions) | `supabase_schema.sql` | Continuous tracking |

## Limitations & Pending Validation
- Confusion matrix PNG is referenced but not versioned; commit it after regenerating for reproducibility.
- No persisted test set size, class distribution, or exact Top-1/Top-3 numeric results in text artifacts.
- Validation numbers (≈57%) are below aspirational targets; indicates need for additional data, model tuning (e.g., class balancing, feature augmentation, ensemble calibration).
- Citizen-science / field recordings ingestion volume not summarized yet; Supabase tables will enable future aggregate reporting once populated.

## Recommended Next Steps (Technical)
1. Execute RF evaluation cells; capture `accuracy_score`, macro/micro F1, and commit both confusion matrix PNG and a JSON export of `classification_report` (e.g., `reports/rf_report.json`).
2. Add automatic evaluation script (`scripts/evaluate_rf.py`) to regenerate metrics headlessly for CI.
3. Implement dataset snapshot manifest (`data/dataset_manifest.csv`) enumerating files per species to contextualize class imbalance.
4. Enhance feature set (e.g., delta MFCCs, spectral contrast) and compare via A/B notebook.
5. Integrate periodic Supabase cron job to materialize accuracy & drift metrics (store daily aggregates).

## Supabase Monitoring Workflow (Poster Callout)
1. Prediction insert (via `/predict-audio`) populates `predictions` (stores full probability vector & top-3).
2. User correction (`/feedback`) increments `feedback` and shifts accuracy proxy.
3. Analyst runs:
   ```sql
   select * from get_model_stats();
   select * from prediction_accuracy order by total_predictions desc;
   ```
4. Dashboard tiles: total recordings, feedback count, proxy accuracy trend, average top-1 confidence, top-5 most frequent species.

## Reproducibility Checklist (Quick Reference)
- [ ] Pull repo; create Python venv; install `services/frog-api/requirements.txt`.
- [ ] Run FastAPI locally; invoke `test_audio.py` with a sample wav to confirm top-3 output.
- [ ] Open RF notebook; run evaluation section; export confusion matrix PNG + classification report JSON.
- [ ] Query Supabase for live stats once predictions present.

## Poster Visual Suggestions
- Pipeline diagram (Audio → Preprocess → Features (26) → Calibrated RF → Top-3 + Confidences → Feedback Loop).
- Bar chart of validation accuracy progression (CNN experiments) vs target threshold line.
- Confusion matrix heatmap (RF) with misclassification highlights.
- Supabase live metrics mini-panel (mock numbers if not yet populated).

## Rapid Evaluation Script (Proposed Stub)
Add `scripts/evaluate_rf.py` (not yet present) to automate metric extraction; example structure:
```python
#!/usr/bin/env python3
import json, joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

# TODO: load X_test, y_test from prepared artifact
model = joblib.load('services/frog-api/rf_calibrated_model.joblib')
scaler = joblib.load('services/frog-api/scaler.joblib')
X_test = np.load('data/X_test.npy')
y_test = np.load('data/y_test.npy')

if scaler:
  X_test = scaler.transform(X_test)
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)
cm = confusion_matrix(y_test, y_pred)
with open('reports/rf_report.json','w') as f: json.dump({'accuracy': acc, 'report': report, 'confusion_matrix': cm.tolist()}, f, indent=2)
print(f'Accuracy: {acc:.4f}')
```

---
Prepared directly from repository code artifacts; no external assumptions added beyond explicit files.
