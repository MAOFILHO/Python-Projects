"""
train.py
--------
Handles train/test splitting, feature standardisation, SVM training,
and GridSearchCV hyperparameter tuning.
"""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

RANDOM_STATE = 2529
TEST_SIZE = 0.3

# Numeric columns that need standardisation
SCALE_COLS = ["CreditScore", "Age", "Tenure", "Balance", "Estimated Salary"]

# Hyperparameter grid (matches the notebook exactly)
PARAM_GRID = {
    "C": [0.1, 1, 10],
    "gamma": [1, 0.1, 0.01],
    "kernel": ["rbf"],
    "class_weight": ["balanced"],
}


# ── helpers ────────────────────────────────────────────────────────────────

def split_and_scale(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split into train / test, then standardise numeric columns.
    A fresh StandardScaler is fitted on the train set and applied to both.

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    sc = StandardScaler()
    X_train = X_train.copy()
    X_test = X_test.copy()

    # Fit on train, transform both (avoids data leakage)
    X_train[SCALE_COLS] = sc.fit_transform(X_train[SCALE_COLS])
    X_test[SCALE_COLS] = sc.transform(X_test[SCALE_COLS])

    return X_train, X_test, y_train, y_test


# ── baseline SVM ──────────────────────────────────────────────────────────

def train_svm(
    X_train: pd.DataFrame, y_train: pd.Series, label: str = ""
) -> SVC:
    """Fit a default SVC and return it."""
    svc = SVC()
    svc.fit(X_train, y_train)
    if label:
        print(f"  SVM trained ({label})")
    return svc


# ── GridSearchCV tuning ───────────────────────────────────────────────────

def tune_svm(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    label: str = "",
    cv: int = 2,
    verbose: int = 1,
) -> GridSearchCV:
    """
    Run GridSearchCV over PARAM_GRID and return the fitted grid object.
    Access the best model via grid.best_estimator_.
    """
    grid = GridSearchCV(SVC(), PARAM_GRID, refit=True, verbose=verbose, cv=cv)
    print(f"\n  Running GridSearchCV ({label}) …")
    grid.fit(X_train, y_train)
    print(f"  Best params ({label}): {grid.best_params_}")
    return grid
