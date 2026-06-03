"""
evaluate.py
-----------
Evaluation utilities: confusion matrix visualisation, classification
reports, and class-distribution plots.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report


# ── metrics ───────────────────────────────────────────────────────────────

def print_report(y_true: pd.Series, y_pred: np.ndarray, label: str = "") -> None:
    """Print confusion matrix + classification report to stdout."""
    title = f"── {label} " if label else "── "
    print(f"\n{title}{'─' * (60 - len(title))}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, zero_division=1))


# ── plots ─────────────────────────────────────────────────────────────────

def plot_confusion_matrix(
    y_true: pd.Series,
    y_pred: np.ndarray,
    label: str = "",
    output_dir: str = "outputs",
) -> None:
    """Save a heatmap of the confusion matrix as a PNG."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["No Churn", "Churn"],
        yticklabels=["No Churn", "Churn"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix – {label}")
    fig.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.join(output_dir, f"confusion_matrix_{label.replace(' ', '_')}.png")
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved → {fname}")


def plot_class_distribution(
    y_dict: dict[str, pd.Series],
    output_dir: str = "outputs",
) -> None:
    """
    Plot class distribution for multiple datasets side-by-side.

    Parameters
    ----------
    y_dict : {"Original": y, "Under-sampled": y_rus, "Over-sampled": y_ros}
    """
    fig, axes = plt.subplots(1, len(y_dict), figsize=(5 * len(y_dict), 4))
    if len(y_dict) == 1:
        axes = [axes]

    for ax, (name, y) in zip(axes, y_dict.items()):
        counts = y.value_counts().sort_index()
        ax.bar(["No Churn (0)", "Churn (1)"], counts.values, color=["steelblue", "tomato"])
        ax.set_title(name)
        ax.set_ylabel("Count")
        for i, v in enumerate(counts.values):
            ax.text(i, v + counts.values.max() * 0.01, str(v), ha="center", fontsize=10)

    fig.suptitle("Class Distribution After Sampling", fontsize=13)
    fig.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.join(output_dir, "class_distribution.png")
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved → {fname}")


def plot_zero_balance(
    zero_balance_col: pd.Series,
    output_dir: str = "outputs",
) -> None:
    """Save histogram for the engineered Zero Balance feature."""
    fig, ax = plt.subplots(figsize=(5, 4))
    zero_balance_col.hist(ax=ax, bins=3, color="steelblue", edgecolor="white")
    ax.set_title("Zero Balance Feature Distribution")
    ax.set_xlabel("Value (0 = zero balance, 1 = positive balance)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.join(output_dir, "zero_balance_histogram.png")
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved → {fname}")


def plot_churn_distribution(
    y: pd.Series,
    output_dir: str = "outputs",
) -> None:
    """Save a count-plot of the target Churn column."""
    fig, ax = plt.subplots(figsize=(5, 4))
    counts = y.value_counts().sort_index()
    ax.bar(["No Churn (0)", "Churn (1)"], counts.values, color=["steelblue", "tomato"])
    ax.set_title("Churn Distribution (Original Dataset)")
    ax.set_ylabel("Count")
    for i, v in enumerate(counts.values):
        ax.text(i, v + counts.values.max() * 0.01, str(v), ha="center", fontsize=11)
    fig.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    fname = os.path.join(output_dir, "churn_distribution.png")
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved → {fname}")
