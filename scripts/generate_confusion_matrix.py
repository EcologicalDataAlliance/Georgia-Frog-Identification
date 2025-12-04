#!/usr/bin/env python3
"""
Generate Confusion Matrix with Clear Class Labels
===================================================
Creates a publication-ready confusion matrix visualization from trained RF model.

Usage:
    python scripts/generate_confusion_matrix.py
    python scripts/generate_confusion_matrix.py --model path/to/model.joblib --data path/to/test.csv
"""

import argparse
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from pathlib import Path


# Species name mapping for clearer display
SPECIES_DISPLAY_NAMES = {
    'american_bullfrog': 'American Bullfrog',
    'barking_treefrog': 'Barking Treefrog',
    'bird_voiced_treefrog': 'Bird-voiced Treefrog',
    'brimleys_chorus_frog': "Brimley's Chorus Frog",
    'copes_gray_treefrog': "Cope's Gray Treefrog",
    'fowlers_toad': "Fowler's Toad",
    'green_treefrog': 'Green Treefrog',
    'greenhouse_frog': 'Greenhouse Frog',
    'little_grass_frog': 'Little Grass Frog',
    'northern_cricket_frog': 'Northern Cricket Frog',
    'pig_frog': 'Pig Frog',
    'pine_barrens_treefrog': 'Pine Barrens Treefrog',
    'southern_chorus_frog': 'Southern Chorus Frog',
    'southern_leopard_frog': 'Southern Leopard Frog',
    'spring_peeper': 'Spring Peeper',
    # Add alternative formats
    'american_toad': 'American Toad',
    'eastern_spadefoot_toad': 'Eastern Spadefoot',
    'upland_chorus_frog': 'Upland Chorus Frog',
    'pickerel_frog': 'Pickerel Frog',
}


def load_model_and_scaler(model_path, scaler_path):
    """Load the trained model and scaler."""
    print(f"Loading model from: {model_path}")
    model = joblib.load(model_path)
    
    print(f"Loading scaler from: {scaler_path}")
    scaler = joblib.load(scaler_path)
    
    return model, scaler


def load_test_data(data_path):
    """Load test data from CSV or generate from saved split."""
    if data_path.endswith('.csv'):
        print(f"Loading test data from: {data_path}")
        df = pd.read_csv(data_path)
        
        # Assume last column is target, rest are features
        X_test = df.iloc[:, :-1].values
        y_test = df.iloc[:, -1].values
    else:
        raise ValueError("Only CSV format supported. Please provide test data as CSV.")
    
    return X_test, y_test


def clean_species_name(name):
    """Convert species name to display format."""
    if name in SPECIES_DISPLAY_NAMES:
        return SPECIES_DISPLAY_NAMES[name]
    
    # Fallback: clean underscores and title case
    return name.replace('_', ' ').title()


def plot_confusion_matrix(y_true, y_pred, class_labels, output_path, 
                         normalize=False, figsize=(14, 12), fontsize=10):
    """
    Create a clear, publication-ready confusion matrix.
    
    Parameters:
    -----------
    y_true : array-like
        True labels
    y_pred : array-like
        Predicted labels
    class_labels : list
        List of class names
    output_path : str
        Path to save the figure
    normalize : bool
        If True, normalize confusion matrix (default: False)
    figsize : tuple
        Figure size (width, height)
    fontsize : int
        Font size for labels
    """
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fmt = '.2f'
        cmap = 'Blues'
        title = 'Normalized Confusion Matrix'
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
                cbar_kws={'label': 'Normalized' if normalize else 'Count'},
                ax=ax, linewidths=0.5, linecolor='gray')
    
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
    print(f"✅ Saved confusion matrix to: {output_path}")
    
    plt.close()


def generate_classification_report(y_true, y_pred, class_labels, output_path=None):
    """Generate and optionally save classification report."""
    # Clean labels for report
    target_names = [clean_species_name(label) for label in class_labels]
    
    # Generate report
    report = classification_report(y_true, y_pred, target_names=target_names, 
                                   digits=3, zero_division=0)
    
    print("\n" + "="*80)
    print("CLASSIFICATION REPORT")
    print("="*80)
    print(report)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_true, y_pred)
    print(f"\nOverall Accuracy: {accuracy:.3f}")
    
    # Save to file if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CLASSIFICATION REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(report)
            f.write(f"\n\nOverall Accuracy: {accuracy:.3f}\n")
        print(f"✅ Saved classification report to: {output_path}")
    
    return accuracy


def main():
    parser = argparse.ArgumentParser(
        description='Generate confusion matrix with clear class labels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default paths (services/frog-api)
  python scripts/generate_confusion_matrix.py
  
  # Specify custom model and data
  python scripts/generate_confusion_matrix.py \\
      --model models/rf_model.joblib \\
      --data data/processed/test_set.csv
  
  # Generate normalized matrix
  python scripts/generate_confusion_matrix.py --normalize
  
  # Custom output location
  python scripts/generate_confusion_matrix.py \\
      --output reports/figures/custom_cm.png
        """
    )
    
    parser.add_argument('--model', type=str, 
                       default='services/frog-api/rf_calibrated_model.joblib',
                       help='Path to trained model (.joblib)')
    parser.add_argument('--scaler', type=str,
                       default='services/frog-api/scaler.joblib',
                       help='Path to feature scaler (.joblib)')
    parser.add_argument('--data', type=str,
                       help='Path to test data CSV (features + target)')
    parser.add_argument('--output', type=str,
                       default='reports/figures/confusion_matrix_clear.png',
                       help='Output path for confusion matrix image')
    parser.add_argument('--normalize', action='store_true',
                       help='Normalize confusion matrix (show percentages)')
    parser.add_argument('--figsize', type=int, nargs=2, default=[14, 12],
                       help='Figure size (width height)')
    parser.add_argument('--fontsize', type=int, default=10,
                       help='Font size for labels')
    parser.add_argument('--report', type=str,
                       default='reports/classification_report.txt',
                       help='Output path for classification report')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("CONFUSION MATRIX GENERATOR")
    print("="*80 + "\n")
    
    # Load model and scaler
    try:
        model, scaler = load_model_and_scaler(args.model, args.scaler)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure model files exist:")
        print(f"  - {args.model}")
        print(f"  - {args.scaler}")
        return
    
    # Load or prompt for test data
    if args.data:
        try:
            X_test, y_test = load_test_data(args.data)
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            return
    else:
        print("❌ No test data provided.")
        print("\nPlease provide test data using --data flag:")
        print("  python scripts/generate_confusion_matrix.py --data data/processed/test_set.csv")
        print("\nTest data CSV should have features in columns and species labels in the last column.")
        return
    
    # Get class labels from model
    if hasattr(model, 'classes_'):
        class_labels = model.classes_
    else:
        # Extract unique labels from test set
        class_labels = np.unique(y_test)
    
    print(f"\nTest set: {len(y_test)} samples")
    print(f"Classes: {len(class_labels)} species")
    
    # Scale features
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    print("\nGenerating predictions...")
    y_pred = model.predict(X_test_scaled)
    
    # Generate confusion matrix
    print(f"\nCreating confusion matrix...")
    plot_confusion_matrix(
        y_test, y_pred, class_labels, 
        args.output, 
        normalize=args.normalize,
        figsize=tuple(args.figsize),
        fontsize=args.fontsize
    )
    
    # Generate both normalized and count versions
    if not args.normalize:
        normalized_output = str(Path(args.output).parent / 
                               (Path(args.output).stem + '_normalized.png'))
        print(f"\nCreating normalized confusion matrix...")
        plot_confusion_matrix(
            y_test, y_pred, class_labels, 
            normalized_output, 
            normalize=True,
            figsize=tuple(args.figsize),
            fontsize=args.fontsize
        )
    
    # Generate classification report
    generate_classification_report(y_test, y_pred, class_labels, args.report)
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  📊 {args.output}")
    if not args.normalize:
        print(f"  📊 {normalized_output}")
    print(f"  📄 {args.report}")
    print()


if __name__ == '__main__':
    main()
