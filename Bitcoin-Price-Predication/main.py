"""
Bitcoin Price Prediction using Machine Learning
================================================
Models: Logistic Regression, SVM (poly kernel), XGBoost
Metric: ROC-AUC
Dataset: bitcoin.csv (OHLC 2014–2022)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import ConfusionMatrixDisplay
from xgboost import XGBClassifier
from sklearn import metrics

import os

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 – Load & explore data
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("Step 1: Loading and Exploring Data")
print("=" * 60)

df = pd.read_csv("data/bitcoin.csv")
print(f"\nShape: {df.shape}")
print("\nFirst 5 rows:")
print(df.head())
print("\nDescriptive statistics:")
print(df.describe())
print("\nData types & nulls:")
df.info()
print("\nNull counts:")
print(df.isnull().sum())

# Close price over time
plt.figure(figsize=(15, 5))
plt.plot(df["Close"])
plt.title("Bitcoin Close Price", fontsize=15)
plt.ylabel("Price in dollars")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_close_price.png", dpi=150)
plt.close()
print("\n[Saved] outputs/01_close_price.png")

# Verify Adj Close == Close (redundant column)
match = df[df["Close"] == df["Adj Close"]].shape
print(f"\nRows where Close == Adj Close: {match[0]} / {df.shape[0]}")
df = df.drop(["Adj Close"], axis=1)
print("'Adj Close' column dropped.")

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 – EDA: distributions & boxplots
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Step 2: EDA – Distributions & Boxplots")
print("=" * 60)

features_ohlc = ["Open", "High", "Low", "Close"]

# Distribution plots
plt.subplots(figsize=(20, 10))
for i, col in enumerate(features_ohlc):
    plt.subplot(2, 2, i + 1)
    sb.histplot(df[col], kde=True)
    plt.title(f"Distribution of {col}")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_distributions.png", dpi=150)
plt.close()
print("[Saved] outputs/02_distributions.png")

# Boxplots
plt.subplots(figsize=(20, 10))
for i, col in enumerate(features_ohlc):
    plt.subplot(2, 2, i + 1)
    sb.boxplot(y=df[col])
    plt.title(f"Boxplot of {col}")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/03_boxplots.png", dpi=150)
plt.close()
print("[Saved] outputs/03_boxplots.png")

# ─────────────────────────────────────────────────────────────────────────────
# Step 3 – Feature Engineering
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Step 3: Feature Engineering")
print("=" * 60)

# Parse date parts
splitted = df["Date"].str.split("-", expand=True)
df["year"]  = splitted[0].astype("int")
df["month"] = splitted[1].astype("int")
df["day"]   = splitted[2].astype("int")
df["Date"]  = pd.to_datetime(df["Date"])

print("\nDate columns added:")
print(df.head())

# Yearly mean bar charts
data_grouped = df.groupby("year").mean(numeric_only=True)
plt.subplots(figsize=(20, 10))
for i, col in enumerate(features_ohlc):
    plt.subplot(2, 2, i + 1)
    data_grouped[col].plot.bar()
    plt.title(f"Yearly Average {col}")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/04_yearly_averages.png", dpi=150)
plt.close()
print("[Saved] outputs/04_yearly_averages.png")

# Quarter-end indicator
df["is_quarter_end"] = np.where(df["month"] % 3 == 0, 1, 0)

# Derived features + target
df["open-close"] = df["Open"] - df["Close"]
df["low-high"]   = df["Low"]  - df["High"]
df["target"]     = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)

print("\nEngineered feature sample:")
print(df[["open-close", "low-high", "is_quarter_end", "target"]].head())

# Target class balance
plt.figure(figsize=(6, 6))
plt.pie(
    df["target"].value_counts().values,
    labels=["Down (0)", "Up (1)"],
    autopct="%1.1f%%",
    startangle=90,
)
plt.title("Target Class Distribution")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/05_target_distribution.png", dpi=150)
plt.close()
print("[Saved] outputs/05_target_distribution.png")

# Correlation heatmap (highly correlated features)
plt.figure(figsize=(10, 10))
numeric_df = df.select_dtypes(include=[np.number])
sb.heatmap(numeric_df.corr() > 0.9, annot=True, cbar=False)
plt.title("High Correlation Heatmap (> 0.9)")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/06_correlation_heatmap.png", dpi=150)
plt.close()
print("[Saved] outputs/06_correlation_heatmap.png")

# ─────────────────────────────────────────────────────────────────────────────
# Step 4 – Model Development & Evaluation
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Step 4: Model Development & Evaluation")
print("=" * 60)

feature_cols = ["open-close", "low-high", "is_quarter_end"]
X = df[feature_cols]
y = df["target"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Chronological 70/30 split (no shuffle — preserves time order)
split = int(len(X_scaled) * 0.7)
X_train, X_valid = X_scaled[:split], X_scaled[split:]
Y_train, Y_valid = y.values[:split],  y.values[split:]

print(f"\nTrain size: {len(X_train)} | Validation size: {len(X_valid)}")

models = [
    LogisticRegression(),
    SVC(kernel="poly", probability=True),
    XGBClassifier(eval_metric="logloss"),
]

results = []
for model in models:
    model.fit(X_train, Y_train)
    train_auc = metrics.roc_auc_score(Y_train, model.predict_proba(X_train)[:, 1])
    valid_auc = metrics.roc_auc_score(Y_valid, model.predict_proba(X_valid)[:, 1])
    results.append(
        {"Model": type(model).__name__, "Train ROC-AUC": round(train_auc, 4), "Val ROC-AUC": round(valid_auc, 4)}
    )
    print(f"\n{type(model).__name__}")
    print(f"  Train ROC-AUC : {train_auc:.4f}")
    print(f"  Val   ROC-AUC : {valid_auc:.4f}")

# Summary table
results_df = pd.DataFrame(results)
print("\n── Model Summary ──")
print(results_df.to_string(index=False))
results_df.to_csv(f"{OUTPUT_DIR}/model_results.csv", index=False)
print("[Saved] outputs/model_results.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Step 5 – Confusion Matrix (Logistic Regression)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Step 5: Confusion Matrix – Logistic Regression")
print("=" * 60)

fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay.from_estimator(models[0], X_valid, Y_valid, ax=ax)
ax.set_title("Confusion Matrix – Logistic Regression (Validation)")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/07_confusion_matrix.png", dpi=150)
plt.close()
print("[Saved] outputs/07_confusion_matrix.png")

print("\n" + "=" * 60)
print("Pipeline complete. All outputs saved to ./outputs/")
print("=" * 60)
