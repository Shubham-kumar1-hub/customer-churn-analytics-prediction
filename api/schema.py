# INPUT SCHEMA
# Defines the exact shape of data the API expects.
# Pydantic automatically validates types and raises
# clean errors if something is missing/wrong type

from pydantic import BaseModel
from typing import Literal

class CustomerInput(BaseModel):
    gender: Literal["Male", "Female"]
    SeniorCitizen: int  # 0 or 1
    Partner: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]
    tenure: int
    PhoneService: Literal["Yes", "No"]
    MultipleLines: Literal["Yes", "No"]
    OnlineSecurity: Literal["Yes", "No"]
    OnlineBackup: Literal["Yes", "No"]
    DeviceProtection: Literal["Yes", "No"]
    TechSupport: Literal["Yes", "No"]
    StreamingTV: Literal["Yes", "No"]
    StreamingMovies: Literal["Yes", "No"]
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: Literal["Yes", "No"]
    MonthlyCharges: float
    InternetService: Literal["DSL", "Fiber optic", "No"]
    PaymentMethod: Literal[
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)"
    ]

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 2,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "MonthlyCharges": 70.70,
                "InternetService": "Fiber optic",
                "PaymentMethod": "Electronic check"
            }
        }