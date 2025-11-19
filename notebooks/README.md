# Notebooks

This directory contains Jupyter notebooks for data exploration, model development, and experimentation.

## Directory Structure

### `data-exploration/`
Notebooks for analyzing and understanding the dataset.

- **`database_integration_and_analysis.ipynb`** - Supabase integration, audio file metadata exploration, species distribution analysis, and file size outlier detection
- **`audio_data_analysis_sample.ipynb`** - Sample audio analysis and feature extraction demonstrations

### `modeling/`
Model training, evaluation, and comparison notebooks.

- **`Final_Random_Forest.ipynb`** - Production Random Forest model training with calibration, generates confusion matrix and classification reports
- **`Random_Forest (1).ipynb`** - Alternative Random Forest training iteration with evaluation metrics
- **`CNN_f1.ipynb`** - Convolutional Neural Network experiments with F1 score optimization
- **`modeling.ipynb`** - General modeling experiments and baseline comparisons
- **`modeling_updates.ipynb`** - Iterative model improvements and validation accuracy tracking (achieved 0.5714 val accuracy)

### `experiments/`
Experimental approaches and alternative algorithms.

- **`Copy_of_svm_train_improved_py.ipynb`** - SVM classifier experiments with ensemble methods and accuracy comparisons

## Quick Start

### Prerequisites
```bash
pip install jupyter pandas numpy scikit-learn librosa supabase matplotlib seaborn
```

### Running Notebooks
1. Navigate to the repository root
2. Start Jupyter:
   ```bash
   jupyter notebook notebooks/
   ```
3. For Colab notebooks, upload to Google Colab and set Supabase credentials in Secrets

## Key Outputs

- **Confusion Matrices**: Generated in `modeling/` notebooks, saved to `../reports/confusion_matrix_rf.png`
- **Model Artifacts**: Trained models saved to `../services/frog-api/` (e.g., `rf_calibrated_model.joblib`, `scaler.joblib`)
- **Feature Specifications**: `feature_columns.json` defining the 26-dimensional feature vector

## Notebook Workflow

1. **Data Exploration** → Understand dataset composition and quality
2. **Feature Engineering** → Extract 26 audio features (MFCCs, spectral, temporal)
3. **Model Training** → Train and calibrate Random Forest classifier
4. **Evaluation** → Generate metrics, confusion matrices, classification reports
5. **Deployment** → Export models to `services/frog-api/`

## Notes

- Most modeling notebooks expect preprocessed data or Supabase access
- Confusion matrix images are referenced but not committed; regenerate by running evaluation cells
- CNN experiments show progressive validation accuracy improvements documented in printed logs
