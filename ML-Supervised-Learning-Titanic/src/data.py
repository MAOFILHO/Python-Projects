"""
data.py — Load and preprocess the Titanic dataset (built into seaborn).
"""

import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURES = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare']
TARGET   = 'survived'


def load_and_preprocess():
    """
    Loads the seaborn Titanic dataset, cleans it, splits into train/test,
    and returns scaled arrays plus the fitted scaler.

    Returns
    -------
    X_train, X_test, y_train, y_test : np.ndarray
    X_train_scaled, X_test_scaled    : np.ndarray  (StandardScaler applied)
    scaler                           : fitted StandardScaler
    """
    df_raw = sns.load_dataset('titanic')

    print(f"Dataset loaded: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    print(f"\nSurvival breakdown:")
    print(df_raw[TARGET].value_counts().rename({0: 'Did NOT survive', 1: 'Survived'}))

    # Select columns
    df = df_raw[FEATURES + [TARGET]].copy()

    # Fill missing values
    df['age']  = df['age'].fillna(df['age'].median())
    df['fare'] = df['fare'].fillna(df['fare'].median())

    # Encode sex: male=1, female=0
    df['sex'] = df['sex'].map({'male': 1, 'female': 0})

    # Drop any remaining NaN rows
    df = df.dropna()

    print(f"\nMissing values after cleaning : {df.isnull().sum().sum()}")
    print(f"Dataset shape after cleaning  : {df.shape}")

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    print(f"\nTraining set : {X_train.shape[0]} samples")
    print(f"Test set     : {X_test.shape[0]} samples")

    return X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled, scaler
