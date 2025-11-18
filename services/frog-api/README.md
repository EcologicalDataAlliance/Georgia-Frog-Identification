# Frog Random Forest API

This directory contains a production-ready implementation for serving your trained RandomForestClassifier model as a web API.

## Model Information

**Model Type:** Calibrated Random Forest Classifier  
**Species Classified:** 15 Georgia Frog Species

The model can identify the following species:
1. American Bullfrog (`american_bullfrog`)
2. American Toad (`american_toad`)
3. Bird-Voiced Tree Frog (`bird_voiced_tree_frog`)
4. Cope's Gray Treefrog (`copes_gray_treefrog`)
5. Eastern Narrow-Mouthed Toad (`eastern_narrow_mouthed_toad`)
6. Eastern Spadefoot Toad (`eastern_spadefoot_toad`)
7. Fowler's Toad (`fowlers_toad`)
8. Green Frog (`green_frog`)
9. Green Tree Frog (`green_tree_frog`)
10. Northern Cricket Frog (`northern_cricket_frog`)
11. Not Frogs (`not_frogs`) - background noise/other animals
12. Pickerel Frog (`pickerel_frog`)
13. Southern Leopard Frog (`southern_leopard_frog`)
14. Spring Peeper (`spring_peeper`)
15. Upland Chorus Frog (`upland_chorus_frog`)

**Example Prediction:**
```json
{
  "prediction": "american_bullfrog",
  "top_3": [
    {"species": "american_bullfrog", "confidence": 0.2199},
    {"species": "pickerel_frog", "confidence": 0.1187},
    {"species": "green_tree_frog", "confidence": 0.0895}
  ]
}
```
*Top prediction: American Bullfrog with 21.99% confidence*

## Contents

* `main.py` – FastAPI application with prediction endpoints
* `test_api.py` – test script for feature-based predictions
* `test_audio.py` – test script for audio file predictions
* `requirements.txt` – Python dependencies
* `Dockerfile` – Docker image configuration
* `rf_calibrated_model.joblib` – trained Random Forest model
* `scaler.joblib` – fitted StandardScaler
* `feature_columns.json` – 26 feature names in correct order
* `.env.example` – environment variable template
* `supabase_schema.sql` – SQL schema for Supabase tables
* `SUPABASE_SETUP.md` – detailed Supabase integration guide

## Features

✨ **Audio Upload Support** - Upload WAV, MP3, FLAC, OGG, M4A files  
✨ **Smart Preprocessing** - Automatic silence trimming and best 10-second window selection  
✨ **Top-3 Predictions** - Get ranked species predictions with confidence scores  
✨ **Data Collection** (Optional) - Save recordings to Supabase for model improvement  
✨ **Background Save** - Upload + DB insert run asynchronously for low latency  
✨ **Signed URLs** - Short‑lived links to stored audio for in‑app playback  
✨ **Feedback System** - Users can report incorrect predictions  
✨ **Docker Ready** - Containerized for easy deployment  
✨ **Interactive Docs** - Built-in Swagger UI at `/docs`

## Quick Start

### 1. Set Up Python Environment

**Create a virtual environment (recommended):**

```powershell
# On Windows
python -m venv .venv
.\.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**Install dependencies:**

```powershell
pip install -r requirements.txt
```

### 2. Run the API Server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload when you change the code (useful for development).

The API will be available at `http://localhost:8000`

### 3. Test the API

**Option 1: Interactive Documentation (Easiest)**

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

FastAPI automatically generates interactive documentation where you can test all endpoints.

**Option 2: Test Script**

Run the provided test script:

```powershell
python test_api.py
```

This will test all endpoints and show you example requests/responses.

**Option 3: Manual Request (Python)**

```python
import requests

# Test health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Test prediction with 26 features
features = [1500.0, 2000.0, 3000.0, -200.0, 150.0, 100.0, 50.0, 30.0, 
            20.0, 10.0, 5.0, 3.0, 2.0, 1.0, 0.5, 0.2, 50.0, 30.0, 
            20.0, 15.0, 10.0, 8.0, 5.0, 0.15, 0.05, 0.02]

response = requests.post(
    "http://localhost:8000/predict",
    json={"features": features}
)
print(response.json())
```

## API Endpoints

### `GET /`
Root endpoint with API information and available endpoints.

### `GET /health`
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Frog classifier API is running"
}
```

### `POST /predict-audio`
🎙️ **Predict frog species from an uploaded audio file** (Recommended for end users)

Upload an audio file and get predictions automatically. The system handles all feature extraction.

**Supported Formats:** WAV, MP3, FLAC, OGG, M4A

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file upload

**Recording Guidelines:**
- 🎤 **Record for 15-30 seconds** to ensure the frog call is captured
- 🔇 **Minimize background noise** (wind, traffic, talking)
- 📍 **Get as close as safely possible** to the frog (5-15 feet ideal)
- ⏱️ **The system automatically finds the best 10-second segment** with highest activity
- 🐸 **Make sure the frog calls clearly** during your recording

**Response:**
```json
{
  "prediction": "american_bullfrog",
  "top_3": [
    {"species": "american_bullfrog", "confidence": 0.65},
    {"species": "green_frog", "confidence": 0.20},
    {"species": "pickerel_frog", "confidence": 0.08}
  ],
  "probabilities": [0.65, 0.20, ...],
  "filename": "20251118_003026_american_toad_0.80.mp3",
  "signed_url": "https://...supabase.co/storage/v1/object/sign/frog-user-recordings/...",
  "signed_url_expires_in": 900
}
```

Notes:
- `signed_url` is best‑effort; if the background upload hasn’t finished yet it may be `null`. Poll `/signed-url/{filename}` to fetch one shortly after.

**Python Example:**
```python
import requests

with open("frog_recording.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/predict-audio",
        files={"file": f}
    )
print(response.json())
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/predict-audio" \
  -F "file=@frog_recording.wav"
```

### `GET /audio/{filename}`
Stream a previously uploaded audio file via the API with the correct `Content-Type` header (useful if Storage metadata shows `text/plain`).

### `GET /signed-url/{filename}?expires_in=900`
Return a short‑lived signed URL for a stored audio file in Supabase Storage. Default expiry is 900 seconds. Use this for direct playback/download from the browser.
```

### `POST /predict`
Predict frog species from audio features (for advanced users with pre-extracted features).

**Request Body:**
```json
{
  "features": [1500.0, 2000.0, 3000.0, ... ] // 26 numeric values
}
```

**Response:**
```json
{
  "prediction": "american_bullfrog",
  "top_3": [
    {"species": "american_bullfrog", "confidence": 0.22},
    {"species": "pickerel_frog", "confidence": 0.12},
    {"species": "green_tree_frog", "confidence": 0.09}
  ],
  "probabilities": [0.22, 0.09, 0.01, ...]
}
```

## Feature Requirements

The model expects **exactly 26 features** in this order:

1. `centroid_mean`
2. `bandwidth_mean`
3. `rolloff_mean`
4. `mfcc1_mean` through `mfcc13_mean` (13 features)
5. `mfcc1_std`, `mfcc3_std`, `mfcc4_std`, `mfcc5_std`, `mfcc7_std`, `mfcc8_std`, `mfcc12_std` (7 features)
6. `zcr_mean`
7. `rms_mean`
8. `rms_std`

See `feature_columns.json` for the exact list.

## Supabase Integration (Optional)

The API can optionally save uploaded audio files and prediction metadata to Supabase for model improvement and analysis.

### Setup Instructions

**1. Configure Environment Variables**

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```powershell
cp .env.example .env
```

Edit `.env`:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
SUPABASE_BUCKET=frog-user-recordings
SAVE_AUDIO_UPLOADS=true
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com
```

**2. Create Supabase Storage Bucket**

In your Supabase Dashboard:
1. Go to **Storage**
2. Click **New Bucket**
3. Name: `frog-user-recordings`
4. Set to **Private**

**3. Create Database Tables**

Run the SQL commands in `supabase_schema.sql` in your Supabase SQL Editor:

```sql
-- This creates two tables:
-- 1. predictions - stores audio files and prediction results
-- 2. feedback - stores user corrections for incorrect predictions
```

**4. Test the Integration**

Upload an audio file and check your Supabase dashboard:
- **Storage**: Should see the audio file in `frog-user-recordings` bucket
- **Database**: Check `predictions` table for metadata

### Behavior Details
- Upload + DB insert run in the background — responses return without waiting on storage.
- The API returns a deterministic `filename` that you can store in your app for future reference.
- Use `/signed-url/{filename}` if you need a URL after background save completes.

### Using the Feedback Endpoint

Allow users to report incorrect predictions:

```python
import requests

feedback = {
    "filename": "20251117_220403_american_toad_0.80.mp3",
    "predicted_species": "american_toad",
    "actual_species": "fowlers_toad",  # User correction
    "confidence": 0.80,
    "notes": "Recording was actually a Fowler's Toad, not American Toad"
}

response = requests.post(
    "http://localhost:8000/feedback",
    json=feedback
)
print(response.json())
```

### Analyzing Collected Data

Query your Supabase database to analyze model performance:

```sql
-- Get prediction distribution
SELECT prediction, COUNT(*) as count
FROM predictions
GROUP BY prediction
ORDER BY count DESC;

-- Get average confidence by species
SELECT prediction, 
       AVG((top_3_predictions->0->>'confidence')::float) as avg_confidence
FROM predictions
GROUP BY prediction;

-- Get user feedback
SELECT predicted_species, actual_species, COUNT(*) as corrections
FROM feedback
GROUP BY predicted_species, actual_species
ORDER BY corrections DESC;

-- Use the built-in stats function
SELECT * FROM get_model_stats();
```

**Note:** If `SAVE_AUDIO_UPLOADS=false` or Supabase credentials are not set, the API will still work normally but won't save uploads.

## Docker Deployment

### Build the Docker Image

```powershell
docker build -t frog-rf-api .
```

### Run the Container

```powershell
docker run -d -p 8000:80 ^
  -e SAVE_AUDIO_UPLOADS=true ^
  -e SUPABASE_URL="https://<project>.supabase.co" ^
  -e SUPABASE_KEY="<service_role_key>" ^
  -e SUPABASE_BUCKET="frog-user-recordings" ^
  -e CORS_ORIGINS="http://localhost:5173,https://yourdomain.com" ^
  --name frog-rf-api frog-rf-api
```

The API will be available at `http://localhost:8000`

### Test the Dockerized API

```powershell
# Health check
curl http://localhost:8000/health

# Or use the test script
python test_api.py
```

## Integration Guide for Teammates

### From a Web App (JavaScript/React)

**Upload Audio File (Recommended):**
```javascript
const predictFromAudio = async (audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  
  const response = await fetch('http://localhost:8000/predict-audio', {
    method: 'POST',
    body: formData,
  });
  
  const result = await response.json();
  return result;
};

// Usage with file input
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  const prediction = await predictFromAudio(file);
  
  console.log('Top prediction:', prediction.prediction);
  console.log('Top 3 species:', prediction.top_3);
  // Display top_3 in UI:
  // prediction.top_3.forEach(item => {
  //   console.log(`${item.species}: ${(item.confidence * 100).toFixed(1)}%`);
  // });
  // Play immediately if signed URL returned
  if (prediction.signed_url) {
    const audio = new Audio(prediction.signed_url);
    audio.play();
  } else if (prediction.filename) {
    // Fallback: request a signed URL after a short delay
    setTimeout(async () => {
      const r = await fetch(`http://localhost:8000/signed-url/${encodeURIComponent(prediction.filename)}?expires_in=900`);
      const j = await r.json();
      if (j.signed_url) new Audio(j.signed_url).play();
    }, 1500);
  }
};
```

**Or use pre-extracted features:**
```javascript
const predictSpecies = async (features) => {
  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ features }),
  });
  
  const result = await response.json();
  return result;
};

// Usage
const features = [1500.0, 2000.0, /* ... 26 features total */];
const prediction = await predictSpecies(features);
console.log('Predicted species:', prediction.prediction);
console.log('Top 3:', prediction.top_3);
```

### From Python

**Upload Audio File (Recommended):**
```python
import requests

def predict_from_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        response = requests.post(
            "http://localhost:8000/predict-audio",
            files={"file": f}
        )
    return response.json()

# Usage
result = predict_from_audio("frog_recording.wav")
print(f"Predicted species: {result['prediction']}")
print("\nTop 3 predictions:")
for i, pred in enumerate(result['top_3'], 1):
    print(f"  {i}. {pred['species']}: {pred['confidence']:.1%}")
```

**Or use pre-extracted features:**
```python
import requests

def predict_frog_species(features):
    response = requests.post(
        "http://localhost:8000/predict",
        json={"features": features}
    )
    return response.json()

# Usage
features = [1500.0, 2000.0, # ... 26 features total]
result = predict_frog_species(features)
print(f"Predicted species: {result['prediction']}")
print(f"Confidence: {result['top_3'][0]['confidence']:.1%}")
```

## Troubleshooting

**"Module not found" errors:**
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

**"Failed to load model" error:**
- Verify `rf_calibrated_model.joblib`, `scaler.joblib`, and `feature_columns.json` are in the project directory
- Check file permissions

**"Expected X features, got Y" error:**
- Ensure you're sending exactly 26 numeric values
- Check the order matches `feature_columns.json`

**Port already in use:**
- Change the port: `uvicorn main:app --port 8001`
- Or kill the process using port 8000

## Model Training

If you need to retrain or update the model, use the `Deploy_Final_Random_Forest.ipynb` notebook and save the artifacts:

```python
import joblib
import json

# Save model and scaler
joblib.dump(rf_cal, "rf_calibrated_model.joblib")
joblib.dump(scaler, "scaler.joblib")

# Save feature names
with open("feature_columns.json", "w") as f:
    json.dump(reduced_features, f)
```
