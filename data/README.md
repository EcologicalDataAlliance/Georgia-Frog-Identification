# Data

This directory contains datasets, processed features, and data artifacts for the Georgia Frog Identification project.

## ⚠️ Data Not Included in Git

Most data files are excluded from version control via `.gitignore` due to size constraints. This directory serves as the **standard location** for local data storage.

## Data Sources

### Primary Sources (Cloud Storage)

**Supabase Storage**:
- **Bucket**: `Species Catalog` (public) - Reference audio and images for 15 frog species
- **Bucket**: `frog-user-recordings` (private) - User-uploaded recordings for prediction
- **Database Tables**: 
  - `audio_files` - Metadata for training recordings
  - `predictions` - Top-3 predictions with confidence scores
  - `feedback` - User corrections for model improvement

**External Sources**:
- Xeno-canto: Citizen science recordings
- Macaulay Library: Cornell Lab of Ornithology
- Digital Library of Georgia: Regional recordings

### Species Covered (15 classes)

1. American Bullfrog
2. Barking Treefrog
3. Bird-voiced Treefrog
4. Brimley's Chorus Frog
5. Cope's Gray Treefrog
6. Fowler's Toad
7. Green Treefrog
8. Greenhouse Frog
9. Little Grass Frog
10. Northern Cricket Frog
11. Pig Frog
12. Pine Barrens Treefrog
13. Southern Chorus Frog
14. Southern Leopard Frog
15. Spring Peeper

## Expected Directory Structure

```
data/
├── raw/                          # Original audio files (not committed)
│   ├── american_bullfrog/
│   ├── copes_gray_treefrog/
│   └── ...
│
├── processed/                    # Extracted features (CSV/NPY)
│   ├── features_train.csv
│   ├── features_test.csv
│   ├── X_train.npy
│   ├── X_test.npy
│   ├── y_train.npy
│   └── y_test.npy
│
├── spectrograms/                 # Spectrogram representations
│   └── spectrogram_features.csv
│
├── samples/                      # Small test files (committed for demos)
│   ├── test_audio_1.wav
│   └── test_audio_2.wav
│
└── dataset_manifest.csv          # Metadata: file paths, species, splits
```

## Feature Format

### Audio Features (26 dimensions)
Extracted from 10-second audio clips:

**Spectral Features**:
- `centroid_mean`, `bandwidth_mean`, `rolloff_mean`

**MFCC Features**:
- Means: `mfcc1_mean` through `mfcc13_mean` (13 features)
- Stdevs: `mfcc1_std`, `mfcc3_std`, `mfcc4_std`, `mfcc5_std`, `mfcc7_std`, `mfcc8_std`, `mfcc12_std` (7 features)

**Temporal Features**:
- `zcr_mean`, `rms_mean`, `rms_std`

**Order**: Enforced by `services/frog-api/feature_columns.json`

## Preprocessing Pipeline

1. **Load audio** → Mono conversion
2. **Silence trimming** → `top_db=30`
3. **Best 10s window** → RMS-based scanning with 1s hops
4. **Resample** → 22,050 Hz
5. **Standardize** → Pad/trim to exactly 10 seconds
6. **Pre-emphasis** → 0.97 (optional)
7. **Peak normalize** → 0.98 max amplitude
8. **Feature extraction** → 26-D vector via librosa

See `services/frog-api/main.py` for implementation.

## Data Access

### Query Supabase Metadata
```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table("audio_files").select("*").execute()
```

### Download Sample
```python
# From Supabase Storage
url = f"https://{PROJECT_REF}.supabase.co/storage/v1/object/public/Species Catalog/{species}/{file}"
```

## Data Augmentation (Future)

Planned techniques:
- Time stretching
- Pitch shifting
- Background noise injection
- SpecAugment for spectrograms

## Dataset Statistics

- **Training set**: ~X recordings (distribution per species varies)
- **Test set**: ~Y recordings
- **Validation set**: ~Z recordings
- **Average file size**: ~500 KB (varies by format)
- **Formats**: WAV, MP3, OGG

**Note**: Run `notebooks/data-exploration/database_integration_and_analysis.ipynb` for current statistics.

## Gitignore Patterns

```gitignore
data/raw/**
data/processed/**
data/spectrograms/**
*.wav
*.mp3
*.npy
*.csv
!data/samples/*.wav
!data/dataset_manifest.csv
```
