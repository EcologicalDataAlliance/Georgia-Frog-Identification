# Folder Setup Guide

This guide explains how to create the folder structure for the Georgia Frog Identification project.

## Table of Contents
- [Quick Setup](#quick-setup)
- [Manual Setup](#manual-setup)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Folder Structure Overview](#folder-structure-overview)

## Quick Setup

### Using the Setup Script (Recommended)

Run the automated setup script to create all necessary folders:

```bash
# On Linux/macOS
bash scripts/setup_folders.sh

# On Windows (PowerShell)
.\scripts\setup_folders.ps1

# On Windows (Command Prompt)
scripts\setup_folders.bat
```

This will create all folders defined in the project structure.

## Manual Setup

If you prefer to create folders manually or need to create individual folders:

### Linux/macOS

```bash
# Create a single folder
mkdir folder_name

# Create nested folders (creates parent folders if they don't exist)
mkdir -p path/to/nested/folder

# Create multiple folders at once
mkdir folder1 folder2 folder3

# Example: Create the backend structure
mkdir -p backend/data_mining/scrapers
mkdir -p backend/data_mining/validators
mkdir -p backend/data_mining/pipelines
```

### Windows (Command Prompt)

```cmd
# Create a single folder
mkdir folder_name

# Create nested folders
mkdir path\to\nested\folder

# Create multiple folders (use separate commands)
mkdir folder1
mkdir folder2
mkdir folder3

# Example: Create the backend structure
mkdir backend\data_mining\scrapers
mkdir backend\data_mining\validators
mkdir backend\data_mining\pipelines
```

### Windows (PowerShell)

```powershell
# Create a single folder
New-Item -ItemType Directory -Path "folder_name"

# Or use the alias
mkdir folder_name

# Create nested folders
New-Item -ItemType Directory -Force -Path "path/to/nested/folder"

# Create multiple folders at once
@("folder1", "folder2", "folder3") | ForEach-Object { New-Item -ItemType Directory -Path $_ }
```

## Platform-Specific Instructions

### Creating the Full Project Structure

#### Linux/macOS

```bash
# Backend structure
mkdir -p backend/data_mining/{scrapers,validators,pipelines}
mkdir -p backend/database/{models,migrations,queries}
mkdir -p backend/audio_processing/{preprocessing,features,segmentation,augmentation}
mkdir -p backend/ml_models/{architectures,training,evaluation,inference}
mkdir -p backend/api/{routes,middleware,serializers}
mkdir -p backend/utils

# Data structure
mkdir -p data/{raw,processed,models,exports}

# Notebooks structure
mkdir -p notebooks/{exploratory,modeling,evaluation}

# Additional directories
mkdir -p docker
mkdir -p tests
mkdir -p scripts
mkdir -p docs
```

#### Windows (Command Prompt)

```cmd
:: Backend structure
mkdir backend\data_mining\scrapers
mkdir backend\data_mining\validators
mkdir backend\data_mining\pipelines
mkdir backend\database\models
mkdir backend\database\migrations
mkdir backend\database\queries
mkdir backend\audio_processing\preprocessing
mkdir backend\audio_processing\features
mkdir backend\audio_processing\segmentation
mkdir backend\audio_processing\augmentation
mkdir backend\ml_models\architectures
mkdir backend\ml_models\training
mkdir backend\ml_models\evaluation
mkdir backend\ml_models\inference
mkdir backend\api\routes
mkdir backend\api\middleware
mkdir backend\api\serializers
mkdir backend\utils

:: Data structure
mkdir data\raw
mkdir data\processed
mkdir data\models
mkdir data\exports

:: Notebooks structure
mkdir notebooks\exploratory
mkdir notebooks\modeling
mkdir notebooks\evaluation

:: Additional directories
mkdir docker
mkdir tests
mkdir scripts
mkdir docs
```

#### Windows (PowerShell)

```powershell
# Define folder structure
$folders = @(
    "backend/data_mining/scrapers",
    "backend/data_mining/validators",
    "backend/data_mining/pipelines",
    "backend/database/models",
    "backend/database/migrations",
    "backend/database/queries",
    "backend/audio_processing/preprocessing",
    "backend/audio_processing/features",
    "backend/audio_processing/segmentation",
    "backend/audio_processing/augmentation",
    "backend/ml_models/architectures",
    "backend/ml_models/training",
    "backend/ml_models/evaluation",
    "backend/ml_models/inference",
    "backend/api/routes",
    "backend/api/middleware",
    "backend/api/serializers",
    "backend/utils",
    "data/raw",
    "data/processed",
    "data/models",
    "data/exports",
    "notebooks/exploratory",
    "notebooks/modeling",
    "notebooks/evaluation",
    "docker",
    "tests",
    "scripts",
    "docs"
)

# Create all folders
$folders | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ }
```

## Folder Structure Overview

After setup, your project should have this structure:

```
Georgia-Frog-Identification/
├── backend/
│   ├── data_mining/          # Web scrapers and data collection
│   │   ├── scrapers/         # Individual site scrapers
│   │   ├── validators/       # Data quality validation
│   │   └── pipelines/        # ETL processes
│   ├── database/             # Database models and migrations
│   │   ├── models/           # SQLAlchemy models
│   │   ├── migrations/       # Database migrations
│   │   └── queries/          # Complex queries and views
│   ├── audio_processing/     # Audio analysis and feature extraction
│   │   ├── preprocessing/    # Noise reduction, normalization
│   │   ├── features/         # MFCC, spectrogram extraction
│   │   ├── segmentation/     # Call detection and segmentation
│   │   └── augmentation/     # Data augmentation techniques
│   ├── ml_models/            # Machine learning components
│   │   ├── architectures/    # Model definitions (CNN, RNN)
│   │   ├── training/         # Training scripts and utilities
│   │   ├── evaluation/       # Model evaluation and metrics
│   │   └── inference/        # Prediction and serving
│   ├── api/                  # REST API endpoints
│   │   ├── routes/           # API route definitions
│   │   ├── middleware/       # Authentication, logging
│   │   └── serializers/      # Data serialization
│   └── utils/                # Shared utilities and helpers
├── frontend/                 # React dashboard (already exists)
├── data/                     # Data storage and management
│   ├── raw/                  # Raw audio files and metadata
│   ├── processed/            # Processed features and spectrograms
│   ├── models/               # Trained model artifacts
│   └── exports/              # Data exports and reports
├── notebooks/                # Jupyter notebooks for analysis
│   ├── exploratory/          # Data exploration and EDA
│   ├── modeling/             # Model development and testing
│   └── evaluation/           # Performance analysis
├── docker/                   # Container configurations
├── tests/                    # Test suites
├── scripts/                  # Utility scripts and automation
└── docs/                     # Documentation and guides
```

## Verifying Your Setup

After creating folders, verify the structure:

### Linux/macOS
```bash
# Show directory tree (if tree is installed)
tree -L 3 -d

# Or use find
find . -type d -maxdepth 3 | sort
```

### Windows (Command Prompt)
```cmd
# Show directory tree
tree /F /A
```

### Windows (PowerShell)
```powershell
# Show directory tree
Get-ChildItem -Directory -Recurse -Depth 2 | Select-Object FullName
```

## Adding .gitkeep Files

Empty folders won't be tracked by Git. To preserve the folder structure, add `.gitkeep` files:

### Linux/macOS
```bash
# Add .gitkeep to all empty directories
find . -type d -empty -not -path "./.git/*" -exec touch {}/.gitkeep \;
```

### Windows (PowerShell)
```powershell
# Add .gitkeep to all empty directories
Get-ChildItem -Directory -Recurse | 
    Where-Object { (Get-ChildItem $_.FullName -Force).Count -eq 0 } |
    ForEach-Object { New-Item -ItemType File -Path "$($_.FullName)\.gitkeep" }
```

### Windows (Command Prompt)
```cmd
:: Manually create .gitkeep in empty folders
echo. > backend\data_mining\scrapers\.gitkeep
echo. > backend\data_mining\validators\.gitkeep
:: ... repeat for other empty folders
```

## Troubleshooting

### Permission Denied Errors
If you get permission errors:

**Linux/macOS:**
```bash
# Use sudo for system-wide permissions (not recommended for project folders)
sudo mkdir folder_name

# Or change ownership
sudo chown -R $USER:$USER .
```

**Windows:**
- Run Command Prompt or PowerShell as Administrator
- Right-click → "Run as Administrator"

### Folder Already Exists
If a folder already exists, you'll see an error. This is usually safe to ignore, but you can:

**Linux/macOS:**
```bash
# Use -p flag to suppress errors
mkdir -p existing_folder
```

**Windows (PowerShell):**
```powershell
# Use -Force flag
New-Item -ItemType Directory -Force -Path "existing_folder"
```

### Path Too Long (Windows)
On Windows, if you encounter "path too long" errors:
1. Enable long path support in Windows 10/11
2. Use shorter folder names
3. Create project closer to root (e.g., C:\projects\frog-id)

## Next Steps

After creating the folder structure:

1. **Add placeholder files**: Create README.md or .gitkeep in empty folders
2. **Initialize Git**: Add and commit the folder structure
3. **Review .gitignore**: Ensure temporary files won't be tracked
4. **Set up virtual environment**: Create Python venv in project root
5. **Install dependencies**: Follow main README.md instructions

## Additional Resources

- [Git documentation](https://git-scm.com/doc)
- [Python virtual environments](https://docs.python.org/3/tutorial/venv.html)
- [Project README](README.md) - Main project documentation
