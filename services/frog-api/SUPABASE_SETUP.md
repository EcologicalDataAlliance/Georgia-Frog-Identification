# Supabase Setup Guide for Frog Classifier API

This guide will walk you through setting up Supabase to store audio uploads and prediction metadata.

## Why Use Supabase?

- **Data Collection**: Save all user recordings for future model training
- **Quality Control**: Review predictions and identify edge cases
- **User Feedback**: Collect corrections to improve the model
- **Analytics**: Track model performance over time

## Prerequisites

- Supabase account (free tier works fine)
- Project created in Supabase

## Step 1: Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Click **Project Settings** (gear icon) → **API**
3. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: For client-side (not needed for this API)
   - **service_role key**: For server-side (**KEEP SECRET!**)

## Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```powershell
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   SUPABASE_URL=https://cyrcuzsugsltxkthcamm.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_BUCKET=frog-user-recordings
   SAVE_AUDIO_UPLOADS=true
   ```

3. **IMPORTANT**: Never commit `.env` to Git! It's already in `.gitignore`.

## Step 3: Create Storage Bucket

1. In Supabase Dashboard, go to **Storage**
2. Click **New Bucket**
3. Settings:
   - **Name**: `frog-user-recordings`
   - **Public**: **OFF** (keep private)
   - **File size limit**: 10 MB (adjust as needed)
   - **Allowed MIME types**: Leave blank (or add: audio/wav, audio/mpeg, audio/mp3, etc.)
4. Click **Create Bucket**

## Step 4: Set Up Database Tables

1. Go to **SQL Editor** in Supabase Dashboard
2. Click **New Query**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** or press F5

This creates:
- `predictions` table - stores all audio upload results
- `feedback` table - stores user corrections
- Indexes for fast queries
- Helper functions for analytics

### Table Structures

**predictions:**
```
id                  | BIGSERIAL PRIMARY KEY
filename            | TEXT (stored filename in bucket)
original_filename   | TEXT (user's original filename)
prediction          | TEXT (primary predicted species)
top_3_predictions   | JSONB (array of top 3 with confidence)
all_probabilities   | JSONB (full probability distribution)
timestamp           | TIMESTAMPTZ
created_at          | TIMESTAMPTZ
```

**feedback:**
```
id                  | BIGSERIAL PRIMARY KEY
filename            | TEXT (references predictions filename)
predicted_species   | TEXT (what model predicted)
actual_species      | TEXT (user's correction)
confidence          | FLOAT (model's confidence)
notes               | TEXT (optional user notes)
timestamp           | TIMESTAMPTZ
created_at          | TIMESTAMPTZ
```

## Step 5: Test the Integration

1. Start your API server:
   ```powershell
   uvicorn main:app --reload
   ```

2. You should see this message on startup:
   ```
   ✅ Supabase client initialized - audio uploads will be saved
   ```

3. Upload a test audio file:
   ```powershell
   python test_audio.py
   ```

4. Check Supabase Dashboard:
   - **Storage** → `frog-user-recordings` → You should see the uploaded file
   - **Table Editor** → `predictions` → You should see a new row with metadata

## Step 6: Verify Storage Policies

If uploads fail with permission errors:

1. Go to **Storage** → `frog-user-recordings` → **Policies**
2. Ensure these policies exist:

**Allow service role to upload:**
```sql
CREATE POLICY "Service role can upload"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'frog-user-recordings');
```

**Allow service role to read:**
```sql
CREATE POLICY "Service role can read"
ON storage.objects FOR SELECT
TO service_role
USING (bucket_id = 'frog-user-recordings');
```

## Testing Feedback Endpoint

```python
import requests

feedback = {
    "filename": "20251117_220403_american_toad_0.80.mp3",
    "predicted_species": "american_toad",
    "actual_species": "fowlers_toad",
    "confidence": 0.80,
    "notes": "Close species, easy to confuse"
}

response = requests.post(
    "http://localhost:8000/feedback",
    json=feedback
)
print(response.json())
```

Check **Table Editor** → `feedback` for the new entry.

## Querying Your Data

### Get all predictions:
```sql
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10;
```

### Get prediction distribution:
```sql
SELECT prediction, COUNT(*) as count
FROM predictions
GROUP BY prediction
ORDER BY count DESC;
```

### Get average confidence by species:
```sql
SELECT 
    prediction,
    COUNT(*) as total,
    AVG((top_3_predictions->0->>'confidence')::float) as avg_confidence
FROM predictions
GROUP BY prediction
ORDER BY total DESC;
```

### Get all user corrections:
```sql
SELECT * FROM feedback ORDER BY created_at DESC;
```

### Model accuracy (based on feedback):
```sql
SELECT * FROM get_model_stats();
```

## Docker Deployment with Supabase

When deploying via Docker, pass environment variables:

```powershell
docker run -d \
  -p 8000:80 \
  -e SAVE_AUDIO_UPLOADS=true \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_KEY=your-service-role-key \
  -e SUPABASE_BUCKET=frog-user-recordings \
  frog-rf-api
```

Or use a `.env` file with docker-compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:80"
    env_file:
      - .env
```

## Troubleshooting

### "Supabase client not initialized"
- Check `.env` file exists and has correct values
- Ensure `SAVE_AUDIO_UPLOADS=true`
- Restart the API server after changing `.env`

### "Failed to save to Supabase"
- Check bucket name matches: `frog-user-recordings`
- Verify service_role key has correct permissions
- Check Supabase dashboard for error logs

### "predictions table does not exist"
- Run `supabase_schema.sql` in SQL Editor
- Check spelling: `predictions` (plural)

### Storage upload fails
- Check storage policies (Step 6)
- Ensure bucket is created and named correctly
- Verify file size is under bucket limit

## Data Privacy & Security

**Important Reminders:**

1. **Never commit `.env` to Git** - Contains secret keys
2. **Use private buckets** - User audio should not be public
3. **Review data retention** - Delete old recordings as needed
4. **Inform users** - Let beta testers know audio is being saved
5. **Service role key** - Never expose in client-side code

## Next Steps

Once everything is working:

1. **Beta Testing**: Share API with testers and collect recordings
2. **Review Data**: Analyze predictions and feedback in Supabase
3. **Model Improvement**: Use collected data for retraining
4. **Cloud Deployment**: Deploy API to production with Supabase configured

## Support

If you encounter issues:
- Check Supabase logs: Dashboard → **Logs**
- Check API logs: Terminal output from uvicorn
- Verify table schema matches `supabase_schema.sql`
- Test with small audio files first (< 1 MB)
