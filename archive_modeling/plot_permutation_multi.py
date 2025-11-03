#!/usr/bin/env python3
"""Create a single multi-panel figure showing permutation importances for all classes.
Saves to models/baseline/plots/permutation_importance_all_classes.png
"""
from pathlib import Path
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

REPO = Path.cwd()
PERM_CSV = REPO / 'models' / 'baseline' / 'permutation_importance_top10_per_class.csv'
OUT_PNG = REPO / 'models' / 'baseline' / 'plots' / 'permutation_importance_all_classes.png'
OUT_DIR = OUT_PNG.parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not PERM_CSV.exists():
    print('Permutation CSV not found at', PERM_CSV)
    raise SystemExit(1)

perm = pd.read_csv(PERM_CSV)
classes = sorted(perm['class'].unique())
num = len(classes)
cols = 4
rows = math.ceil(num / cols)

sns.set(style='whitegrid')
fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.5, rows * 3.5), constrained_layout=True)
axes = axes.flatten()

for ax in axes[num:]:
    ax.axis('off')

for i, cls in enumerate(classes):
    ax = axes[i]
    sub = perm[perm['class'] == cls].sort_values('importance', ascending=True).tail(10)
    if sub.empty:
        ax.set_title(cls)
        continue
    sns.barplot(x='importance', y='feature', data=sub, ax=ax, palette='magma')
    ax.set_title(cls)
    ax.set_xlabel('Drop in F1')

plt.suptitle('Permutation Importances (top features by class)', fontsize=16)
plt.savefig(OUT_PNG, dpi=200)
print('Wrote multi-panel permutation importance PNG to', OUT_PNG)
