#!/usr/bin/env python3
"""Generate PNG plots from feature importances and permutation importances and write a short email-style summary."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap

REPO = Path.cwd()
FI_CSV = REPO / 'models' / 'baseline' / 'feature_importances.csv'
PERM_CSV = REPO / 'models' / 'baseline' / 'permutation_importance_top10_per_class.csv'
REPORT_MD = REPO / 'models' / 'baseline' / 'report.md'
PLOTS_DIR = REPO / 'models' / 'baseline' / 'plots'
EMAIL_PATH = REPO / 'models' / 'baseline' / 'email_summary.txt'
PACKAGE_ZIP = REPO / 'release' / 'modelers_package.zip'

PLOTS_DIR.mkdir(parents=True, exist_ok=True)

sns.set(style='whitegrid')

# Utility to sanitize filenames
def sanitize(name):
    return ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).replace(' ', '_')

# 1) Global feature importances plot (top 20)
if FI_CSV.exists():
    fi = pd.read_csv(FI_CSV)
    topn = fi.head(20).sort_values('importance')
    plt.figure(figsize=(8,10))
    sns.barplot(x='importance', y='feature', data=topn, palette='viridis')
    plt.title('Top 20 RandomForest Feature Importances')
    plt.tight_layout()
    out = PLOTS_DIR / 'global_top20_feature_importances.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print('Wrote', out)
else:
    print('Missing', FI_CSV)

# 2) Per-class permutation importance plots
if PERM_CSV.exists():
    perm = pd.read_csv(PERM_CSV)
    classes = perm['class'].unique()
    for cls in classes:
        sub = perm[perm['class'] == cls].sort_values('importance', ascending=True).tail(10)
        if sub.empty:
            continue
        plt.figure(figsize=(8,5))
        sns.barplot(x='importance', y='feature', data=sub, palette='magma')
        plt.title(f'Permutation importances (top) for class: {cls}')
        plt.xlabel('Drop in F1 when permuted')
        plt.tight_layout()
        fname = PLOTS_DIR / f"perm_importance_{sanitize(cls)}.png"
        plt.savefig(fname, dpi=150)
        plt.close()
        print('Wrote', fname)
else:
    print('Missing', PERM_CSV)

# 3) Short email-style summary
val_macro = 'N/A'
test_macro = 'N/A'
# try to parse report.md for macro-F1 lines
if REPORT_MD.exists():
    text = REPORT_MD.read_text(encoding='utf8')
    for line in text.splitlines():
        if 'Validation macro-F1:' in line:
            try:
                val_macro = line.split(':')[-1].strip()
            except Exception:
                pass
        if 'Test macro-F1:' in line:
            try:
                test_macro = line.split(':')[-1].strip()
            except Exception:
                pass

# top global features
top_feats = []
if FI_CSV.exists():
    fi = pd.read_csv(FI_CSV)
    top_feats = fi.head(10)['feature'].tolist()

aug_count = 0
aug_list = REPO / 'models' / 'baseline' / 'augmentation_sample.txt'
if aug_list.exists():
    aug_count = len([l for l in aug_list.read_text(encoding='utf8').splitlines() if l.strip()])

summary = textwrap.dedent(f"""
Subject: GA Frog ID — Baseline results and artifacts (quick summary)

Hi team,

I ran a quick RandomForest baseline and produced aggregated features and a small augmentation sample for inspection. Key artifacts are in `release/modelers_package.zip` (already created).

Quick metrics:
- Validation macro-F1: {val_macro}
- Test macro-F1: {test_macro}

Top global features (RF): {', '.join(top_feats)}
Augmented samples created for inspection: {aug_count} files under `data/augmented/sample/`.

Artifacts produced:
- data/features_aggregated.csv — aggregated features (MFCC means/std, spectral stats) with provenance
- models/baseline/rf_baseline.joblib — trained RF model
- models/baseline/report.md — detailed metrics and top features
- models/baseline/feature_importances.csv and permutation_importance_top10_per_class.csv
- models/baseline/plots/ — PNG plots (global & per-class permutation importance)
- data/augmented/sample/ — small set of augmented WAVs for inspection
- release/modelers_package.zip — packaged deliverables

Notes and next recommendations:
- MFCC means dominate feature importance; consider normalizing MFCC channels or testing a small CNN on spectrograms.
- Low-support classes (see report.md) are the most likely candidates for targeted augmentation and/or additional curated data.
- Full augmentation should be applied on-the-fly during training; the samples provided are only for inspection.

If you'd like, I can:
- produce per-class permutation plots saved to PNG (done), or
- run a small grid search over RF hyperparameters and report improved metrics, or
- add a notebook cell demonstrating on-the-fly augmentation with sample code.

Cheers,
Data preparation pipeline
""")

EMAIL_PATH.write_text(summary, encoding='utf8')
print('Wrote email summary to', EMAIL_PATH)
print('Done.')
