#!/usr/bin/env python3
"""Training script for RandomForest baseline moved into a separate modeling folder.

Usage: run this from the repo root or from the modeling folder. It expects
`data/features_aggregated.csv` to exist (produced by the extractor).

This file intentionally keeps modeling artifacts inside `modeling/models/` so
the data-prep project remains clean.
"""
import os
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, f1_score, confusion_matrix


REPO_ROOT = Path.cwd()
FEATURES_CSV = REPO_ROOT / 'data' / 'features_aggregated.csv'
OUT_DIR = REPO_ROOT / 'modeling' / 'models'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def train_and_eval(feat_df, n_estimators=200, max_depth=None, n_jobs=-1, random_state=42):
    le = LabelEncoder()
    feat_df = feat_df.copy()
    numeric_cols = [c for c in feat_df.columns if c not in ('file_id', 'species', 'processed_path', 'split', 'provenance')]
    feat_df[numeric_cols] = feat_df[numeric_cols].fillna(0.0)

    X = feat_df[numeric_cols].values
    y = le.fit_transform(feat_df['species'].values)

    train_idx = feat_df['split'] == 'train'
    val_idx = feat_df['split'] == 'val'
    test_idx = feat_df['split'] == 'test'

    X_train, y_train = X[train_idx.values], y[train_idx.values]
    X_val, y_val = X[val_idx.values], y[val_idx.values]
    X_test, y_test = X[test_idx.values], y[test_idx.values]

    if len(X_val) == 0 and len(X_test) == 0:
        from sklearn.model_selection import train_test_split
        try:
            X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=random_state, stratify=y_train)
        except Exception:
            X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=random_state)

    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state, n_jobs=n_jobs)
    clf.fit(X_train, y_train)

    preds_val = clf.predict(X_val)
    preds_test = clf.predict(X_test) if len(X_test) > 0 else None

    all_labels = list(range(len(le.classes_)))
    report = {
        'val_report': classification_report(y_val, preds_val, labels=all_labels, target_names=le.classes_, output_dict=True, zero_division=0),
        'val_macro_f1': float(f1_score(y_val, preds_val, average='macro')),
    }
    if preds_test is not None:
        report['test_report'] = classification_report(y_test, preds_test, labels=all_labels, target_names=le.classes_, output_dict=True, zero_division=0)
        report['test_macro_f1'] = float(f1_score(y_test, preds_test, average='macro'))

    report['val_confusion'] = confusion_matrix(y_val, preds_val).tolist()
    if preds_test is not None:
        report['test_confusion'] = confusion_matrix(y_test, preds_test).tolist()

    # save models inside modeling/ so data-prep repo remains clean
    joblib.dump(clf, OUT_DIR / 'rf_baseline.joblib')
    joblib.dump(le, OUT_DIR / 'label_encoder.joblib')

    rep_path = OUT_DIR / 'report.md'
    with open(rep_path, 'w', encoding='utf8') as f:
        f.write('# Baseline report\n\n')
        f.write(json.dumps(report, indent=2))

    return report


def main():
    if not FEATURES_CSV.exists():
        print('Features CSV not found at', FEATURES_CSV)
        return
    df = pd.read_csv(FEATURES_CSV)
    print('Loaded features with', len(df), 'rows')
    report = train_and_eval(df)
    print('Training complete. Models saved under', OUT_DIR)


if __name__ == '__main__':
    main()
