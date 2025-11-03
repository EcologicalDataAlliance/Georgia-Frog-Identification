#!/usr/bin/env python3
"""Compute class-wise permutation importance on validation set.
Saves top-10 features per class to models/baseline/permutation_importance_top10_per_class.csv
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
import joblib

REPO = Path.cwd()
FEAT_CSV = REPO / 'data' / 'features_aggregated.csv'
MODEL_FILE = REPO / 'models' / 'baseline' / 'rf_baseline.joblib'
LABEL_FILE = REPO / 'models' / 'baseline' / 'label_encoder.joblib'
OUT_CSV = REPO / 'models' / 'baseline' / 'permutation_importance_top10_per_class.csv'

if not FEAT_CSV.exists() or not MODEL_FILE.exists():
    print('Missing features or model. Make sure previous steps ran.')
    raise SystemExit(1)

feat_df = pd.read_csv(FEAT_CSV)
model = joblib.load(MODEL_FILE)
le = joblib.load(LABEL_FILE)

# identify numeric features
excluded = {'file_id', 'species', 'processed_path', 'split', 'provenance'}
features = [c for c in feat_df.columns if c not in excluded]

val_df = feat_df[feat_df['split'] == 'val']
if val_df.empty:
    print('No validation split found in features; aborting.')
    raise SystemExit(1)

X_val = val_df[features].fillna(0).values
y_true = le.transform(val_df['species'].values)

# baseline predictions
y_pred = model.predict(X_val)
classes = le.classes_

# baseline f1 per class
base_f1 = {}
for i, cls in enumerate(classes):
    # f1_score with labels for that class only
    base_f1[cls] = f1_score((y_true == i).astype(int), (y_pred == i).astype(int), average='binary')

results = []

for j, feat in enumerate(features):
    Xp = X_val.copy()
    # permute column j
    rng = np.random.RandomState(42)
    rng.shuffle(Xp[:, j])
    y_perm = model.predict(Xp)
    for i, cls in enumerate(classes):
        perm_f1 = f1_score((y_true == i).astype(int), (y_perm == i).astype(int), average='binary')
        importance = base_f1[cls] - perm_f1
        results.append({'class': cls, 'feature': feat, 'importance': importance})

res_df = pd.DataFrame(results)
# for each class, keep top 10
top_list = []
for cls in res_df['class'].unique():
    sel = res_df[res_df['class'] == cls].sort_values('importance', ascending=False).head(10)
    for _, r in sel.iterrows():
        top_list.append(r)

out_df = pd.DataFrame(top_list)
out_df.to_csv(OUT_CSV, index=False)
print('Wrote permutation importances to', OUT_CSV)
