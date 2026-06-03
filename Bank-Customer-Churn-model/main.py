"""
main.py
-------
Bank Customer Churn Model – full pipeline runner.

Steps
-----
1. Load & preprocess data
2. Apply Random Under-Sampling (RUS) and Random Over-Sampling (ROS)
3. Train/test split + standardisation for each dataset variant
4. Baseline SVM evaluation (Original / RUS / ROS)
5. GridSearchCV hyperparameter tuning (Original / RUS / ROS)
6. Save evaluation plots to outputs/

Usage
-----
    python main.py [--data PATH] [--output-dir DIR] [--skip-grid]

Defaults
--------
    --data        data/Bank_Churn_Modelling.csv
    --output-dir  outputs/
"""

import argparse
import os
import sys

import pandas as pd

from src.preprocess import load_and_preprocess
from src.sampling import apply_undersampling, apply_oversampling
from src.train import split_and_scale, train_svm, tune_svm
from src.evaluate import (
    print_report,
    plot_confusion_matrix,
    plot_class_distribution,
    plot_zero_balance,
    plot_churn_distribution,
)


# ── CLI ───────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bank Customer Churn – SVM pipeline")
    p.add_argument(
        "--data",
        default=os.path.join("data", "Bank_Churn_Modelling.csv"),
        help="Path to the CSV dataset (default: data/Bank_Churn_Modelling.csv)",
    )
    p.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for saved plots (default: outputs/)",
    )
    p.add_argument(
        "--skip-grid",
        action="store_true",
        help="Skip GridSearchCV (much faster; useful for a quick smoke-test)",
    )
    return p.parse_args()


# ── pipeline ──────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # ── 1. Load & preprocess ───────────────────────────────────────────────
    print("\n═══════════════════════════════════════")
    print("  STEP 1 – Load & Preprocess")
    print("═══════════════════════════════════════")
    X, y = load_and_preprocess(args.data)
    print(f"  Dataset shape : X={X.shape}  y={y.shape}")
    print(f"  Churn counts  :\n{y.value_counts().to_string()}")

    plot_churn_distribution(y, args.output_dir)
    plot_zero_balance(X["Zero Balance"], args.output_dir)

    # ── 2. Sampling ────────────────────────────────────────────────────────
    print("\n═══════════════════════════════════════")
    print("  STEP 2 – Sampling")
    print("═══════════════════════════════════════")
    X_rus, y_rus = apply_undersampling(X, y)
    print(f"  After RUS : X={X_rus.shape}  y={y_rus.shape}")
    print(f"  Churn counts (RUS):\n{y_rus.value_counts().to_string()}")

    X_ros, y_ros = apply_oversampling(X, y)
    print(f"  After ROS : X={X_ros.shape}  y={y_ros.shape}")
    print(f"  Churn counts (ROS):\n{y_ros.value_counts().to_string()}")

    plot_class_distribution(
        {"Original": y, "Under-sampled": y_rus, "Over-sampled": y_ros},
        args.output_dir,
    )

    # ── 3. Train / test split + scaling ───────────────────────────────────
    print("\n═══════════════════════════════════════")
    print("  STEP 3 – Train / Test Split & Scaling")
    print("═══════════════════════════════════════")
    X_train,     X_test,     y_train,     y_test     = split_and_scale(X,     y)
    X_train_rus, X_test_rus, y_train_rus, y_test_rus = split_and_scale(X_rus, y_rus)
    X_train_ros, X_test_ros, y_train_ros, y_test_ros = split_and_scale(X_ros, y_ros)
    print(f"  Original  → train: {X_train.shape}  test: {X_test.shape}")
    print(f"  RUS       → train: {X_train_rus.shape}  test: {X_test_rus.shape}")
    print(f"  ROS       → train: {X_train_ros.shape}  test: {X_test_ros.shape}")

    # ── 4. Baseline SVM ───────────────────────────────────────────────────
    print("\n═══════════════════════════════════════")
    print("  STEP 4 – Baseline SVM (default params)")
    print("═══════════════════════════════════════")
    svc     = train_svm(X_train,     y_train,     "Original")
    svc_rus = train_svm(X_train_rus, y_train_rus, "RUS")
    svc_ros = train_svm(X_train_ros, y_train_ros, "ROS")

    y_pred     = svc.predict(X_test)
    y_pred_rus = svc_rus.predict(X_test_rus)
    y_pred_ros = svc_ros.predict(X_test_ros)

    print_report(y_test,     y_pred,     "Baseline – Original")
    print_report(y_test_rus, y_pred_rus, "Baseline – RUS")
    print_report(y_test_ros, y_pred_ros, "Baseline – ROS")

    plot_confusion_matrix(y_test,     y_pred,     "Baseline_Original", args.output_dir)
    plot_confusion_matrix(y_test_rus, y_pred_rus, "Baseline_RUS",      args.output_dir)
    plot_confusion_matrix(y_test_ros, y_pred_ros, "Baseline_ROS",      args.output_dir)

    # ── 5. GridSearchCV ───────────────────────────────────────────────────
    if args.skip_grid:
        print("\n  GridSearchCV skipped (--skip-grid flag set).")
        return

    print("\n═══════════════════════════════════════")
    print("  STEP 5 – GridSearchCV Hyperparameter Tuning")
    print("  (this may take several minutes)")
    print("═══════════════════════════════════════")
    grid     = tune_svm(X_train,     y_train,     "Original")
    grid_rus = tune_svm(X_train_rus, y_train_rus, "RUS")
    grid_ros = tune_svm(X_train_ros, y_train_ros, "ROS")

    print(f"\n  Best estimator (Original) : {grid.best_estimator_}")
    print(f"  Best estimator (RUS)      : {grid_rus.best_estimator_}")
    print(f"  Best estimator (ROS)      : {grid_ros.best_estimator_}")

    grid_pred     = grid.predict(X_test)
    grid_pred_rus = grid_rus.predict(X_test_rus)
    grid_pred_ros = grid_ros.predict(X_test_ros)

    print_report(y_test,     grid_pred,     "GridSearch – Original")
    print_report(y_test_rus, grid_pred_rus, "GridSearch – RUS")
    print_report(y_test_ros, grid_pred_ros, "GridSearch – ROS")

    plot_confusion_matrix(y_test,     grid_pred,     "GridSearch_Original", args.output_dir)
    plot_confusion_matrix(y_test_rus, grid_pred_rus, "GridSearch_RUS",      args.output_dir)
    plot_confusion_matrix(y_test_ros, grid_pred_ros, "GridSearch_ROS",      args.output_dir)

    print("\n  ✓ Pipeline complete. Plots saved to:", args.output_dir)


if __name__ == "__main__":
    main()
