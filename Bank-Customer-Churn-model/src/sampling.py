"""
sampling.py
-----------
Produces balanced datasets using Random Under-Sampling and
Random Over-Sampling (imbalanced-learn).
"""

import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler

RANDOM_STATE = 2529


def apply_undersampling(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    """Return (X_rus, y_rus) after random under-sampling the majority class."""
    rus = RandomUnderSampler(random_state=RANDOM_STATE)
    X_rus, y_rus = rus.fit_resample(X, y)
    return X_rus, y_rus


def apply_oversampling(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.Series]:
    """Return (X_ros, y_ros) after random over-sampling the minority class."""
    ros = RandomOverSampler(random_state=RANDOM_STATE)
    X_ros, y_ros = ros.fit_resample(X, y)
    return X_ros, y_ros
