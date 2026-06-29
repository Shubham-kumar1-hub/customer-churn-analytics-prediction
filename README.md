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
| Best Model | Logistic Regression (class_weight='balanced', tuned: C=0.1, L1 penalty) |
| AUC-ROC (test set) | 0.8346 |
| Recall (test set) | 0.7834 |
| Precision (test set) | 0.4933 |
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

**Initial screen** — 3 algorithms × 2 imbalance-handling techniques, single train/test split:

| Model | Method | Recall | AUC-ROC |
|---|---|---|---|
| **Logistic Regression** | **class_weight** | **0.789** | **0.833** |
| Logistic Regression | SMOTE | 0.727 | 0.827 |
| XGBoost | SMOTE | 0.639 | 0.810 |
| Random Forest | class_weight | 0.489 | 0.814 |
| XGBoost | scale_pos_weight | 0.666 | 0.807 |

**Validation via 5-fold Stratified CV** (training set only, SMOTE applied inside each fold via `imblearn.Pipeline` to avoid leakage) — confirms the initial screen wasn't an artifact of one particular train/test split:

| Model | Recall (mean ± std) | AUC-ROC (mean ± std) |
|---|---|---|
| **Logistic Regression (class_weight)** | **0.797 ± 0.017** | **0.845 ± 0.006** |
| Logistic Regression (SMOTE) | 0.738 ± 0.027 | 0.835 ± 0.008 |
| Random Forest (class_weight) | 0.480 ± 0.023 | 0.822 ± 0.010 |

**Hyperparameter tuning** — `GridSearchCV` over `C` (8 values, 0.0001–1000) and `penalty` (L1/L2), 5-fold CV, scored on AUC-ROC:
- Best params: `C=0.1`, `penalty='l1'`
- Best CV AUC-ROC: 0.845
- L1 regularization zeroed out 4 of 21 features entirely (`gender`, `DeviceProtection`, `PaymentMethod_Credit card (automatic)`, `PaymentMethod_Mailed check`) — independently confirming these weren't meaningful churn drivers, consistent with SHAP not flagging them either.

**Decision:** Selected Logistic Regression despite Random Forest's higher 
accuracy (0.783 vs 0.729), because Recall and AUC-ROC matter more for 
churn — missing an actual churner costs more than a false alarm. Tuning 
confirmed the default hyperparameters were already close to optimal, 
with the tuned model providing a modest, genuine AUC improvement 
(0.833 → 0.835 on CV) rather than a threshold-trading artifact.

### 5. Explainability (SHAP)
- Validated EDA hypotheses against model-level feature attributions
- Built local explanations contrasting a retained customer (5.1% churn 
  probability) against a churned customer (94.4% churn probability)
- Top SHAP drivers (Contract, tenure, Fiber optic internet, Electronic 
  check payment) independently corroborated by the L1-regularized 
  coefficient magnitudes from hyperparameter tuning

### 6. Business Translation
- Segmented customers into High/Medium/Low risk
- Validated segmentation: High Risk bucket had 61.6% actual churn rate 
  vs 7.8% in Low Risk — confirming the model's probabilities carry real signal
- Quantified retention ROI assuming a conservative 30% intervention success rate

### 7. Deployment
- **FastAPI** backend serving real-time predictions
- **Streamlit** dashboard for single predictions + batch risk insights
- **Dockerized** both services with Docker Compose for local orchestration
- **Deployed live on Render** (two independent web services), running 
  the CV-validated, hyperparameter-tuned model

---

## ⚠️ Known Limitations

Being upfront about what this project doesn't yet handle correctly:

- **`tenure = 0` customers are absent from training data.** During 
  ingestion, 11 rows with blank `TotalCharges` were dropped rather than 
  imputed. Those 11 rows are exactly the customers with `tenure = 0` 
  (not yet billed). Since `tenure` is the model's top SHAP driver, this 
  means the model has zero training signal for brand-new signups — the 
  segment the model's own analysis flags as highest-risk. The dataset's 
  minimum `tenure` is currently 1, not 0. Fix: impute `TotalCharges = 0` 
  for these rows instead of dropping them (the column is dropped from 
  the model anyway due to multicollinearity with `tenure`, so the fix 
  is free in terms of final features — it only matters because dropping 
  rows also removed `tenure = 0` from the training distribution).
- **Threshold inconsistency between binary prediction and risk segments.** 
  The API currently returns a binary `Churn`/`No Churn` label at a 0.5 
  cutoff, and a separate three-tier risk segment at 0.4/0.7 cutoffs. For 
  any customer scoring between 0.4 and 0.7, these two outputs can send 
  conflicting signals (e.g. `prediction: "Churn"` alongside 
  `risk_segment: "Medium Risk"`, which the dashboard then displays as a 
  low-urgency warning despite the binary label saying churn is predicted). 
  Neither threshold was derived from a cost-of-error analysis. Fix: derive 
  a single threshold from the relative cost of a missed churner vs. a 
  wasted retention offer, then define risk tiers as bands around that one 
  threshold so the two outputs can't disagree.
- No automated tests verifying preprocessing logic in `api/main.py` stays 
  in sync with the notebooks it replicates.
- No model versioning, drift monitoring, or retraining pipeline — this 
  is a static, one-time-trained model.

---

## 🛠️ Tech Stack

`Python` `Pandas` `Scikit-learn` `XGBoost` `imbalanced-learn` `SHAP` 
`MySQL` `SQLAlchemy` `FastAPI` `Streamlit` `Docker` `Render`

---

# 📁 Project Structure

```
customer-churn-analytics-prediction/
│
├── notebooks/
│   ├── 01_eda.ipynb              # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb    # Cleaning, encoding, scaling
│   └── 03_modeling.ipynb         # Model training, CV, tuning, comparison, SHAP
│
├── api/
│   ├── main.py                   # FastAPI app + /predict endpoint
│   ├── schema.py                 # Pydantic input validation schema
│   └── Dockerfile                # Container build for FastAPI service
│
├── app/
│   ├── streamlit_app.py          # Streamlit dashboard (prediction + insights)
│   └── Dockerfile                # Container build for Streamlit service
│
├── data/
│   ├── Customer_Churn.csv        # Raw dataset
│   ├── X_train.csv               # Preprocessed training features
│   ├── X_test.csv                # Preprocessed test features
│   ├── y_train.csv               # Training labels
│   ├── y_test.csv                # Test labels
│   ├── scaler.pkl                # Fitted StandardScaler (tenure, MonthlyCharges)
│   ├── feature_names.pkl         # Column order for inference consistency
│   ├── final_churn_model.pkl     # Trained, CV-validated, tuned Logistic Regression model
│   └── risk_segmented_results.csv # Test set predictions + risk segments
│
├── docker-compose.yml            # Orchestrates FastAPI + Streamlit containers
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview, methodology, results
```

## Folder Purpose Summary

| Folder | Purpose |
|---|---|
| `notebooks/` | End-to-end analysis — EDA → preprocessing → modeling |
| `api/` | Production inference service (FastAPI) |
| `app/` | User-facing dashboard (Streamlit) |
| `data/` | Datasets, trained model artifacts, preprocessing objects |
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
- A single train/test split can make a model selection decision look 
  more conclusive than it is. 5-fold cross-validation confirmed the 
  initial screen's winner was genuinely robust, not an artifact of one 
  particular split — and revealed that hyperparameter tuning had little 
  room to improve on the defaults, which is itself a useful result
- Ordinal relationships in categorical data (like contract length) should 
  be explicitly encoded, not flattened into one-hot — preserving this 
  signal improved interpretability without hurting performance
- SHAP-based local explanations make a model's decisions defensible to 
  non-technical stakeholders, not just accurate on paper
- L1 regularization can serve as an independent cross-check on feature 
  importance — features it zeroed out matched features SHAP also 
  ranked as low-impact, increasing confidence in both methods