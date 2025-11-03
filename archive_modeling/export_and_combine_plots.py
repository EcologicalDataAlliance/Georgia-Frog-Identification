#!/usr/bin/env python3
"""Export high-res/SVG for global RF importances and create a one-slide PNG combining
global RF importances and the multi-panel permutation importance image.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import seaborn as sns

REPO = Path.cwd()
FI_CSV = REPO / 'models' / 'baseline' / 'feature_importances.csv'
PERM_PNG = REPO / 'models' / 'baseline' / 'plots' / 'permutation_importance_all_classes.png'
OUT_DIR = REPO / 'models' / 'baseline' / 'plots'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# output names
GLOBAL_HIGHRES_PNG = OUT_DIR / 'global_top20_feature_importances_highres.png'
GLOBAL_SVG = OUT_DIR / 'global_top20_feature_importances.svg'
ONE_SLIDE = OUT_DIR / 'one_slide_combined.png'
ONE_SLIDE_HIGHRES = OUT_DIR / 'one_slide_combined_highres.png'

sns.set(style='whitegrid')

if not FI_CSV.exists():
    print('Missing feature importances CSV:', FI_CSV)
    raise SystemExit(1)

fi = pd.read_csv(FI_CSV)
# prepare top20
top20 = fi.head(20).sort_values('importance')

# create high-res PNG and SVG for global plot
fig, ax = plt.subplots(figsize=(12, 14), dpi=200)
sns.barplot(x='importance', y='feature', data=top20, palette='viridis', ax=ax)
ax.set_title('Top 20 RandomForest Feature Importances')
plt.tight_layout()
fig.savefig(GLOBAL_HIGHRES_PNG, dpi=300)
fig.savefig(GLOBAL_SVG)
plt.close(fig)
print('Wrote', GLOBAL_HIGHRES_PNG, 'and', GLOBAL_SVG)

# Now compose one-slide PNG: left=global_highres (resized), right=perm_png (existing)
if not PERM_PNG.exists():
    print('Missing permutation multi-panel PNG:', PERM_PNG)
    raise SystemExit(1)

# open images
left = Image.open(GLOBAL_HIGHRES_PNG)
right = Image.open(PERM_PNG)

# target height = max heights
target_h = max(left.height, right.height)
# scale each to target height while preserving aspect ratio
def scale_to_height(im, h):
    w = int(im.width * (h / im.height))
    return im.resize((w, h), Image.LANCZOS)

left_s = scale_to_height(left, target_h)
right_s = scale_to_height(right, target_h)

# padding between
pad = 40
# composite width
W = left_s.width + pad + right_s.width
H = target_h
composite = Image.new('RGB', (W, H), (255,255,255))
composite.paste(left_s, (0,0))
composite.paste(right_s, (left_s.width + pad, 0))

# save regular and high-res (just save bigger by scaling 2x)
composite.save(ONE_SLIDE)
# highres: upscale by 2x
composite.resize((composite.width*2, composite.height*2), Image.LANCZOS).save(ONE_SLIDE_HIGHRES)

print('Wrote combined one-slide PNGs:', ONE_SLIDE, ONE_SLIDE_HIGHRES)
