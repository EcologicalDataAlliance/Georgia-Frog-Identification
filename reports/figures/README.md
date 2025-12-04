# Reports - Figures Directory

This directory contains visualizations and performance metrics from the Georgia Frog Identification project.

## Confusion Matrix

### 📊 Primary Files

**`confusion_matrix_Random_Forest_Smote_Tuned.png`** (40 KB)
- Heatmap visualization of Random Forest model performance
- Generated from: `notebooks/modeling/Final_Random_Forest.ipynb`
- Overall accuracy: **86.2%**
- Macro F1-score: **0.861**
- Test set: 412 samples across 15 species

**`confusion_matrix_analysis.md`** (4.8 KB)
- Comprehensive analysis document explaining:
  - Best performing species (Upland Chorus Frog, American Toad, Pickerel Frog, Green Tree Frog)
  - Species needing improvement (Fowler's Toad, Eastern Spadefoot, Southern Leopard Frog)
  - Confusion patterns between acoustically similar species
  - Feature drivers and recommendations
- Read this for detailed interpretation of the confusion matrix

## Other Visualizations

**`distrubution_chart.png`** (71 KB)
- Species distribution analysis chart

**`Amphibians_USA_total_richness_large.jpg`** (209 KB)
- Geographic richness map for amphibians in the United States

---

## Quick Access Guide

### For Presentations
Use `confusion_matrix_Random_Forest_Smote_Tuned.png` directly in slides or posters.

### For Deep Analysis
Read `confusion_matrix_analysis.md` for:
- Performance insights by species
- Acoustic confusion patterns
- Model architecture details
- Recommendations for improvement

### For Regeneration
Run cells in `notebooks/modeling/Final_Random_Forest.ipynb`:
```python
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Greens")
plt.title("Confusion Matrix - Random Forest")
plt.savefig("reports/figures/confusion_matrix_Random_Forest_Smote_Tuned.png", dpi=150)
```

---

## Key Performance Highlights

| Metric | Value |
|--------|-------|
| Overall Accuracy | 86.2% |
| Macro F1-Score | 0.861 |
| Best Species (F1) | Eastern Spadefoot (0.98), Green Tree Frog (0.97+) |
| Most Confused Pair | American Toad ↔ Fowler's Toad |

**Target Goals:**
- Top-1 Accuracy: >85% ✅ **ACHIEVED**
- Top-3 Accuracy: >95% (pending verification)

---

## Related Files

- **Model artifacts:** `services/frog-api/rf_calibrated_model.joblib`
- **Training notebook:** `notebooks/modeling/Final_Random_Forest.ipynb`
- **Feature specification:** `services/frog-api/feature_columns.json`
- **API documentation:** `services/frog-api/README.md`
