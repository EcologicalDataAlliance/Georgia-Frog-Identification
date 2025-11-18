FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency lists and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model artifacts
COPY main.py ./
# Copy any model files present in the context
COPY rf_calibrated_model.joblib ./
COPY scaler.joblib ./
COPY feature_columns.json ./

# Environment variables (can be overridden at runtime)
ENV SAVE_AUDIO_UPLOADS=false
# Set these via docker run -e or docker-compose
# ENV SUPABASE_URL=
# ENV SUPABASE_KEY=
# ENV SUPABASE_BUCKET=frog-user-recordings

# Expose port 80 for Uvicorn
EXPOSE 80

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]