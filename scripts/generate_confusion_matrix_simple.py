#!/usr/bin/env python3
"""
Generate Confusion Matrix from Notebook Output
===============================================
Creates a clear confusion matrix visualization from saved predictions or notebook data.

This version works standalone without needing sklearn/joblib installed globally.

Usage:
    python scripts/generate_confusion_matrix_simple.py
    python scripts/generate_confusion_matrix_simple.py --notebook notebooks/modeling/Final_Random_Forest.ipynb
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nInstall with:")
    print("  pip install numpy matplotlib seaborn")
    sys.exit(1)


# Species name mapping for clearer display (15 Georgia frog species)
SPECIES_DISPLAY_NAMES = {
    'american_bullfrog': 'American Bullfrog',
    'american_toad': 'American Toad',
    'bird_voiced_tree_frog': 'Bird-Voiced Tree Frog',
    'copes_gray_treefrog': "Cope's Gray Treefrog",
    'eastern_narrow_mouthed_toad': 'Eastern Narrow-Mouthed Toad',
    'eastern_spadefoot_toad': 'Eastern Spadefoot Toad',
    'fowlers_toad': "Fowler's Toad",
    'green_frog': 'Green Frog',
    'green_tree_frog': 'Green Tree Frog',
    'northern_cricket_frog': 'Northern Cricket Frog',
    'not_frogs': 'Not Frogs',
    'pickerel_frog': 'Pickerel Frog',
    'southern_leopard_frog': 'Southern Leopard Frog',
    'spring_peeper': 'Spring Peeper',
    'upland_chorus_frog': 'Upland Chorus Frog',
}


def clean_species_name(name):
    """Convert species name to display format."""
    name_lower = name.lower().strip()
    if name_lower in SPECIES_DISPLAY_NAMES:
        return SPECIES_DISPLAY_NAMES[name_lower]
    
    # Fallback: clean underscores and title case
    return name.replace('_', ' ').title()


def load_confusion_matrix_from_json(json_path):
    """Load confusion matrix from saved JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    cm = np.array(data['confusion_matrix'])
    labels = data['labels']
    
    return cm, labels


def create_sample_confusion_matrix():
    """
    Create a sample confusion matrix based on known performance.
    This is a placeholder - replace with actual data from notebook.
    """
    # 15 species from the Georgia Frog project (matching API model)
    species = [
        'american_bullfrog', 'american_toad', 'bird_voiced_tree_frog',
        'copes_gray_treefrog', 'eastern_narrow_mouthed_toad', 'eastern_spadefoot_toad',
        'fowlers_toad', 'green_frog', 'green_tree_frog',
        'northern_cricket_frog', 'not_frogs', 'pickerel_frog',
        'southern_leopard_frog', 'spring_peeper', 'upland_chorus_frog'
    ]
    
    # Create a sample 15x15 confusion matrix with realistic patterns
    np.random.seed(42)
    n = len(species)
    cm = np.zeros((n, n), dtype=int)
    
    # Simulate good diagonal performance with some confusion
    for i in range(n):
        total = np.random.randint(20, 40)
        # Strong diagonal (70-95% correct)
        cm[i, i] = int(total * np.random.uniform(0.7, 0.95))
        
        # Distribute remaining among similar species
        remaining = total - cm[i, i]
        if remaining > 0:
            # Add some confusion to nearby species
            confusion_idx = np.random.choice([j for j in range(n) if j != i], 
                                            size=min(3, remaining), replace=False)
            for idx in confusion_idx:
                cm[i, idx] = remaining // len(confusion_idx)
    
    return cm, species


def plot_confusion_matrix(cm, class_labels, output_path, 
                         normalize=False, figsize=(14, 12), fontsize=10):
    """
    Create a clear, publication-ready confusion matrix.
    
    Parameters:
    -----------
    cm : array-like
        Confusion matrix (NxN)
    class_labels : list
        List of class names
    output_path : str
        Path to save the figure
    normalize : bool
        If True, normalize confusion matrix
    figsize : tuple
        Figure size (width, height)
    fontsize : int
        Font size for labels
    """
    cm = np.array(cm)
    
    if normalize:
        # Normalize by row (recall perspective)
        cm_sum = cm.sum(axis=1, keepdims=True)
        cm_sum[cm_sum == 0] = 1  # Avoid division by zero
        cm = cm.astype('float') / cm_sum
        fmt = '.2f'
        cmap = 'Blues'
        title = 'Normalized Confusion Matrix (Recall)'
    else:
        fmt = 'd'
        cmap = 'Greens'
        title = 'Confusion Matrix (Count)'
    
    # Clean class labels for display
    display_labels = [clean_species_name(label) for label in class_labels]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot heatmap
    sns.heatmap(cm, annot=True, fmt=fmt, cmap=cmap, 
                xticklabels=display_labels,
                yticklabels=display_labels,
                cbar_kws={'label': 'Proportion' if normalize else 'Count'},
                ax=ax, linewidths=0.5, linecolor='gray',
                square=True)
    
    # Set labels and title
    ax.set_xlabel('Predicted Label', fontsize=fontsize+2, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=fontsize+2, fontweight='bold')
    ax.set_title(title, fontsize=fontsize+4, fontweight='bold', pad=20)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', 
             rotation_mode='anchor', fontsize=fontsize)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=fontsize)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save figure
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    
    plt.close()


def extract_cm_from_notebook(notebook_path):
    """
    Extract confusion matrix data from Jupyter notebook JSON.
    Looks for saved CM data in notebook outputs.
    """
    try:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)
        
        # Search for confusion matrix in outputs
        for cell in nb.get('cells', []):
            if cell.get('cell_type') != 'code':
                continue
            
            outputs = cell.get('outputs', [])
            for output in outputs:
                # Look for text output containing confusion matrix
                if output.get('output_type') == 'stream':
                    text = ''.join(output.get('text', []))
                    if 'confusion_matrix' in text.lower():
                        print(f"Found CM reference in notebook: {notebook_path}")
                        # TODO: Parse actual matrix data
                        return None, None
        
        print(f"⚠️  No confusion matrix found in notebook outputs")
        return None, None
        
    except Exception as e:
        print(f"❌ Error reading notebook: {e}")
        return None, None


def main():
    parser = argparse.ArgumentParser(
        description='Generate clear confusion matrix visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--notebook', type=str,
                       help='Extract CM from notebook JSON (experimental)')
    parser.add_argument('--json', type=str,
                       help='Load CM from JSON file')
    parser.add_argument('--output', type=str,
                       default='reports/figures/confusion_matrix_clear.png',
                       help='Output path for confusion matrix image')
    parser.add_argument('--figsize', type=int, nargs=2, default=[14, 12],
                       help='Figure size (width height)')
    parser.add_argument('--fontsize', type=int, default=10,
                       help='Font size for labels')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX GENERATOR (Standalone)")
    print("="*80 + "\n")
    
    cm = None
    labels = None
    
    # Try loading from JSON
    if args.json:
        try:
            cm, labels = load_confusion_matrix_from_json(args.json)
            print(f"✅ Loaded confusion matrix from: {args.json}")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
    
    # Try extracting from notebook
    elif args.notebook:
        cm, labels = extract_cm_from_notebook(args.notebook)
    
    # Use sample data if no source provided
    if cm is None:
        print("ℹ️  Using sample confusion matrix")
        print("   (To use real data, run this from your notebook:)")
        print("   np.save('cm_data.npy', confusion_matrix(y_test, y_pred))")
        print("   np.save('cm_labels.npy', model.classes_)")
        print()
        cm, labels = create_sample_confusion_matrix()
    
    # Generate both versions
    print(f"\n📊 Generating confusion matrices...")
    print(f"   Classes: {len(labels)}")
    print(f"   Total samples: {cm.sum()}")
    
    # Count-based matrix
    output_path = Path(args.output)
    plot_confusion_matrix(
        cm, labels, 
        output_path,
        normalize=False,
        figsize=tuple(args.figsize),
        fontsize=args.fontsize
    )
    
    # Normalized matrix
    normalized_path = output_path.parent / (output_path.stem + '_normalized.png')
    plot_confusion_matrix(
        cm, labels,
        normalized_path,
        normalize=True,
        figsize=tuple(args.figsize),
        fontsize=args.fontsize
    )
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  📊 {output_path}")
    print(f"  📊 {normalized_path}")
    print()


if __name__ == '__main__':
    main()
