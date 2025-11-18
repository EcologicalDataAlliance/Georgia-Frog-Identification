# Frog Classifier Integration Guide

This guide explains how to run the complete integrated system with the frontend, Express media server, and FastAPI classification service.

## Architecture Overview

```
┌─────────────────┐
│  React Frontend │  (Port 5173)
│   (Vite Dev)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Express Server  │  (Port 8000)
│  Media + Proxy  │
└────┬───────┬────┘
     │       │
     │       └──────────────┐
     ▼                      ▼
┌─────────────┐    ┌────────────────┐
│  Supabase   │    │  FastAPI       │  (Port 8001)
│  Storage    │    │  Classifier    │
│  (Images)   │    │  (ML Model)    │
└─────────────┘    └────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

#### Frontend and Express Server
```bash
cd frontend
npm install

cd server
npm install
```

#### FastAPI Service
```bash
cd services/frog-api
python -m venv .venv

# On Windows
.\.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

#### Express Server (`frontend/server/.env`)
```bash
cd frontend/server
cp .env.example .env
```

Edit `.env` with your values:
```env
PORT=8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
FROG_API_URL=http://localhost:8001
```

#### FastAPI Service (`services/frog-api/.env`) - Optional
```bash
cd services/frog-api
cp .env.example .env
```

Edit `.env` if you want to save predictions to Supabase:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=frog-user-recordings
SAVE_AUDIO_UPLOADS=true
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
```

#### Frontend (`frontend/.env`)
```bash
cd frontend
```

Create `.env`:
```env
VITE_API_BASE=http://localhost:8000
```

### 3. Start All Services

#### Terminal 1: FastAPI Classification Service
```bash
cd services/frog-api
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

#### Terminal 2: Express Media Server
```bash
cd frontend/server
npm start
```

You should see:
```
🚀 Server running on http://localhost:8000
📡 FastAPI proxy target: http://localhost:8001
```

#### Terminal 3: React Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

### 4. Verify Setup

1. Open http://localhost:5173 in your browser
2. Navigate to "Classifier Interface"
3. Upload an audio file (WAV, MP3, FLAC, OGG, M4A)
4. Click "Classify Recording"
5. View top-3 predictions with images and confidence scores

## API Endpoints

### Express Server (http://localhost:8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/classify` | POST | Classify audio (proxies to FastAPI) |
| `/api/species/:slug/media` | GET | Get media URLs for single species |
| `/api/species/media/batch` | POST | Get media URLs for multiple species |

### FastAPI Service (http://localhost:8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/predict-audio` | POST | Classify audio file |
| `/predict` | POST | Classify from features |
| `/docs` | GET | Interactive API docs (Swagger) |

## How It Works

1. **User uploads audio** in React frontend (`Classifier.jsx`)
2. **Frontend sends file** to Express server at `/classify`
3. **Express server**:
   - Receives file via multer
   - Forwards to FastAPI `/predict-audio` on port 8001
   - Gets prediction with top-3 species
   - Enriches response with image URLs from Supabase
   - Returns enhanced response to frontend
4. **Frontend displays** top-3 predictions with:
   - Species images from Supabase
   - Formatted species names
   - Confidence percentages
   - Visual confidence bars

## Troubleshooting

### "Failed to classify audio"
- Verify FastAPI is running on port 8001
- Check Express server logs for connection errors
- Ensure `FROG_API_URL=http://localhost:8001` in Express `.env`

### Images not loading
- Verify Supabase credentials in Express server `.env`
- Check Supabase bucket "Species Catalog" exists
- Ensure images are at `images/{slug}/{slug}.jpg`
- Check browser console for 404 errors

### Port already in use
- FastAPI: Change port with `--port 8002` and update `FROG_API_URL`
- Express: Change `PORT=8001` in `.env`
- Frontend: Vite auto-assigns new port if 5173 is taken

### CORS errors
- Ensure Express server is configured with proper CORS
- Check FastAPI CORS settings in `main.py`
- Verify `VITE_API_BASE` matches Express server URL

## Testing Individual Services

### Test FastAPI directly
```bash
curl -X POST http://localhost:8001/predict-audio \
  -F "file=@path/to/audio.wav"
```

### Test Express proxy
```bash
curl -X POST http://localhost:8000/classify \
  -F "file=@path/to/audio.wav"
```

### Test media URLs
```bash
curl http://localhost:8000/api/species/american_bullfrog/media
```

## Species Supported

The classifier recognizes 15 species:
- American Bullfrog
- American Toad
- Bird-Voiced Tree Frog
- Cope's Gray Treefrog
- Eastern Narrow-Mouthed Toad
- Eastern Spadefoot Toad
- Fowler's Toad
- Green Frog
- Green Tree Frog
- Northern Cricket Frog
- Not Frogs (background noise)
- Pickerel Frog
- Southern Leopard Frog
- Spring Peeper
- Upland Chorus Frog

## Next Steps

- Add audio playback for uploaded recordings
- Implement feedback system for incorrect predictions
- Add species detail pages with more information
- Deploy to production environment
- Add authentication for saving user recordings
