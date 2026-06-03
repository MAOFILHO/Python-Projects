"""
preprocess.py
-------------
Loads the Bank Churn dataset, applies encoding, feature engineering,
and returns feature matrix X and target vector y.
"""

import pandas as pd
import numpy as np


def load_and_preprocess(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    """
    Load the CSV, encode categorical columns, engineer features,
    and return (X, y).

    Parameters
    ----------
    csv_path : str
        Path to Bank_Churn_Modelling.csv

    Returns
    -------
    X : pd.DataFrame  – feature matrix (CustomerId set as index, Surname / Churn dropped)
    y : pd.Series     – binary churn target
    """
    df = pd.read_csv(csv_path)

    # ── index ──────────────────────────────────────────────────────────────
    df = df.set_index("CustomerId")

    # ── Geography encoding  (France=2, Germany=1, Spain=0) ─────────────────
    df = df.replace({"Geography": {"France": 2, "Germany": 1, "Spain": 0}})

    # ── Gender encoding  (Male=0, Female=1) ────────────────────────────────
    df = df.replace({"Gender": {"Male": 0, "Female": 1}})

    # ── Num Of Products  binarise  (1→0, 2/3/4→1) ──────────────────────────
    df.replace({"Num Of Products": {1: 0, 2: 1, 3: 1, 4: 1}}, inplace=True)

    # ── Zero Balance feature ───────────────────────────────────────────────
    df["Zero Balance"] = np.where(df["Balance"] > 0, 1, 0)

    # ── Split X / y ────────────────────────────────────────────────────────
    X = df.drop(["Surname", "Churn"], axis=1)
    y = df["Churn"]

    return X, y
