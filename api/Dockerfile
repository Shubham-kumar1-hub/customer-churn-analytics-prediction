# ---------------------------------------------
# FASTAPI SERVICE DOCKERFILE
# Builds a container that runs the churn prediction API
# ---------------------------------------------

FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY api/ ./api/

# Copy model artifacts — needed at runtime for predictions
COPY data/final_churn_model.pkl ./data/
COPY data/scaler.pkl ./data/
COPY data/feature_names.pkl ./data/

WORKDIR /app/api

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]