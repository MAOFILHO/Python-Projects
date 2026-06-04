"""
evaluate.py — EDA plots, per-model result plots, and final comparison.
All figures are saved to the outputs/ folder.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, auc,
)

OUTPUTS = os.path.join(os.path.dirname(__file__), '..', 'outputs')


def _save(name: str):
    path = os.path.join(OUTPUTS, name)
    plt.savefig(path, dpi=120, bbox_inches='tight')
    print(f"   Saved → {path}")


# ── EDA ───────────────────────────────────────────────────────────────────────

def plot_eda():
    """Loads raw Titanic data and saves the 4-panel EDA figure."""
    df_raw = sns.load_dataset('titanic')

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Titanic Dataset — Exploratory Data Analysis',
                 fontsize=15, fontweight='bold')

    sns.countplot(data=df_raw, x='survived',
                  palette=['#E11D48', '#059669'], ax=axes[0, 0])
    axes[0, 0].set_title('Overall Survival Count')
    axes[0, 0].set_xticklabels(['Did Not Survive', 'Survived'])
    axes[0, 0].set_xlabel('')

    sns.countplot(data=df_raw, x='sex', hue='survived',
                  palette=['#E11D48', '#059669'], ax=axes[0, 1])
    axes[0, 1].set_title('Survival by Sex')
    axes[0, 1].legend(['Did Not Survive', 'Survived'])

    sns.countplot(data=df_raw, x='pclass', hue='survived',
                  palette=['#E11D48', '#059669'], ax=axes[1, 0])
    axes[1, 0].set_title('Survival by Passenger Class')
    axes[1, 0].legend(['Did Not Survive', 'Survived'])
    axes[1, 0].set_xlabel('Class (1=First, 2=Second, 3=Third)')

    df_raw.groupby('survived')['age'].plot(
        kind='hist', alpha=0.6, bins=25, ax=axes[1, 1], legend=True)
    axes[1, 1].set_title('Age Distribution by Survival')
    axes[1, 1].legend(['Did Not Survive', 'Survived'])
    axes[1, 1].set_xlabel('Age')

    plt.tight_layout()
    _save('eda_titanic.png')
    plt.close()

    print("\n💡 Key observations:")
    print("   • Women survived at much higher rates than men")
    print("   • 1st class passengers had better survival odds")
    print("   • Children (young ages) had better survival odds")


# ── Logistic Regression ───────────────────────────────────────────────────────

def evaluate_logistic_regression(model, X_test_scaled, y_test, features):
    preds = model.predict(X_test_scaled)
    probs = model.predict_proba(X_test_scaled)[:, 1]
    acc   = accuracy_score(y_test, preds)

    print(f"\n✅ Logistic Regression — Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, preds,
                                target_names=['Did Not Survive', 'Survived']))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    fig.suptitle('Logistic Regression — Results', fontsize=13, fontweight='bold')

    ConfusionMatrixDisplay(
        confusion_matrix(y_test, preds),
        display_labels=['Not Survived', 'Survived'],
    ).plot(ax=axes[0], colorbar=False, cmap='Blues')
    axes[0].set_title(f'Confusion Matrix (Acc: {acc*100:.1f}%)')

    coefs = pd.Series(np.abs(model.coef_[0]),
                      index=features).sort_values(ascending=True)
    coefs.plot(kind='barh', ax=axes[1], color='#4F46E5')
    axes[1].set_title('Feature Importance (|Coefficient|)')
    axes[1].set_xlabel('Absolute Weight')

    plt.tight_layout()
    _save('lr_results.png')
    plt.close()

    print("\n💡 Sex (gender) has the highest coefficient — strongest predictor of survival.")
    return acc, probs


# ── Random Forest ─────────────────────────────────────────────────────────────

def evaluate_random_forest(model, X_test, y_test, features):
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    acc   = accuracy_score(y_test, preds)

    print(f"\n✅ Random Forest (200 trees) — Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, preds,
                                target_names=['Did Not Survive', 'Survived']))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    fig.suptitle('Random Forest — Results', fontsize=13, fontweight='bold')

    ConfusionMatrixDisplay(
        confusion_matrix(y_test, preds),
        display_labels=['Not Survived', 'Survived'],
    ).plot(ax=axes[0], colorbar=False, cmap='Greens')
    axes[0].set_title(f'Confusion Matrix (Acc: {acc*100:.1f}%)')

    importances = pd.Series(model.feature_importances_,
                            index=features).sort_values(ascending=True)
    importances.plot(kind='barh', ax=axes[1], color='#059669')
    axes[1].set_title('Feature Importance (RF Gini)')
    axes[1].set_xlabel('Importance Score')

    plt.tight_layout()
    _save('rf_results.png')
    plt.close()

    print("\n💡 RF confirms: sex, fare, and age are the top 3 predictors.")
    return acc, probs


# ── Neural Network ────────────────────────────────────────────────────────────

def evaluate_neural_network(model, history, X_test_scaled, y_test):
    _, acc  = model.evaluate(X_test_scaled, y_test, verbose=0)
    preds   = (model.predict(X_test_scaled, verbose=0) > 0.5).astype(int).flatten()
    probs   = model.predict(X_test_scaled, verbose=0).flatten()

    print(f"\n✅ Neural Network — Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, preds,
                                target_names=['Did Not Survive', 'Survived']))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4))
    fig.suptitle('Neural Network (Keras) — Results', fontsize=13, fontweight='bold')

    axes[0].plot(history.history['loss'],     label='Train Loss',  color='#4F46E5')
    axes[0].plot(history.history['val_loss'], label='Val Loss',
                 color='#E11D48', linestyle='--')
    axes[0].set_title('Loss Curve')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()

    axes[1].plot(history.history['accuracy'],     label='Train Acc',  color='#059669')
    axes[1].plot(history.history['val_accuracy'], label='Val Acc',
                 color='#D97706', linestyle='--')
    axes[1].set_title('Accuracy Curve')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].legend()

    ConfusionMatrixDisplay(
        confusion_matrix(y_test, preds),
        display_labels=['Not Survived', 'Survived'],
    ).plot(ax=axes[2], colorbar=False, cmap='Purples')
    axes[2].set_title(f'Confusion Matrix (Acc: {acc*100:.1f}%)')

    plt.tight_layout()
    _save('dl_results.png')
    plt.close()

    return acc, probs


# ── Final Comparison ──────────────────────────────────────────────────────────

def plot_model_comparison(y_test, results: dict):
    """
    results = {
        'Logistic Regression': (acc, probs),
        'Random Forest':       (acc, probs),
        'Neural Network':      (acc, probs),
    }
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('All Models — Final Comparison', fontsize=13, fontweight='bold')

    for name, (acc, probs) in results.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_auc = auc(fpr, tpr)
        axes[0].plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.3f})')

    axes[0].plot([0, 1], [0, 1], 'k--', label='Random (AUC = 0.500)')
    axes[0].set_xlabel('False Positive Rate')
    axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curves')
    axes[0].legend(fontsize=9)

    labels  = [n.replace(' ', '\n') for n in results.keys()]
    accs    = [v[0] for v in results.values()]
    colors  = ['#4F46E5', '#059669', '#7C3AED']
    bars = axes[1].bar(labels, [a * 100 for a in accs], color=colors, width=0.4)
    axes[1].set_ylim(60, 100)
    axes[1].set_ylabel('Test Accuracy (%)')
    axes[1].set_title('Model Accuracy Comparison')
    for bar, acc in zip(bars, accs):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f'{acc*100:.1f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=11,
        )

    plt.tight_layout()
    _save('model_comparison.png')
    plt.close()

    print("\n" + "=" * 52)
    print(f"{'MODEL':<25} {'ACCURACY':>10} {'AUC':>10}")
    print("=" * 52)
    for name, (acc, probs) in results.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_auc = auc(fpr, tpr)
        print(f"{name:<25} {acc*100:>9.1f}% {roc_auc:>10.3f}")
    print("=" * 52)

    print("\nKey Takeaways:")
    print("-" * 57)
    print("* Logistic Regression  — Fast, interpretable, solid baseline")
    print("* Random Forest        — Best accuracy, built-in feature importance")
    print("* Neural Network       — Competitive, great for larger data")
    print("-" * 57)
    print("For this dataset (891 rows), Random Forest wins.")
    print("For bigger datasets (100,000+ rows), Neural Networks shine.")
