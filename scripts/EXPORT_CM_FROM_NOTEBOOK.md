# Export Confusion Matrix Data from Notebook

Add this code to your training notebook (e.g., `Final_Random_Forest.ipynb`) after you generate predictions:

```python
import numpy as np
from sklearn.metrics import confusion_matrix

# After making predictions (y_pred = model.predict(X_test))
cm = confusion_matrix(y_test, y_pred)
labels = model.classes_  # or your list of species names

# Save to files
np.save('cm_data.npy', cm)
np.save('cm_labels.npy', labels)

print("✅ Saved confusion matrix data")
print(f"   Shape: {cm.shape}")
print(f"   Labels: {len(labels)}")
```

Then run the script to generate clear visualizations:

```bash
cd /Users/professornirvar/datacap/Georgia-Frog-Identification

# Activate environment with matplotlib/seaborn
source services/frog-api/.venv/bin/activate

# Generate matrices from saved data
python scripts/generate_confusion_matrix_from_arrays.py
```

The script will automatically load `cm_data.npy` and `cm_labels.npy` from the root directory and create publication-ready confusion matrices in `reports/figures/`.

## Alternative: Export as JSON

```python
import json
import numpy as np

# After predictions
cm = confusion_matrix(y_test, y_pred)
labels = model.classes_.tolist()  # Convert to list

# Save as JSON
data = {
    'confusion_matrix': cm.tolist(),
    'labels': labels
}

with open('cm_export.json', 'w') as f:
    json.dump(data, f)

print("✅ Saved: cm_export.json")
```

Then run:
```bash
python scripts/generate_confusion_matrix_simple.py --json cm_export.json
```
