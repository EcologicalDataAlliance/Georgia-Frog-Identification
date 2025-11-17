# PowerShell setup script for creating the Georgia Frog Identification project folder structure
# This script creates all necessary directories as defined in the README

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Georgia Frog Identification - Folder Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "Creating folder structure in: $ProjectRoot" -ForegroundColor Yellow
Write-Host ""

# Define the complete folder structure
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
    "docs"
)

Write-Host "Creating directories..." -ForegroundColor Green

# Create all folders
foreach ($folder in $folders) {
    $path = Join-Path $ProjectRoot $folder
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
        Write-Host "  Created: $folder" -ForegroundColor Gray
    } else {
        Write-Host "  Exists:  $folder" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Creating .gitkeep files in empty directories..." -ForegroundColor Green

# Add .gitkeep to all empty directories
Get-ChildItem -Directory -Recurse -Exclude ".git","node_modules","frontend" | 
    Where-Object { 
        $files = Get-ChildItem $_.FullName -Force -ErrorAction SilentlyContinue
        ($files | Where-Object { $_.Name -ne '.gitkeep' }).Count -eq 0
    } |
    ForEach-Object { 
        $gitkeepPath = Join-Path $_.FullName ".gitkeep"
        if (-not (Test-Path $gitkeepPath)) {
            New-Item -ItemType File -Path $gitkeepPath -Force | Out-Null
            Write-Host "  Added .gitkeep to: $($_.FullName.Replace($ProjectRoot, '.'))" -ForegroundColor Gray
        }
    }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Folder structure created successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Display the created structure
Write-Host "Directory tree:" -ForegroundColor Yellow
Write-Host ""

# Get all directories and display them
Get-ChildItem -Directory -Recurse -Depth 2 -Exclude ".git","node_modules" | 
    Where-Object { $_.FullName -notlike "*\frontend\*" } |
    Select-Object @{Name='Path';Expression={$_.FullName.Replace($ProjectRoot, '.').Replace('\', '/')}} |
    Sort-Object Path |
    ForEach-Object { Write-Host "  $($_.Path)" -ForegroundColor Gray }

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review FOLDER_SETUP.md for detailed documentation"
Write-Host "2. Add README.md files to document each module"
Write-Host "3. Set up Python virtual environment"
Write-Host "4. Install project dependencies"
Write-Host ""

# Pause to let user read the output
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
