# Georgia Frog Vocalization Classifier

A comprehensive data science platform for automated classification of frog species native to Georgia using bioacoustic analysis and machine learning. This capstone project emphasizes robust data mining, database architecture, and classification model development over frontend aesthetics.

## Project Overview

This system combines bioacoustic data collection, audio processing, and machine learning to create an automated classifier for Georgia's native frog species. The project prioritizes data science rigor and model performance while utilizing a clean, functional dashboard interface for visualization and analysis.

### Target Species (Initial Phase)
Treefrogs 
- Green Treefrog (Hyla cinerea)
- Cope's Gray Treefrog (Hyla chrysoscelis)
- Squirrel Treefrog (Hyla squirella)
- Pine Woods Tree Frog (Hyla femoralis)
- Barking Treefrog (Hyla gratiosa)
- Bird-voiced Treefrog (Hyla avivoca)
Chorus Frogs 
- Spring Peeper (Pseudacris crucifer)
- Upland Chorus Frog (Pseudacris feriarum)
- Southern Chorus Frog (Pseudacris nigrita)
- Little Grass Frog (Pseudacris ocularis)
- Ornate Chorus Frog (Pseudacris ornata)
- Brimley's Chorus Frog (Pseudacris brimleyi)
True Frogs 
- American Bullfrog (Lithobates catesbeianus)
- Green Frog (Lithobates clamitans)
- Southern Leopard Frog (Lithobates sphenocephalus)
- Pickerel Frog (Lithobates palustris)
- River Frog (Lithobates heckscheri)
- Pig Frog (Lithobates grylio)

(if there are more add them)

## Core Data Science Features

### 🔍 **Data Mining & Collection**
- Automated scraping from bioacoustic databases (Xeno-canto, eBird, FrogID)
- Citizen science data integration and validation
- Custom field recording management system
- Quality assessment and filtering algorithms

### 🗄️ **Audio Database Architecture**
- PostgreSQL database with optimized audio metadata schema
- MinIO object storage for audio file management
- Data versioning and provenance tracking
- Automated backup and synchronization systems

### 🎵 **Audio Processing Pipeline**
- Noise reduction and audio enhancement
- Spectrogram generation and visualization
- MFCC feature extraction
- Call segmentation and pattern analysis
- Data augmentation for training set expansion

### 🤖 **Machine Learning Models**
- Convolutional Neural Networks for spectrogram classification
- Recurrent Neural Networks for temporal pattern recognition
- Ensemble methods combining multiple approaches
- Cross-validation and performance evaluation framework
- Model interpretability and confidence scoring

### 📊 **Analytics Dashboard**
- Real-time classification results visualization
- Model performance metrics and comparison
- Species distribution mapping
- Audio waveform and spectrogram displays
- Data quality assessment tools

## Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Mining Pipeline │───▶│   Raw Storage   │
│                 │    │                  │    │                 │
│ • Xeno-canto    │    │ • Web scrapers   │    │ • Audio files   │
│ • Citizen sci   │    │ • Data validation│    │ • Metadata      │
│ • Field recordings│  │ • Quality filter │    │ • Quality scores│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Processed     │◀───│  Audio Pipeline  │◀───│   PostgreSQL    │
│     Data        │    │                  │    │    Database     │
│                 │    │ • Preprocessing  │    │                 │
│ • Spectrograms  │    │ • Feature extract│    │ • Species data  │
│ • MFCC features │    │ • Augmentation   │    │ • Locations     │
│ • Call segments │    │ • Normalization  │    │ • Recordings    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ML Models     │◀───│  Training Pipeline│    │  React Dashboard│
│                 │    │                  │    │                 │
│ • CNN Classifier│    │ • Model training │    │ • Visualizations│
│ • RNN Temporal  │    │ • Validation     │    │ • Performance   │
│ • Ensemble      │    │ • Hyperparameter │    │ • Audio players │
│ • Confidence    │    │ • Cross-validation│   │ • Species maps  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Project Structure

```
EDA_frog_call_classifier_dashboard/
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
│   ├── ml_models/           # Machine learning components
│   │   ├── architectures/    # Model definitions (CNN, RNN)
│   │   ├── training/         # Training scripts and utilities
│   │   ├── evaluation/       # Model evaluation and metrics
│   │   └── inference/        # Prediction and serving
│   ├── api/                 # REST API endpoints
│   │   ├── routes/           # API route definitions
│   │   ├── middleware/       # Authentication, logging
│   │   └── serializers/      # Data serialization
│   └── utils/               # Shared utilities and helpers
├── frontend/                # React dashboard (adapted from eco_dataset_analytics)
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/       # Audio visualization components
│   │   │   │   ├── SpectrogramChart.jsx
│   │   │   │   ├── WaveformChart.jsx
│   │   │   │   ├── ConfidenceChart.jsx
│   │   │   │   └── SpeciesDistribution.jsx
│   │   │   ├── dashboard/    # Dashboard layout components
│   │   │   ├── audio/        # Audio player and controls
│   │   │   └── classification/ # Classification result displays
│   │   ├── data/            # Mock data and API integration
│   │   ├── hooks/           # Custom React hooks
│   │   └── pages/           # Main application pages
│   └── public/              # Static assets and audio samples
├── data/                    # Data storage and management
│   ├── raw/                 # Raw audio files and metadata
│   ├── processed/           # Processed features and spectrograms
│   ├── models/              # Trained model artifacts
│   └── exports/             # Data exports and reports
├── notebooks/               # Jupyter notebooks for analysis
│   ├── exploratory/         # Data exploration and EDA
│   ├── modeling/            # Model development and testing
│   └── evaluation/          # Performance analysis
├── docker/                  # Container configurations
├── tests/                   # Test suites
├── scripts/                 # Utility scripts and automation
└── docs/                    # Documentation and guides
```

## Getting Started

### Prerequisites

**Data Science Stack:**
- Python 3.9+ with conda/pip environment
- PostgreSQL 13+
- Redis (for caching and job queues)
- Docker & Docker Compose

**Frontend Development:**
- Node.js 16+
- npm or yarn

**Audio Processing Dependencies:**
```bash
# Core audio libraries
pip install librosa soundfile scipy numpy

# Machine learning frameworks
pip install tensorflow scikit-learn

# Database and web framework
pip install sqlalchemy psycopg2 fastapi uvicorn

# Data processing
pip install pandas matplotlib seaborn
```

### Installation

1. **Clone and setup environment:**
   ```bash
   git clone https://github.com/your-team/georgia-frog-classifier.git
   cd georgia-frog-classifier
   
   # Backend setup
   conda create -n frog-classifier python=3.9
   conda activate frog-classifier
   pip install -r backend/requirements.txt
   
   # Frontend setup
   cd frontend
   npm install
   ```

2. **Database initialization:**
   ```bash
   # Start PostgreSQL container
   docker-compose up -d postgres
   
   # Run migrations
   cd backend
   python -m alembic upgrade head
   ```

3. **Data pipeline setup:**
   ```bash
   # Initialize data mining
   python scripts/init_data_sources.py
   
   # Run initial data collection
   python -m backend.data_mining.pipelines.initial_collection
   ```

4. **Start development servers:**
   ```bash
   # Backend API
   cd backend
   uvicorn api.main:app --reload
   
   # Frontend dashboard
   cd frontend
   npm run dev
   ```

## Data Collection Strategy

### Phase 1: Existing Datasets
- Target 500+ recordings per species from established databases
- Focus on high-quality, labeled recordings from Georgia locations
- Implement data quality scoring system

### Phase 2: Citizen Science Integration
- Develop partnerships with local herpetological societies
- Create submission portal for citizen scientists
- Implement crowd-sourced validation system

### Phase 3: Field Recording Campaign
- Coordinate with Georgia DNR for sampling locations
- Standardized recording protocols and equipment
- Seasonal recording schedules aligned with breeding patterns

## Model Development Roadmap

### Milestone 1: Baseline Models (Weeks 1-4)
- Simple CNN on mel-spectrograms
- Traditional ML approaches (SVM, Random Forest) on MFCC features
- Establish evaluation metrics and benchmarks

### Milestone 2: Advanced Architectures (Weeks 5-8)
- ResNet-based CNN for improved spectrogram classification
- LSTM/GRU networks for temporal pattern recognition
- Attention mechanisms for call structure analysis

### Milestone 3: Ensemble and Production (Weeks 9-12)
- Model ensemble combining multiple approaches
- Real-time inference optimization
- Confidence calibration and uncertainty quantification

## Data Science Deliverables

1. **Comprehensive Dataset**: Curated collection of Georgia frog vocalizations with quality metadata
2. **Processing Pipeline**: Robust, scalable audio preprocessing and feature extraction system
3. **Classification Models**: Multiple trained models with thorough performance evaluation
4. **Evaluation Framework**: Rigorous testing methodology with cross-validation and statistical analysis
5. **Interactive Dashboard**: Functional visualization platform for exploring data and model results
6. **Technical Documentation**: Detailed methodology, model architecture, and performance analysis

## Team Collaboration

### Data Science Roles
- **Data Engineer**: Mining pipelines, database architecture, data quality
- **ML Engineer**: Model development, training infrastructure, evaluation
- **Audio Signal Processing**: Feature extraction, preprocessing, domain expertise
- **Full-Stack Developer**: Dashboard integration, API development, deployment

### Development Workflow
- Feature branches with peer review
- Automated testing for data pipelines and models
- Regular model performance monitoring
- Documentation-driven development

## Performance Goals

### Data Quality Targets
- 90%+ data quality scores for training set
- Balanced representation across species (minimum 300 recordings each)
- Geographic diversity across Georgia ecoregions

### Model Performance Targets
- Top-1 accuracy: >85% on test set
- Top-3 accuracy: >95% on test set
- False positive rate: <10% per species
- Real-time inference capability (<2 seconds per classification)

## Critical Challenges & Mitigation

### Data Challenges
- **Limited labeled data**: Active learning, data augmentation, transfer learning
- **Class imbalance**: Weighted sampling, synthetic data generation
- **Recording quality variation**: Robust preprocessing, quality-aware training

### Technical Challenges
- **Audio processing complexity**: Leverage established libraries, domain expertise
- **Model interpretability**: Attention visualization, feature importance analysis
- **Scalability**: Containerized deployment, efficient data pipelines

## License & Contributing

This project is developed as an academic capstone with potential for open-source release. See CONTRIBUTING.md for development guidelines and code standards.

## Acknowledgments

- Georgia Department of Natural Resources for species data
- Xeno-canto and eBird communities for bioacoustic databases
- [University Name] Data Science Program faculty advisors

---

**Note**: This is a data science capstone project emphasizing rigorous methodology, reproducible research, and practical applications in bioacoustic conservation.
