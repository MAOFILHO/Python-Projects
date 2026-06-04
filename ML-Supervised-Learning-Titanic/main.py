"""
main.py — Titanic Survival Prediction
Supervised Learning: Logistic Regression | Random Forest | Keras Neural Network

K21 Academy — Machine Learning Hands-On Series
"""

import os
import sys
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

# Ensure src/ is importable when running from the project root
sys.path.insert(0, os.path.dirname(__file__))

from src.data import load_and_preprocess, FEATURES
from src.models import (
    train_logistic_regression,
    train_random_forest,
    train_neural_network,
)
from src.evaluate import (
    plot_eda,
    evaluate_logistic_regression,
    evaluate_random_forest,
    evaluate_neural_network,
    plot_model_comparison,
)


def main():
    print("=" * 60)
    print(" 🎯  Titanic Survival Prediction — Supervised Learning")
    print("=" * 60)

    # ── 1. EDA ────────────────────────────────────────────────────
    print("\n📊 Section 1 — Exploratory Data Analysis")
    plot_eda()

    # ── 2. Data Preprocessing ────────────────────────────────────
    print("\n🛠️  Section 2 — Data Loading & Preprocessing")
    (X_train, X_test, y_train, y_test,
     X_train_scaled, X_test_scaled, _scaler) = load_and_preprocess()

    # ── 3. Model 1: Logistic Regression ──────────────────────────
    print("\n🤖 Section 3 — Logistic Regression")
    lr_model = train_logistic_regression(X_train_scaled, y_train)
    lr_acc, lr_probs = evaluate_logistic_regression(
        lr_model, X_test_scaled, y_test, FEATURES
    )

    # ── 4. Model 2: Random Forest ─────────────────────────────────
    print("\n🌲 Section 4 — Random Forest")
    rf_model = train_random_forest(X_train, y_train)
    rf_acc, rf_probs = evaluate_random_forest(
        rf_model, X_test, y_test, FEATURES
    )

    # ── 5. Model 3: Neural Network ────────────────────────────────
    print("\n🧠 Section 5 — Neural Network (Keras)")
    nn_model, nn_history = train_neural_network(X_train_scaled, y_train)
    dl_acc, dl_probs = evaluate_neural_network(
        nn_model, nn_history, X_test_scaled, y_test
    )

    # ── 6. Final Comparison ───────────────────────────────────────
    print("\n📊 Section 6 — Model Comparison")
    results = {
        'Logistic Regression': (lr_acc, lr_probs),
        'Random Forest':       (rf_acc, rf_probs),
        'Neural Network':      (dl_acc, dl_probs),
    }
    plot_model_comparison(y_test, results)

    print("\n✅ All done! Plots saved to the outputs/ folder.")


if __name__ == '__main__':
    main()
