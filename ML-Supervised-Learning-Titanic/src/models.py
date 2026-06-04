"""
models.py — Train all three classifiers used in the notebook.
"""

import os
import warnings
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def train_logistic_regression(X_train_scaled, y_train):
    """Trains and returns a fitted LogisticRegression model."""
    print("\n── Training Logistic Regression ──")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    print("   Done.")
    return lr


def train_random_forest(X_train, y_train):
    """Trains and returns a fitted RandomForestClassifier (200 trees)."""
    print("\n── Training Random Forest (200 trees) ──")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
    )
    rf.fit(X_train, y_train)
    print("   Done.")
    return rf


def build_keras_model(input_dim: int):
    """Builds and compiles the 3-layer Keras neural network."""
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    tf.random.set_seed(42)

    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid'),
    ], name='titanic_survival_nn')

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy'],
    )
    return model


def train_neural_network(X_train_scaled, y_train):
    """Builds, trains and returns the fitted Keras model + training history."""
    from tensorflow import keras

    print("\n── Training Neural Network (Keras) ──")
    model = build_keras_model(X_train_scaled.shape[1])
    model.summary()

    early_stop = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
    )

    history = model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.15,
        callbacks=[early_stop],
        verbose=0,
    )

    epochs_run = len(history.history['loss'])
    best_val_acc = max(history.history['val_accuracy'])
    print(f"   Stopped at epoch {epochs_run}  |  Best val_accuracy: {best_val_acc:.4f}")
    return model, history
