# ----------------------------------------------
# STREAMLIT SERVICE DOCKERFILE
# Builds a container that runs the dashboard
# ----------------------------------------------

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Streamlit needs the results CSV for the Risk Insights tab
COPY data/risk_segmented_results.csv ./data/

WORKDIR /app/app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]