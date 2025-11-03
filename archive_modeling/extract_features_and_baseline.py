#!/usr/bin/env python3
"""Extract aggregated audio features for all samples, train a quick RandomForest baseline,
and produce a small augmented sample per underrepresented species.

Outputs:
 - data/features_aggregated.csv
 - models/baseline/rf_baseline.joblib
 - models/baseline/report.md
 - data/augmented/sample/<species>/*.wav

Run from repo root.
"""
import os
import sys
import uuid
import json
import time
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

import librosa
import soundfile as sf

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, f1_score, confusion_matrix
import joblib


REPO_ROOT = Path.cwd()
METADATA_CSV = REPO_ROOT / "metadata_all.csv"
OUT_FEATURES = REPO_ROOT / "data" / "features_aggregated.csv"
AUG_OUT_DIR = REPO_ROOT / "data" / "augmented" / "sample"
MODEL_DIR = REPO_ROOT / "models" / "baseline"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
AUG_OUT_DIR.mkdir(parents=True, exist_ok=True)

SR = 22050


def git_commit():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception:
        commit = "unknown"
    return commit


def extract_features_from_file(wav_path, sr=SR):
    y, sr = librosa.load(wav_path, sr=sr, mono=True)
    # ensure finite
    y = np.nan_to_num(y)

    feats = {}
    # spectral features
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    feats['centroid_mean'] = float(np.mean(centroid))
    feats['centroid_std'] = float(np.std(centroid))

    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    feats['bandwidth_mean'] = float(np.mean(bandwidth))
    feats['bandwidth_std'] = float(np.std(bandwidth))

    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    feats['rolloff_mean'] = float(np.mean(rolloff))
    feats['rolloff_std'] = float(np.std(rolloff))

    rmse = librosa.feature.rms(y=y)
    feats['rms_mean'] = float(np.mean(rmse))
    feats['rms_std'] = float(np.std(rmse))

    zcr = librosa.feature.zero_crossing_rate(y)
    feats['zcr_mean'] = float(np.mean(zcr))
    feats['zcr_std'] = float(np.std(zcr))

    # MFCCs: mean/std for first 13
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for i in range(mfcc.shape[0]):
        feats[f'mfcc{i+1}_mean'] = float(np.mean(mfcc[i]))
        feats[f'mfcc{i+1}_std'] = float(np.std(mfcc[i]))

    return feats


def build_features_table(df):
    rows = []
    for _, r in tqdm(df.iterrows(), total=len(df), desc="extracting features"):
        rel_path = r['processed_path']
        wav_path = REPO_ROOT / Path(rel_path)
        if not wav_path.exists():
            # try normalizing slashes
            wav_path = REPO_ROOT / Path(rel_path.replace('\\', os.sep))
        if not wav_path.exists():
            print(f"WARNING: missing file {wav_path}")
            feats = {}
        else:
            feats = extract_features_from_file(str(wav_path))

        out = {
            'file_id': r['file_id'],
            'species': r['species'],
            'processed_path': str(r['processed_path']),
            'split': r.get('split', ''),
        }
        out.update(feats)
        rows.append(out)

    feat_df = pd.DataFrame(rows)
    return feat_df


def train_and_eval(feat_df):
    le = LabelEncoder()
    feat_df = feat_df.copy()
    # drop rows with NaN features
    numeric_cols = [c for c in feat_df.columns if c not in ('file_id', 'species', 'processed_path', 'split', 'provenance')]
    feat_df[numeric_cols] = feat_df[numeric_cols].fillna(0.0)

    X = feat_df[numeric_cols].values
    y = le.fit_transform(feat_df['species'].values)

    # split indices
    train_idx = feat_df['split'] == 'train'
    val_idx = feat_df['split'] == 'val'
    test_idx = feat_df['split'] == 'test'

    X_train, y_train = X[train_idx.values], y[train_idx.values]
    X_val, y_val = X[val_idx.values], y[val_idx.values]
    X_test, y_test = X[test_idx.values], y[test_idx.values]

    # If any split is empty, fall back to using train/val splitting from available data
    if len(X_val) == 0 and len(X_test) == 0:
        print("No val/test split found — will do a 80/20 split from train rows for quick eval")
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)

    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    preds_val = clf.predict(X_val)
    preds_test = clf.predict(X_test) if len(X_test) > 0 else None

    report = {
        'val_report': classification_report(y_val, preds_val, target_names=le.classes_, output_dict=True),
        'val_macro_f1': float(f1_score(y_val, preds_val, average='macro')),
    }
    if preds_test is not None:
        report['test_report'] = classification_report(y_test, preds_test, target_names=le.classes_, output_dict=True)
        report['test_macro_f1'] = float(f1_score(y_test, preds_test, average='macro'))

    # confusion matrix for val
    report['val_confusion'] = confusion_matrix(y_val, preds_val).tolist()
    if preds_test is not None:
        report['test_confusion'] = confusion_matrix(y_test, preds_test).tolist()

    # save model and label encoder
    joblib.dump(clf, MODEL_DIR / 'rf_baseline.joblib')
    joblib.dump(le, MODEL_DIR / 'label_encoder.joblib')

    return report


def create_augmentation_sample(meta_df, sr=SR):
    train_meta = meta_df[meta_df['split'] == 'train']
    counts = train_meta['species'].value_counts()
    threshold = 30
    under = counts[counts < threshold].index.tolist()
    # if none under threshold, choose bottom 10 species
    if not under:
        under = counts.nsmallest(10).index.tolist()

    created = []
    for sp in under:
        sp_rows = train_meta[train_meta['species'] == sp]
        if sp_rows.empty:
            continue
        row = sp_rows.iloc[0]
        wav_path = REPO_ROOT / Path(row['processed_path'])
        if not wav_path.exists():
            wav_path = REPO_ROOT / Path(row['processed_path'].replace('\\', os.sep))
        y, _ = librosa.load(str(wav_path), sr=sr, mono=True)
        # simple augmentation: pitch shift + small gaussian noise
        # use keyword args for compatibility with different librosa versions
        y_aug = librosa.effects.pitch_shift(y, n_steps=1, sr=sr)
        noise = 0.005 * np.random.randn(len(y_aug))
        y_aug = y_aug + noise

        out_dir = AUG_OUT_DIR / sp
        out_dir.mkdir(parents=True, exist_ok=True)
        out_name = out_dir / f"{row['file_id']}_aug_pitch1_noise.wav"
        sf.write(out_name, y_aug, sr, subtype='PCM_16')
        created.append(str(out_name))

    return created


def main():
    if not METADATA_CSV.exists():
        print(f"metadata_all.csv not found at {METADATA_CSV}")
        sys.exit(1)

    meta = pd.read_csv(METADATA_CSV)
    print(f"Loaded metadata with {len(meta)} rows")

    feat_df = build_features_table(meta)

    # provenance
    prov = {
        'run_id': str(uuid.uuid4()),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'git_commit': git_commit(),
        'script': 'tools/extract_features_and_baseline.py',
    }

    feat_df['provenance'] = json.dumps(prov)
    OUT_FEATURES.parent.mkdir(parents=True, exist_ok=True)
    feat_df.to_csv(OUT_FEATURES, index=False)
    print(f"Wrote features to {OUT_FEATURES}")

    report = train_and_eval(feat_df)

    # write report
    rep_path = MODEL_DIR / 'report.md'
    with open(rep_path, 'w', encoding='utf8') as f:
        f.write('# Baseline report\n\n')
        f.write(f"Run id: {prov['run_id']}\n\n")
        f.write('## Metrics (validation)\n')
        f.write(json.dumps(report.get('val_report', {}), indent=2))
        f.write('\n\n')
        f.write(f"Validation macro-F1: {report.get('val_macro_f1'):.4f}\n\n")
        if 'test_report' in report:
            f.write('## Metrics (test)\n')
            f.write(json.dumps(report.get('test_report', {}), indent=2))
            f.write('\n\n')
            f.write(f"Test macro-F1: {report.get('test_macro_f1'):.4f}\n\n")

    # create augmentation sample
    created = create_augmentation_sample(meta)
    with open(MODEL_DIR / 'augmentation_sample.txt', 'w', encoding='utf8') as f:
        f.write('\n'.join(created))

    print('Baseline training complete. Report and model saved under', MODEL_DIR)
    print('Augmented samples created:', len(created))


if __name__ == '__main__':
    main()
