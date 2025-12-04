#!/usr/bin/env python3
"""
Generate Confusion Matrix from Saved Arrays
============================================
Load confusion matrix from .npy files exported from notebook.

Usage:
    # From notebook, run:
    # np.save('cm_data.npy', confusion_matrix(y_test, y_pred))
    # np.save('cm_labels.npy', model.classes_)
    
    # Then generate visualization:
    python scripts/generate_confusion_matrix_from_arrays.py
"""

import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("\nRun from backend environment:")
    print("  cd services/frog-api && source .venv/bin/activate")
    print("  python ../../scripts/generate_confusion_matrix_from_arrays.py")
    sys.exit(1)


# Import the plotting function from the simple script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cm_simple", 
    Path(__file__).parent / "generate_confusion_matrix_simple.py"
)
cm_simple = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm_simple)


def main():
    print("\n" + "="*80)
    print("CONFUSION MATRIX FROM SAVED ARRAYS")
    print("="*80 + "\n")
    
    # Look for .npy files
    cm_path = Path('cm_data.npy')
    labels_path = Path('cm_labels.npy')
    
    if not cm_path.exists():
        print(f"❌ File not found: {cm_path}")
        print("\nExport from your notebook:")
        print("  np.save('cm_data.npy', confusion_matrix(y_test, y_pred))")
        print("  np.save('cm_labels.npy', model.classes_)")
        return
    
    if not labels_path.exists():
        print(f"❌ File not found: {labels_path}")
        print("\nExport from your notebook:")
        print("  np.save('cm_labels.npy', model.classes_)")
        return
    
    # Load data
    print(f"📂 Loading: {cm_path}")
    cm = np.load(cm_path)
    
    print(f"📂 Loading: {labels_path}")
    labels = np.load(labels_path, allow_pickle=True)
    
    print(f"\n✅ Loaded confusion matrix")
    print(f"   Shape: {cm.shape}")
    print(f"   Classes: {len(labels)}")
    print(f"   Total samples: {cm.sum()}")
    
    # Generate visualizations
    print(f"\n📊 Generating confusion matrices...")
    
    output_base = Path('reports/figures/confusion_matrix_clear')
    
    # Count-based
    cm_simple.plot_confusion_matrix(
        cm, labels,
        f"{output_base}.png",
        normalize=False,
        figsize=(14, 12),
        fontsize=10
    )
    
    # Normalized
    cm_simple.plot_confusion_matrix(
        cm, labels,
        f"{output_base}_normalized.png",
        normalize=True,
        figsize=(14, 12),
        fontsize=10
    )
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print(f"\nFiles in reports/figures/:")
    print(f"  📊 confusion_matrix_clear.png")
    print(f"  📊 confusion_matrix_clear_normalized.png")
    print()


if __name__ == '__main__':
    main()
