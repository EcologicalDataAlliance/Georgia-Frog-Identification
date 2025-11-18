from fastapi import FastAPI, HTTPException, File, UploadFile, Response
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import joblib
import json
import os
import io
import librosa
import soundfile as sf
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = FastAPI(title="Frog Sound Classifier API")

# CORS for web UI integration
cors_origins = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client (optional)
supabase: Optional[Client] = None
SAVE_UPLOADS = os.getenv("SAVE_AUDIO_UPLOADS", "false").lower() == "true"


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Frog Sound Classifier API",
        "version": "1.1.0",
        "endpoints": {
            "/predict": "POST - Predict frog species from 26 audio features",
            "/predict-audio": "POST - Predict frog species from uploaded audio file",
            "/feedback": "POST - Submit feedback about incorrect predictions",
            "/audio/{filename}": "GET - Stream an uploaded audio file with correct Content-Type",
            "/signed-url/{filename}": "GET - Get a short-lived signed URL for a stored audio file",
            "/health": "GET - Health check endpoint",
            "/docs": "GET - Interactive API documentation"
        },
        "model_info": {
            "type": "Random Forest Classifier (Calibrated)",
            "features_required": 26,
            "audio_requirements": {
                "recommended_duration": "15-30 seconds",
                "processed_duration": "10 seconds (best window auto-selected)",
                "supported_formats": ["WAV", "MP3", "FLAC", "OGG", "M4A"]
            }
        },
        "data_collection": {
            "audio_saving_enabled": SAVE_UPLOADS,
            "note": "Audio uploads may be saved for model improvement" if SAVE_UPLOADS else "Audio uploads are not saved"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "healthy", "message": "Frog classifier API is running"}


# Audio processing constants
TARGET_SR = 22050
TARGET_DURATION = 10.0
PEAK_LEVEL = 0.98
PRE_EMPHASIS_COEF = 0.97


# Audio preprocessing functions (matching training notebook)
def to_mono(y: np.ndarray) -> np.ndarray:
    """Convert multi-channel audio to mono."""
    if y.ndim == 1:
        return y
    if y.shape[0] <= 8 and y.shape[1] > 8:  # channels-first
        return np.mean(y, axis=0)
    return np.mean(y, axis=-1)  # channels-last


def trim_silence(y: np.ndarray, top_db: float = 30.0) -> np.ndarray:
    """Remove leading and trailing silence."""
    yt, _ = librosa.effects.trim(y, top_db=top_db)
    return yt if yt.size > 0 else y


def find_best_10s_window(y: np.ndarray, sr: int, target_duration: float = TARGET_DURATION) -> np.ndarray:
    """
    Find the 10-second window with highest RMS energy (most activity).
    This ensures we capture the frog call even if it's not at the beginning.
    """
    window_samples = int(target_duration * sr)
    
    if len(y) <= window_samples:
        return y
    
    # Calculate RMS in sliding windows (1-second hops)
    hop = sr
    best_rms = -1
    best_start = 0
    
    for start in range(0, len(y) - window_samples + 1, hop):
        window = y[start:start + window_samples]
        rms = np.sqrt(np.mean(window**2))
        if rms > best_rms:
            best_rms = rms
            best_start = start
    
    return y[best_start:best_start + window_samples]


def standardize_duration(y: np.ndarray, sr: int, target_seconds: float) -> np.ndarray:
    """Pad or trim audio to exact target duration."""
    target_len = int(target_seconds * sr)
    if y.shape[0] > target_len:
        return y[:target_len]
    if y.shape[0] < target_len:
        pad = target_len - y.shape[0]
        return np.pad(y, (0, pad), mode="constant")
    return y


def peak_normalize(y: np.ndarray, peak: float = PEAK_LEVEL) -> np.ndarray:
    """Normalize audio to peak level."""
    max_val = np.max(np.abs(y)) if y.size else 0.0
    if max_val > 0:
        return (y / max_val) * peak
    return y


def normalize_audio(y: np.ndarray, sr: int, apply_preemphasis: bool = True) -> tuple:
    """
    Normalize audio to match training data preprocessing.
    Matches the exact process from data_preparation notebook.
    """
    # Convert to mono
    y = to_mono(y)
    
    # Trim silence
    y = trim_silence(y, top_db=30.0)
    
    # Find best 10-second window (smart selection)
    y = find_best_10s_window(y, sr, TARGET_DURATION)
    
    # Resample if needed
    if sr != TARGET_SR:
        y = librosa.resample(y=y, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR
    
    # Standardize duration (pad if needed after window selection)
    y = standardize_duration(y, sr, TARGET_DURATION)
    
    # Optional pre-emphasis
    if apply_preemphasis:
        y = librosa.effects.preemphasis(y, coef=PRE_EMPHASIS_COEF)
    
    # Peak normalize
    y = peak_normalize(y, PEAK_LEVEL)
    
    return y, sr


def extract_audio_features(y: np.ndarray, sr: int) -> dict:
    """
    Extract 26 audio features matching the training process.
    Matches extract_audio_features from data_preparation notebook.
    """
    features = {}
    
    # Spectral features (means only)
    features['centroid_mean'] = librosa.feature.spectral_centroid(y=y, sr=sr)[0].mean()
    features['bandwidth_mean'] = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0].mean()
    features['rolloff_mean'] = librosa.feature.spectral_rolloff(y=y, sr=sr)[0].mean()
    
    # MFCCs (13 coefficients, mean and std)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for i in range(13):
        features[f'mfcc{i+1}_mean'] = mfccs[i].mean()
    
    # MFCC std (only specific coefficients: 1, 3, 4, 5, 7, 8, 12)
    for i in [0, 2, 3, 4, 6, 7, 11]:  # 0-indexed
        features[f'mfcc{i+1}_std'] = mfccs[i].std()
    
    # Other features
    features['zcr_mean'] = librosa.feature.zero_crossing_rate(y)[0].mean()
    features['rms_mean'] = librosa.feature.rms(y=y)[0].mean()
    features['rms_std'] = librosa.feature.rms(y=y)[0].std()
    
    return features


def _guess_content_type_from_ext(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    content_type_map = {
        "mp3": "audio/mpeg",
        "mpeg": "audio/mpeg",
        "wav": "audio/wav",
        "flac": "audio/flac",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4",
        "aac": "audio/aac",
        "wma": "audio/x-ms-wma",
    }
    return content_type_map.get(ext, f"audio/{ext}" if ext else "application/octet-stream")


def features_dict_to_array(features: dict, feature_names: list) -> np.ndarray:
    """Convert features dictionary to ordered array matching training."""
    return np.array([features[name] for name in feature_names])


async def save_prediction_to_supabase(
    audio_bytes: bytes,
    filename: str,
    prediction: str,
    top_3: list,
    probabilities: list,
    storage_filename: Optional[str] = None,
) -> None:
    """Save audio file and prediction metadata to Supabase."""
    global supabase
    if not supabase:
        return
    
    bucket_name = os.getenv("SUPABASE_BUCKET", "frog-user-recordings")
    timestamp = datetime.utcnow().isoformat()
    
    # Create unique filename with timestamp and prediction
    file_ext = os.path.splitext(filename)[1]
    safe_ext = (file_ext[1:] or "mpeg").lower()
    # Map common extensions to proper content types
    content_type = _guess_content_type_from_ext(filename)

    if not storage_filename:
        storage_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{prediction}_{top_3[0]['confidence']:.2f}{file_ext}"

    # Upload audio file to Supabase Storage (with upsert and explicit content type)
    try:
        upload_resp = supabase.storage.from_(bucket_name).upload(
            path=storage_filename,
            file=audio_bytes,
            file_options={
                "content_type": content_type,
            },
        )
        # Some SDK versions return dict, others object; log for visibility
        print(f"✅ Supabase storage upload response: {upload_resp}")
    except Exception as e:
        # Surface storage errors up to caller for logging
        raise RuntimeError(f"Storage upload failed: {e}")
    
    # Store metadata in database (you'll need to create this table in Supabase)
    metadata = {
        "filename": storage_filename,
        "original_filename": filename,
        "prediction": prediction,
        "top_3_predictions": top_3,
        "all_probabilities": probabilities,
        "timestamp": timestamp
    }
    
    # Insert into predictions table (create this table in your Supabase dashboard)
    try:
        db_resp = supabase.table("predictions").insert(metadata).execute()
        print(f"✅ Supabase DB insert response: {db_resp}")
    except Exception as e:
        print(
            f"⚠️  DB insert failed: {e}. Ensure 'predictions' table exists and JSONB columns accept the payload. Metadata: {metadata}"
        )


def _log_bg_result(task: asyncio.Task):
    try:
        task.result()
        print("✅ Background Supabase save completed")
    except Exception as e:
        print(f"⚠️  Background Supabase save failed: {e}")


@app.get("/audio/{filename}")
async def stream_audio(filename: str):
    """Stream an uploaded audio file with a correct Content-Type header.

    This proxies the object from Supabase Storage and ensures clients
    receive an appropriate media type regardless of stored metadata.
    """
    global supabase
    if not supabase:
        raise HTTPException(status_code=503, detail="Storage not configured")

    bucket_name = os.getenv("SUPABASE_BUCKET", "frog-user-recordings")
    try:
        data = supabase.storage.from_(bucket_name).download(filename)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    content_type = _guess_content_type_from_ext(filename)
    return Response(content=data, media_type=content_type)


@app.get("/signed-url/{filename}")
def get_signed_url(filename: str, expires_in: int = 900):
    """Return a short-lived signed URL for an existing stored file.

    Use this from the web UI to obtain a direct Storage URL once the
    background upload has finished. Default expiry is 900 seconds.
    """
    global supabase
    if not supabase:
        raise HTTPException(status_code=503, detail="Storage not configured")

    bucket_name = os.getenv("SUPABASE_BUCKET", "frog-user-recordings")
    try:
        signed = supabase.storage.from_(bucket_name).create_signed_url(filename, expires_in)
        if isinstance(signed, dict):
            url = signed.get("signedURL") or signed.get("signed_url") or signed.get("url")
        else:
            url = getattr(signed, "signed_url", None) or getattr(signed, "signedURL", None) or getattr(signed, "url", None)
        if not url:
            raise RuntimeError("No signed URL returned")
        return {"filename": filename, "signed_url": url, "expires_in": expires_in}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not create signed URL: {e}")



# Load model, scaler, and feature names at startup
@app.on_event("startup")
def load_artifacts() -> None:
    """Load the trained model, scaler, feature names, and initialize Supabase."""
    global model, scaler, feature_names, supabase
    model_path = os.environ.get("MODEL_PATH", "rf_calibrated_model.joblib")
    scaler_path = os.environ.get("SCALER_PATH", "scaler.joblib")
    features_path = os.environ.get("FEATURES_PATH", "feature_columns.json")

    try:
        model = joblib.load(model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from {model_path}: {e}")
    try:
        scaler = joblib.load(scaler_path)
    except Exception as e:
        # If no scaler is provided, set to None
        scaler = None
    if os.path.exists(features_path):
        with open(features_path, "r") as f:
            feature_names = json.load(f)
    else:
        feature_names = None
    
    # Initialize Supabase if credentials are provided
    if SAVE_UPLOADS:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            try:
                supabase = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized - audio uploads will be saved")
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize Supabase: {e}")
                print("   Audio uploads will not be saved")
        else:
            print("⚠️  Warning: SUPABASE_URL or SUPABASE_KEY not set")
            print("   Audio uploads will not be saved")


class PredictionRequest(BaseModel):
    """
    Request body for prediction.
    `features` should be a list of 26 numerical values in the exact order listed below.
    
    Feature order (from feature_columns.json):
    1. centroid_mean, 2. bandwidth_mean, 3. rolloff_mean,
    4-16. mfcc1_mean through mfcc13_mean (13 features),
    17-23. mfcc1_std, mfcc3_std, mfcc4_std, mfcc5_std, mfcc7_std, mfcc8_std, mfcc12_std (7 features),
    24. zcr_mean, 25. rms_mean, 26. rms_std
    """
    features: List[float] = [
        1500.0,    # 1. centroid_mean
        2000.0,    # 2. bandwidth_mean
        3000.0,    # 3. rolloff_mean
        -200.0,    # 4. mfcc1_mean
        150.0,     # 5. mfcc2_mean
        100.0,     # 6. mfcc3_mean
        50.0,      # 7. mfcc4_mean
        30.0,      # 8. mfcc5_mean
        20.0,      # 9. mfcc6_mean
        10.0,      # 10. mfcc7_mean
        5.0,       # 11. mfcc8_mean
        3.0,       # 12. mfcc9_mean
        2.0,       # 13. mfcc10_mean
        1.0,       # 14. mfcc11_mean
        0.5,       # 15. mfcc12_mean
        0.2,       # 16. mfcc13_mean
        50.0,      # 17. mfcc1_std
        30.0,      # 18. mfcc3_std
        20.0,      # 19. mfcc4_std
        15.0,      # 20. mfcc5_std
        10.0,      # 21. mfcc7_std
        8.0,       # 22. mfcc8_std
        5.0,       # 23. mfcc12_std
        0.15,      # 24. zcr_mean
        0.05,      # 25. rms_mean
        0.02       # 26. rms_std
    ]


class PredictionResponse(BaseModel):
    """
    Response body containing the predicted class label and optional probabilities.
    """
    prediction: str | int
    top_3: List[dict] | None = None
    probabilities: List[float] | None = None
    filename: Optional[str] = None
    signed_url: Optional[str] = None
    signed_url_expires_in: Optional[int] = None


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Predict the frog species given a list of feature values.
    The number of features provided must match the model's expected input dimension.
    """
    global model, scaler, feature_names
    # Convert features to numpy array and reshape
    X = np.array(request.features)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    # Validate input dimension
    expected_dim = model.n_features_in_ if hasattr(model, "n_features_in_") else None
    if expected_dim and X.shape[1] != expected_dim:
        raise HTTPException(status_code=400, detail=f"Expected {expected_dim} features, got {X.shape[1]}")
    # Apply scaler if available
    if scaler is not None:
        X = scaler.transform(X)
    # Generate prediction and probabilities
    try:
        pred = model.predict(X)
        # Some classifiers support predict_proba; wrap in try/except
        try:
            proba = model.predict_proba(X)[0]
            proba_list = proba.tolist()
            
            # Calculate top 3 predictions
            if hasattr(model, 'classes_'):
                # Get indices of top 3 probabilities
                top_3_indices = np.argsort(proba)[::-1][:3]
                top_3 = [
                    {
                        "species": str(model.classes_[idx]),
                        "confidence": float(proba[idx])
                    }
                    for idx in top_3_indices
                ]
            else:
                top_3 = None
        except Exception:
            proba_list = None
            top_3 = None
            
        # Handle both string and integer predictions
        prediction_value = pred[0] if isinstance(pred[0], (str, int)) else str(pred[0])
        return PredictionResponse(
            prediction=prediction_value,
            top_3=top_3,
            probabilities=proba_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@app.post("/predict-audio", response_model=PredictionResponse)
async def predict_from_audio(file: UploadFile = File(...)):
    """
    Predict frog species from an uploaded audio file.
    
    Accepts: WAV, MP3, FLAC, OGG, M4A audio files
    Processing:
    - Converts to mono
    - Trims silence
    - Finds best 10-second window (highest activity)
    - Extracts 26 audio features
    - Returns prediction with top 3 species
    - Optionally saves audio and metadata to Supabase (if configured)
    
    Recording tips:
    - Record for 15-30 seconds to ensure frog call is captured
    - Minimize background noise (wind, traffic, talking)
    - Get as close as safely possible to the frog
    - The system automatically finds the best 10-second segment
    """
    global model, scaler, feature_names, supabase
    
    # Validate file type
    allowed_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.wma'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read audio file from upload
        audio_bytes = await file.read()
        
        # Load audio with librosa
        try:
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load audio file: {e}")
        
        # Normalize audio (matching training preprocessing)
        try:
            y_normalized, sr_normalized = normalize_audio(y, sr, apply_preemphasis=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio normalization failed: {e}")
        
        # Extract features
        try:
            features_dict = extract_audio_features(y_normalized, sr_normalized)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Feature extraction failed: {e}")
        
        # Convert to array in correct order
        if feature_names is None:
            raise HTTPException(status_code=500, detail="Feature names not loaded")
        
        try:
            feature_array = features_dict_to_array(features_dict, feature_names)
            X = feature_array.reshape(1, -1)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Feature ordering failed: {e}")
        
        # Validate feature count
        expected_dim = model.n_features_in_ if hasattr(model, "n_features_in_") else None
        if expected_dim and X.shape[1] != expected_dim:
            raise HTTPException(
                status_code=500,
                detail=f"Feature extraction produced {X.shape[1]} features, expected {expected_dim}"
            )
        
        # Apply scaler
        if scaler is not None:
            X = scaler.transform(X)
        
        # Generate prediction
        try:
            pred = model.predict(X)
            proba = model.predict_proba(X)[0]
            proba_list = proba.tolist()
            
            # Calculate top 3 predictions
            if hasattr(model, 'classes_'):
                top_3_indices = np.argsort(proba)[::-1][:3]
                top_3 = [
                    {
                        "species": str(model.classes_[idx]),
                        "confidence": float(proba[idx])
                    }
                    for idx in top_3_indices
                ]
            else:
                top_3 = None
            
            prediction_value = pred[0] if isinstance(pred[0], (str, int)) else str(pred[0])
            storage_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{prediction_value}_{top_3[0]['confidence']:.2f}{file_ext}"
            
            # Save audio and metadata to Supabase if enabled (background)
            signed_url = None
            signed_expires = 900

            if SAVE_UPLOADS and supabase:
                try:
                    task = asyncio.create_task(
                        save_prediction_to_supabase(
                            audio_bytes=audio_bytes,
                            filename=file.filename,
                            prediction=prediction_value,
                            top_3=top_3,
                            probabilities=proba_list,
                            storage_filename=storage_filename,
                        )
                    )
                    task.add_done_callback(_log_bg_result)
                    # Best-effort signed URL (may fail if upload not completed yet)
                    try:
                        signed = supabase.storage.from_(os.getenv("SUPABASE_BUCKET", "frog-user-recordings")).create_signed_url(storage_filename, signed_expires)
                        # The SDK may return dict or object; extract URL accordingly
                        if isinstance(signed, dict):
                            signed_url = signed.get("signedURL") or signed.get("signed_url") or signed.get("url")
                        else:
                            signed_url = getattr(signed, "signed_url", None) or getattr(signed, "signedURL", None) or getattr(signed, "url", None)
                    except Exception:
                        signed_url = None
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"⚠️  Warning: Failed to schedule save to Supabase: {e}")
            
            return PredictionResponse(
                prediction=prediction_value,
                top_3=top_3,
                probabilities=proba_list,
                filename=storage_filename if SAVE_UPLOADS and supabase else None,
                signed_url=signed_url,
                signed_url_expires_in=signed_expires if signed_url else None,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


class FeedbackRequest(BaseModel):
    """Feedback request for incorrect predictions."""
    filename: str
    predicted_species: str
    actual_species: str
    confidence: float
    notes: Optional[str] = None


@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback about an incorrect prediction.
    
    This helps improve the model by collecting user corrections.
    """
    global supabase
    
    if not supabase:
        raise HTTPException(
            status_code=503,
            detail="Feedback system not configured. Please set SUPABASE_URL and SUPABASE_KEY."
        )
    
    try:
        feedback_data = {
            "filename": feedback.filename,
            "predicted_species": feedback.predicted_species,
            "actual_species": feedback.actual_species,
            "confidence": feedback.confidence,
            "notes": feedback.notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Insert into feedback table (create this in your Supabase dashboard)
        supabase.table("feedback").insert(feedback_data).execute()
        
        return {
            "status": "success",
            "message": "Thank you for your feedback! This will help improve the model."
        }
    except Exception as e:
        print(f"⚠️  Note: feedback table may not exist. Create it in Supabase dashboard")
        print(f"   Table schema: feedback(id, filename, predicted_species, actual_species, confidence, notes, timestamp)")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {e}")
