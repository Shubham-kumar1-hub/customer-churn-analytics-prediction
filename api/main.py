# FASTAPI APP -> CHURN PREDICTION SERVICE
# Loads trained model, scaler, and feature names once
# at startup. Each request preprocesses raw input
# exactly like training, then returns a prediction.

from fastapi import FastAPI
import pandas as pd
import joblib
from schema import CustomerInput

app = FastAPI(title="Churn Prediction API")

# --------------------------------------------
# Loading ARTIFACTS Once at Startup
# --------------------------------------------

model = joblib.load("../data/final_churn_model.pkl")
scaler = joblib.load("../data/scaler.pkl")
feature_names = joblib.load("../data/feature_names.pkl")

# Same binary mpping used during training
binary_map = {
    "Yes": 1, "No": 0,
    "Male": 1, "Female": 0
}

contract_map = {"Month-to-month": 0, "One year": 1, "Two year": 2}

def preprocess(data : CustomerInput) -> pd.DataFrame:
    """
    Replicates the EXACT preprocessing pipeline from
    02_preprocessing.ipynb - binary mapping, ordinal
    encoding, one-hot encoding, scaling - so the API
    input matches what the model was trained on.
    """
    row = data.dict()

    # Binary encode
    binary_cols = ["gender", "Partner", "Dependents", "PhoneService",
                   "MultipleLines", "OnlineSecurity", "OnlineBackup",
                   "DeviceProtection", "TechSupport", "StreamingTV",
                   "StreamingMovies", "PaperlessBilling"]
    
    for col in binary_cols:
        row[col] = binary_map[row[col]]

    # Ordinal encode
    row["Contract"] = contract_map[row["Contract"]]

    # One-hot encode InternetService and PaymentMethod
    row["InternetService_Fiber optic"] = 1 if row["InternetService"] == "Fiber optic" else 0
    row["InternetService_No"] = 1 if row["InternetService"] == "No" else 0
    del row["InternetService"]

    row["PaymentMethod_Credit card (automatic)"] = 1 if row["PaymentMethod"] == "Credit card (automatic)" else 0
    row["PaymentMethod_Electronic check"] = 1 if row["PaymentMethod"] == "Electronic check" else 0
    row["PaymentMethod_Mailed check"] = 1 if row["PaymentMethod"] == "Mailed check" else 0
    del row["PaymentMethod"]

    # Converting to dataframe
    df_row = pd.DataFrame([row])

    # Scaling numeric features — same scaler fitted during training
    df_row[["tenure", "MonthlyCharges"]] = scaler.transform(df_row[["tenure", "MonthlyCharges"]])

    # CRITICAL: reordering columns to match training order exactly
    df_row = df_row[feature_names]

    return df_row

@app.get("/")
def root():
    return {"message": "Telco Churn Prediction API is running"}


@app.post("/predict")
def predict(customer: CustomerInput):
    processed = preprocess(customer)

    churn_probability = model.predict_proba(processed)[0][1]

    if churn_probability > 0.7:
        risk_segment = "High Risk"
    elif churn_probability > 0.4:
        risk_segment = "Medium Risk"
    else:
        risk_segment = "Low Risk"

    return {
        "churn_probability": round(float(churn_probability), 4),
        "risk_segment": risk_segment,
        "prediction": "Churn" if churn_probability > 0.5 else "No Churn"
    }