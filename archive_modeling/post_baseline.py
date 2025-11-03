#!/usr/bin/env python3
"""Post-baseline tasks: compute feature importances and expand augmentation sample.

- models/baseline/feature_importances.csv
- update models/baseline/report.md with top features
- create 3 augmented variants per underrepresented species and update augmentation_sample.txt

Run from repo root.
"""
import os
import sys
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import soundfile as sf
import librosa

REPO_ROOT = Path.cwd()
FEATURE_CSV = REPO_ROOT / 'data' / 'features_aggregated.csv'
METADATA_CSV = REPO_ROOT / 'metadata_all.csv'
MODEL_DIR = REPO_ROOT / 'models' / 'baseline'
AUG_DIR = REPO_ROOT / 'data' / 'augmented' / 'sample'
MODEL_FILE = MODEL_DIR / 'rf_baseline.joblib'
LABEL_FILE = MODEL_DIR / 'label_encoder.joblib'
AUG_LIST = MODEL_DIR / 'augmentation_sample.txt'
FEATURE_IMP_CSV = MODEL_DIR / 'feature_importances.csv'

SR = 22050


def compute_feature_importances():
    if not FEATURE_CSV.exists():
        print('features CSV missing:', FEATURE_CSV)
        return None
    if not MODEL_FILE.exists():
        print('model file missing:', MODEL_FILE)
        return None

    feat_df = pd.read_csv(FEATURE_CSV)
    # identify numeric feature columns
    excluded = {'file_id', 'species', 'processed_path', 'split', 'provenance'}
    numeric_cols = [c for c in feat_df.columns if c not in excluded]

    model = joblib.load(MODEL_FILE)
    try:
        importances = model.feature_importances_
    except Exception as e:
        print('Model has no feature_importances_', e)
        return None

    fi = pd.DataFrame({'feature': numeric_cols, 'importance': importances})
    fi = fi.sort_values('importance', ascending=False)
    fi.to_csv(FEATURE_IMP_CSV, index=False)
    print('Wrote feature importances to', FEATURE_IMP_CSV)

    # append top features to report.md
    top = fi.head(20)
    rep = MODEL_DIR / 'report.md'
    with open(rep, 'a', encoding='utf8') as f:
        f.write('\n\n## Top features (by importance)\n')
        for feat, imp in zip(top['feature'], top['importance']):
            f.write(f"- {feat}: {imp:.6f}\n")
    print('Appended top features to', rep)
    return fi


def expand_augmentation_sample(threshold=30, variants_per=3):
    if not METADATA_CSV.exists():
        print('metadata missing:', METADATA_CSV)
        return []
    meta = pd.read_csv(METADATA_CSV)
    train_meta = meta[meta['split'] == 'train']
    counts = train_meta['species'].value_counts()
    under = counts[counts < threshold].index.tolist()
    if not under:
        under = counts.nsmallest(10).index.tolist()

    created = []
    for sp in under:
        sp_rows = train_meta[train_meta['species'] == sp]
        if sp_rows.empty:
            continue
        rows = sp_rows.sample(n=min(len(sp_rows), variants_per), random_state=42)
        for i, (_, row) in enumerate(rows.iterrows()):
            wav_path = REPO_ROOT / Path(row['processed_path'])
            if not wav_path.exists():
                wav_path = REPO_ROOT / Path(row['processed_path'].replace('\\', os.sep))
            y, _ = librosa.load(str(wav_path), sr=SR, mono=True)
            # create 3 variant types per selected row
            variants = []
            # 1: mild pitch up 0.5
            v1 = librosa.effects.pitch_shift(y, n_steps=0.5, sr=SR)
            variants.append(('p_up0.5', v1))
            # 2: mild pitch down 0.5 + noise
            v2 = librosa.effects.pitch_shift(y, n_steps=-0.5, sr=SR)
            v2 = v2 + 0.004 * np.random.randn(len(v2))
            variants.append(('p_dn0.5_n', v2))
            # 3: time-stretch slight (0.95) + noise
            try:
                v3 = librosa.effects.time_stretch(y, rate=0.95)
                # pad/truncate to original length
                if len(v3) < len(y):
                    v3 = np.pad(v3, (0, len(y) - len(v3)))
                else:
                    v3 = v3[:len(y)]
            except Exception:
                # fallback: slight roll of original
                v3 = np.roll(y, 50)
            v3 = v3 + 0.003 * np.random.randn(len(v3))
            variants.append(('ts095_n', v3))

            out_dir = AUG_DIR / sp
            out_dir.mkdir(parents=True, exist_ok=True)
            for tag, arr in variants:
                out_name = out_dir / f"{row['file_id']}_aug_{tag}.wav"
                sf.write(out_name, arr, SR, subtype='PCM_16')
                created.append(str(out_name))

    # write augmentation list (overwrite) with new set
    AUG_DIR.parent.mkdir(parents=True, exist_ok=True)
    with open(AUG_LIST, 'w', encoding='utf8') as f:
        f.write('\n'.join(created))

    print(f'Created {len(created)} augmented samples for {len(under)} species')
    return created


def main():
    fi = compute_feature_importances()
    created = expand_augmentation_sample()
    # mark todo complete by writing small provenance note
    prov_note = {'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'), 'created_augmented_count': len(created)}
    with open(MODEL_DIR / 'post_baseline_provenance.json', 'w', encoding='utf8') as f:
        json.dump(prov_note, f, indent=2)
    print('Post-baseline tasks done.')


if __name__ == '__main__':
    main()
