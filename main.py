# STEP 1: Import libraries
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap

# STEP 2: Create fake business data
np.random.seed(42)

days = 365
data = {
    "day": pd.date_range(start="2024-01-01", periods=days),
    "users": np.random.normal(1000, 100, days),
    "revenue": np.random.normal(5000, 500, days),
    "server_delay": np.random.normal(200, 30, days),
}

df = pd.DataFrame(data)

# Add problem period
df.loc[300:320, "server_delay"] += 300
df.loc[300:320, "users"] -= 400
df.loc[300:320, "revenue"] -= 2000

# STEP 3: Clean data
df.dropna(inplace=True)
df.set_index("day", inplace=True)

# STEP 4: Anomaly Detection
features = df[["users", "revenue", "server_delay"]]

iso_model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = iso_model.fit_predict(features)
df["anomaly"] = df["anomaly"].map({1: 0, -1: 1})

# STEP 5: Future failure label
df["future_failure"] = df["anomaly"].shift(-7)
df.dropna(inplace=True)

# STEP 6: Train prediction model
X = df[["users", "revenue", "server_delay"]]
y = df["future_failure"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

print("✅ Model trained successfully")

# STEP 7: Explainability
explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_train)

print("✅ Explainable AI ready")
import pickle

# Save Isolation Forest
with open("anomaly_model.pkl", "wb") as f:
    pickle.dump(iso_model, f)

# Save Prediction Model
with open("failure_model.pkl", "wb") as f:
    pickle.dump(clf, f)

# Save processed data (for dashboard)
df.to_csv("processed_data.csv")

print("✅ Models and data saved successfully")
import shap

# Create SHAP explainer
shap_explainer = shap.TreeExplainer(clf)

# Save explainer
with open("shap_explainer.pkl", "wb") as f:
    pickle.dump(shap_explainer, f)

print("✅ SHAP explainer saved")
