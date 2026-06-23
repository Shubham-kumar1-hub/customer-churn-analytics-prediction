# 📊 Telco Customer Churn Prediction

An end-to-end Data Science project that predicts customer churn for a 
telecom company, identifies the key drivers behind churn using SHAP, 
and translates predictions into a quantified business retention strategy.

**🔗 Live Demo:** [churn-dashboard-qii9.onrender.com](https://churn-dashboard-qii9.onrender.com)
**🔗 API Docs:** [customer-churn-analytics-prediction.onrender.com/docs](https://customer-churn-analytics-prediction.onrender.com/docs)

---

## 🎯 Business Problem

Customer churn directly impacts recurring revenue. This project answers:
**"Which customers are likely to leave, and what should the business do about it?"**

Using the Telco Customer Churn dataset (7,043 customers, 21 features), 
I built a model that doesn't just predict churn — it segments customers 
by risk and estimates the financial impact of a targeted retention strategy.

---

## 📈 Key Results

| Metric | Value |
|---|---|
| Best Model | Logistic Regression (class_weight='balanced') |
| AUC-ROC | 0.833 |
| Recall | 0.789 |
| High-Risk Customers Identified | 372 |
| Estimated Annual Revenue at Risk | $358,667 |
| Estimated Revenue Saved (30% retention) | **$107,600** |

---

## 🔍 Approach

### 1. Data Pipeline
- Ingested raw CSV into **MySQL**, queried via SQLAlchemy
- Handled missing values (11 rows with blank `TotalCharges`)

### 2. Exploratory Data Analysis
- Identified key churn drivers: **tenure**, **contract type**, 
  **fiber optic internet**, **payment method**
- Found severe multicollinearity between `tenure` and `TotalCharges` 
  (r=0.83) — dropped `TotalCharges` to stabilize the linear model

### 3. Preprocessing
- Label encoding for binary features
- **Ordinal encoding** for `Contract` (preserving Month-to-month < 
  One year < Two year hierarchy — not naively one-hot encoded)
- One-hot encoding for true nominal features (`InternetService`, `PaymentMethod`)
- Stratified train-test split, scaling fit only on training data (no leakage)

### 4. Modeling — Systematic Comparison
Tested **3 algorithms × 2 imbalance-handling techniques** (5 valid configs):

| Model | Method | Recall | AUC-ROC |
|---|---|---|---|
| **Logistic Regression** | **class_weight** | **0.789** | **0.833** |
| Logistic Regression | SMOTE | 0.727 | 0.827 |
| XGBoost | SMOTE | 0.639 | 0.810 |
| Random Forest | class_weight | 0.489 | 0.814 |
| XGBoost | scale_pos_weight | 0.666 | 0.807 |

**Decision:** Selected Logistic Regression despite Random Forest's higher 
accuracy (0.783 vs 0.729), because Recall and AUC-ROC matter more for 
churn — missing an actual churner costs more than a false alarm.

### 5. Explainability (SHAP)
- Validated EDA hypotheses against model-level feature attributions
- Built local explanations contrasting a retained customer (5.1% churn 
  probability) against a churned customer (94.4% churn probability)

### 6. Business Translation
- Segmented customers into High/Medium/Low risk
- Validated segmentation: High Risk bucket had 61.6% actual churn rate 
  vs 7.8% in Low Risk — confirming the model's probabilities carry real signal
- Quantified retention ROI assuming a conservative 30% intervention success rate

### 7. Deployment
- **FastAPI** backend serving real-time predictions
- **Streamlit** dashboard for single predictions + batch risk insights
- **Dockerized** both services with Docker Compose for local orchestration
- **Deployed live on Render** (two independent web services)

---

## 🛠️ Tech Stack

`Python` `Pandas` `Scikit-learn` `XGBoost` `SHAP` `imbalanced-learn` 
`MySQL` `SQLAlchemy` `FastAPI` `Streamlit` `Docker` `Render`

---

## 📁 Project Structure

churn-prediction/

├── notebooks/

│   ├── 01_eda.ipynb

│   ├── 02_preprocessing.ipynb

│   └── 03_modeling.ipynb

├── api/

│   ├── main.py

│   ├── schema.py

│   └── Dockerfile

├── app/

│   ├── streamlit_app.py

│   └── Dockerfile

├── data/

├── docker-compose.yml

└── requirements.txt

---

## 🚀 Run Locally

```bash
git clone https://github.com/Shubham-kumar1-hub/customer-churn-analytics-prediction
cd customer-churn-analytics-prediction
docker-compose up --build
```

Visit `http://localhost:8501` for the dashboard, `http://localhost:8000/docs` for the API.

---

## 📌 Key Learnings

- A simpler, well-tuned model (Logistic Regression) outperformed a more 
  complex one (XGBoost, Random Forest) on the metric that actually mattered 
  for the business — a reminder that model complexity ≠ business value
- Ordinal relationships in categorical data (like contract length) should 
  be explicitly encoded, not flattened into one-hot — preserving this 
  signal improved interpretability without hurting performance
- SHAP-based local explanations make a model's decisions defensible to 
  non-technical stakeholders, not just accurate on paper