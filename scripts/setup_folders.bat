@echo off
REM Setup script for creating the Georgia Frog Identification project folder structure
REM This script creates all necessary directories as defined in the README

echo ==========================================
echo Georgia Frog Identification - Folder Setup
echo ==========================================
echo.

echo Creating folder structure...
echo.

REM Backend structure
echo Creating backend directories...
mkdir backend\data_mining\scrapers 2>nul
mkdir backend\data_mining\validators 2>nul
mkdir backend\data_mining\pipelines 2>nul
mkdir backend\database\models 2>nul
mkdir backend\database\migrations 2>nul
mkdir backend\database\queries 2>nul
mkdir backend\audio_processing\preprocessing 2>nul
mkdir backend\audio_processing\features 2>nul
mkdir backend\audio_processing\segmentation 2>nul
mkdir backend\audio_processing\augmentation 2>nul
mkdir backend\ml_models\architectures 2>nul
mkdir backend\ml_models\training 2>nul
mkdir backend\ml_models\evaluation 2>nul
mkdir backend\ml_models\inference 2>nul
mkdir backend\api\routes 2>nul
mkdir backend\api\middleware 2>nul
mkdir backend\api\serializers 2>nul
mkdir backend\utils 2>nul

REM Data structure
echo Creating data directories...
mkdir data\raw 2>nul
mkdir data\processed 2>nul
mkdir data\models 2>nul
mkdir data\exports 2>nul

REM Notebooks structure
echo Creating notebooks directories...
mkdir notebooks\exploratory 2>nul
mkdir notebooks\modeling 2>nul
mkdir notebooks\evaluation 2>nul

REM Additional directories
echo Creating additional directories...
mkdir docker 2>nul
mkdir tests 2>nul
mkdir docs 2>nul

echo.
echo Creating .gitkeep files in empty directories...

REM Create .gitkeep files in all newly created directories
echo. > backend\data_mining\scrapers\.gitkeep
echo. > backend\data_mining\validators\.gitkeep
echo. > backend\data_mining\pipelines\.gitkeep
echo. > backend\database\models\.gitkeep
echo. > backend\database\migrations\.gitkeep
echo. > backend\database\queries\.gitkeep
echo. > backend\audio_processing\preprocessing\.gitkeep
echo. > backend\audio_processing\features\.gitkeep
echo. > backend\audio_processing\segmentation\.gitkeep
echo. > backend\audio_processing\augmentation\.gitkeep
echo. > backend\ml_models\architectures\.gitkeep
echo. > backend\ml_models\training\.gitkeep
echo. > backend\ml_models\evaluation\.gitkeep
echo. > backend\ml_models\inference\.gitkeep
echo. > backend\api\routes\.gitkeep
echo. > backend\api\middleware\.gitkeep
echo. > backend\api\serializers\.gitkeep
echo. > backend\utils\.gitkeep
echo. > data\raw\.gitkeep
echo. > data\processed\.gitkeep
echo. > data\models\.gitkeep
echo. > data\exports\.gitkeep
echo. > notebooks\exploratory\.gitkeep
echo. > notebooks\modeling\.gitkeep
echo. > notebooks\evaluation\.gitkeep
echo. > docker\.gitkeep
echo. > tests\.gitkeep
echo. > docs\.gitkeep

echo.
echo ==========================================
echo Folder structure created successfully!
echo ==========================================
echo.
echo Directory tree:
echo.

tree /F /A

echo.
echo Next steps:
echo 1. Review FOLDER_SETUP.md for detailed documentation
echo 2. Add README.md files to document each module
echo 3. Set up Python virtual environment
echo 4. Install project dependencies
echo.

pause
