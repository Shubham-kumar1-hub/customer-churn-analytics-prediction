# STREAMLIT DASHBOARD — CHURN PREDICTION
# Two tabs: single customer prediction (calls FastAPI)
# and batch insights from the saved results CSV

import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Telco Churn Dashboard", layout="wide")

st.title("📊 Telco Customer Churn Prediction Dashboard")

tab1, tab2 = st.tabs(["🔍 Single Prediction", "📈 Risk Insights"])

# ---------------------------------------------
# TAB 1 — SINGLE CUSTOMER PREDICTION
# Sends form input to the FastAPI /predict endpoint
# ---------------------------------------------

with tab1:
    st.subheader("Predict Churn for a Single Customer")

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("Gender", ["Female", "Male"])
        SeniorCitizen = st.selectbox("Senior Citizen", [0, 1])
        Partner = st.selectbox("Partner", ["Yes", "No"])
        Dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, value=12)
        PhoneService = st.selectbox("Phone Service", ["Yes", "No"])

    with col2:
        MultipleLines = st.selectbox("Multiple Lines", ["Yes", "No"])
        InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        OnlineSecurity = st.selectbox("Online Security", ["Yes", "No"])
        OnlineBackup = st.selectbox("Online Backup", ["Yes", "No"])
        DeviceProtection = st.selectbox("Device Protection", ["Yes", "No"])
        TechSupport = st.selectbox("Tech Support", ["Yes", "No"])

    with col3:
        StreamingTV = st.selectbox("Streaming TV", ["Yes", "No"])
        StreamingMovies = st.selectbox("Streaming Movies", ["Yes", "No"])
        Contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        PaperlessBilling = st.selectbox("Paperless Billing", ["Yes", "No"])
        PaymentMethod = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check",
            "Bank transfer (automatic)", "Credit card (automatic)"
        ])
        MonthlyCharges = st.number_input("Monthly Charges ($)", min_value=0.0, value=70.0)

    if st.button("Predict Churn", type="primary"):
        payload = {
            "gender": gender, "SeniorCitizen": SeniorCitizen, "Partner": Partner,
            "Dependents": Dependents, "tenure": tenure, "PhoneService": PhoneService,
            "MultipleLines": MultipleLines, "OnlineSecurity": OnlineSecurity,
            "OnlineBackup": OnlineBackup, "DeviceProtection": DeviceProtection,
            "TechSupport": TechSupport, "StreamingTV": StreamingTV,
            "StreamingMovies": StreamingMovies, "Contract": Contract,
            "PaperlessBilling": PaperlessBilling, "MonthlyCharges": MonthlyCharges,
            "InternetService": InternetService, "PaymentMethod": PaymentMethod
        }

        try:
            response = requests.post("https://customer-churn-analytics-prediction.onrender.com/predict", json=payload)
            result = response.json()

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Churn Probability", f"{result['churn_probability']*100:.1f}%")
            c2.metric("Risk Segment", result['risk_segment'])
            c3.metric("Prediction", result['prediction'])

            if result['risk_segment'] == "High Risk":
                st.error("⚠️ This customer is at HIGH risk of churning. Recommend immediate retention action.")
            elif result['risk_segment'] == "Medium Risk":
                st.warning("This customer is at moderate risk. Consider a check-in.")
            else:
                st.success("This customer is low risk. No action needed.")

        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            st.info("Make sure the FastAPI server is running on https://customer-churn-analytics-prediction.onrender.com")

# ---------------------------------------------
# TAB 2 — RISK INSIGHTS (Batch view)
# Loads the pre-computed results from modeling notebook
# ---------------------------------------------

with tab2:
    st.subheader("Risk Segmentation Overview (Test Set)")

    try:
        results_df = pd.read_csv("../data/risk_segmented_results.csv")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", len(results_df))
        col2.metric("High Risk Customers", len(results_df[results_df['Risk_Segment'] == 'High Risk']))
        col3.metric("Avg Churn Probability", f"{results_df['Churn_Probability'].mean()*100:.1f}%")

        st.markdown("---")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.write("**Customers per Risk Segment**")
            st.bar_chart(results_df['Risk_Segment'].value_counts())

        with chart_col2:
            st.write("**Actual Churn Rate by Segment**")
            churn_by_segment = results_df.groupby('Risk_Segment')['Actual_Churn'].mean()
            st.bar_chart(churn_by_segment)

        st.markdown("---")
        st.write("**Sample Data**")
        st.dataframe(results_df.head(20))

    except FileNotFoundError:
        st.error("risk_segmented_results.csv not found. Run the modeling notebook first.")