-- Supabase Database Schema for Frog Classifier API
-- Run these SQL commands in your Supabase SQL Editor

-- 1. Predictions Table
-- Stores all audio upload predictions with metadata
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    prediction TEXT NOT NULL,
    top_3_predictions JSONB NOT NULL,
    all_probabilities JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes for common queries
CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_prediction ON predictions(prediction);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role to insert/select (adjust as needed)
CREATE POLICY "Allow service role full access" ON predictions
    FOR ALL
    USING (true);


-- 2. Feedback Table
-- Stores user corrections for incorrect predictions
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    predicted_species TEXT NOT NULL,
    actual_species TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_feedback_timestamp ON feedback(timestamp DESC);
CREATE INDEX idx_feedback_predicted ON feedback(predicted_species);
CREATE INDEX idx_feedback_actual ON feedback(actual_species);

-- Enable RLS
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow service role full access" ON feedback
    FOR ALL
    USING (true);


-- 3. Storage Bucket (create via Supabase Dashboard or run this)
-- Note: Storage buckets are typically created via Dashboard > Storage
-- If using SQL, ensure you have proper permissions:

INSERT INTO storage.buckets (id, name, public)
VALUES ('frog-user-recordings', 'frog-user-recordings', false)
ON CONFLICT (id) DO NOTHING;

-- Set up storage policies (adjust as needed)
CREATE POLICY "Service role can upload files"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'frog-user-recordings');

CREATE POLICY "Service role can read files"
ON storage.objects FOR SELECT
TO service_role
USING (bucket_id = 'frog-user-recordings');


-- Optional: View for analysis
CREATE OR REPLACE VIEW prediction_accuracy AS
SELECT 
    p.prediction,
    COUNT(*) as total_predictions,
    AVG((p.top_3_predictions->0->>'confidence')::float) as avg_confidence,
    COUNT(f.id) as feedback_count
FROM predictions p
LEFT JOIN feedback f ON p.filename = f.filename
GROUP BY p.prediction
ORDER BY total_predictions DESC;


-- Optional: Function to get model performance metrics
CREATE OR REPLACE FUNCTION get_model_stats()
RETURNS TABLE (
    total_predictions BIGINT,
    total_feedback BIGINT,
    accuracy_rate FLOAT,
    most_common_prediction TEXT,
    avg_confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT p.id) as total_predictions,
        COUNT(DISTINCT f.id) as total_feedback,
        CASE 
            WHEN COUNT(DISTINCT f.id) > 0 
            THEN 1.0 - (COUNT(DISTINCT f.id)::FLOAT / COUNT(DISTINCT p.id)::FLOAT)
            ELSE NULL
        END as accuracy_rate,
        MODE() WITHIN GROUP (ORDER BY p.prediction) as most_common_prediction,
        AVG((p.top_3_predictions->0->>'confidence')::float) as avg_confidence
    FROM predictions p
    LEFT JOIN feedback f ON p.filename = f.filename;
END;
$$ LANGUAGE plpgsql;
