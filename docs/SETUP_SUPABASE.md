# Setup Instructions for Supabase Storage Integration

## What We Built

This setup connects your React frontend to a Supabase storage bucket called "Species Catalog" that contains:
- `audio/{slug}/{slug}.mp3` - Audio files for each species
- `images/{slug}/{slug}.jpg` - Image files for each species

The Express server generates signed URLs (valid for 1 hour) to securely access these files.

## Setup Steps

### 1. Configure Supabase Credentials

Copy the example environment file and add your Supabase credentials:

```bash
cd frontend/server
cp .env.example .env
```

Edit `.env` and add your Supabase project details:
- `SUPABASE_URL`: Your Supabase project URL (e.g., https://xxxxx.supabase.co)
- `SUPABASE_SERVICE_ROLE_KEY`: Your service role key (found in Supabase Dashboard → Settings → API)

⚠️ **Important**: Use the SERVICE_ROLE_KEY, not the anon key, as it bypasses RLS policies.

### 2. Verify Your Supabase Storage Structure

Make sure your Supabase storage bucket "Species Catalog" has this structure:

```
Species Catalog/
├── audio/
│   ├── american_toad/
│   │   └── american_toad.mp3
│   ├── bird_voiced_tree_frog/
│   │   └── bird_voiced_tree_frog.mp3
│   └── ... (all 14 species)
└── images/
    ├── american_toad/
    │   └── american_toad.jpg
    ├── bird_voiced_tree_frog/
    │   └── bird_voiced_tree_frog.jpg
    └── ... (all 14 species)
```

### 3. Start the Backend Server

```bash
cd frontend/server
npm start
```

The server will run on http://localhost:8000

### 4. Configure Frontend to Use Backend

Create or edit `frontend/.env`:

```bash
VITE_API_BASE=http://localhost:8000
```

### 5. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will run on http://localhost:5173

## API Endpoints

The server provides these endpoints:

- `GET /health` - Health check
- `GET /api/species/:slug/media` - Get signed URLs for a single species
- `POST /api/species/media/batch` - Get signed URLs for multiple species (used by frontend)
- `GET /api/storage/list/:folder` - List files in a bucket folder (debugging)

## Testing

1. Visit http://localhost:5173
2. Click on "Species Dictionary"
3. The page should load images and audio from your Supabase bucket
4. If there are issues, check the browser console and server logs

## Debugging

If files aren't loading:

1. **Check server logs** for error messages
2. **Test the API directly**:
   ```bash
   curl http://localhost:8000/api/species/american_toad/media
   ```
3. **Verify bucket permissions** in Supabase Dashboard → Storage
4. **Check file names match** the slug names exactly (case-sensitive)
5. **Use the list endpoint** to see what files exist:
   ```bash
   curl http://localhost:8000/api/storage/list/audio
   curl http://localhost:8000/api/storage/list/images
   ```

## Species Slug Reference

The following slugs are used (must match folder/file names):

- american_toad
- bird_voiced_tree_frog
- american_bullfrog
- copes_gray_treefrog
- eastern_narrow_mouthed_toad
- eastern_spadefoot_toad
- fowlers_toad
- green_frog
- green_tree_frog
- northern_cricket_frog
- pickerel_frog
- southern_leopard_frog
- spring_peeper
- upland_chorus_frog
