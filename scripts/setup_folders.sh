#!/bin/bash
# Setup script for creating the Georgia Frog Identification project folder structure
# This script creates all necessary directories as defined in the README

set -e  # Exit on error

echo "=========================================="
echo "Georgia Frog Identification - Folder Setup"
echo "=========================================="
echo ""

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo "Creating folder structure in: $PROJECT_ROOT"
echo ""

# Backend structure
echo "Creating backend directories..."
mkdir -p backend/data_mining/scrapers
mkdir -p backend/data_mining/validators
mkdir -p backend/data_mining/pipelines
mkdir -p backend/database/models
mkdir -p backend/database/migrations
mkdir -p backend/database/queries
mkdir -p backend/audio_processing/preprocessing
mkdir -p backend/audio_processing/features
mkdir -p backend/audio_processing/segmentation
mkdir -p backend/audio_processing/augmentation
mkdir -p backend/ml_models/architectures
mkdir -p backend/ml_models/training
mkdir -p backend/ml_models/evaluation
mkdir -p backend/ml_models/inference
mkdir -p backend/api/routes
mkdir -p backend/api/middleware
mkdir -p backend/api/serializers
mkdir -p backend/utils

# Data structure
echo "Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/models
mkdir -p data/exports

# Notebooks structure
echo "Creating notebooks directories..."
mkdir -p notebooks/exploratory
mkdir -p notebooks/modeling
mkdir -p notebooks/evaluation

# Additional directories
echo "Creating additional directories..."
mkdir -p docker
mkdir -p tests
mkdir -p docs

echo ""
echo "Creating .gitkeep files in empty directories..."

# Find all empty directories and add .gitkeep
find . -type d -empty -not -path "./.git/*" -exec touch {}/.gitkeep \;

echo ""
echo "=========================================="
echo "Folder structure created successfully!"
echo "=========================================="
echo ""
echo "Directory tree:"
echo ""

# Display the created structure (if tree is available)
if command -v tree &> /dev/null; then
    tree -L 3 -d --gitignore
else
    # Fallback to find if tree is not available
    find . -type d -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./frontend/*" | sort
fi

echo ""
echo "Next steps:"
echo "1. Review FOLDER_SETUP.md for detailed documentation"
echo "2. Add README.md files to document each module"
echo "3. Set up Python virtual environment"
echo "4. Install project dependencies"
echo ""
