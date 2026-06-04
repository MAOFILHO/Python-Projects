# 🎯 Titanic Survival Prediction — Supervised Learning

K21 Academy | Machine Learning Hands-On Series  
**Three models. One dataset. Full pipeline.**

---

## What this project does

Predicts Titanic passenger survival (binary classification: 0 / 1) using:

| Model | Key idea |
|---|---|
| Logistic Regression | Sigmoid decision boundary — fast, interpretable baseline |
| Random Forest (200 trees) | Ensemble majority vote — best accuracy on this dataset |
| Keras Neural Network | 64 → 32 → 1 Dense layers with Dropout — scales to larger data |

All three models are evaluated with accuracy, classification report, confusion matrix, and ROC / AUC curves.

---

## Requirements

- **Python 3.11** (see `.python-version`)
- macOS, Linux, or Windows (VS Code terminal)

---

## Quick start

```bash
# 1. Clone / unzip the project
cd titanic_survival

# 2. Create a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

No dataset download required — the Titanic data is built into `seaborn`.

---

## Output files

All plots are saved to `outputs/`:

| File | Contents |
|---|---|
| `eda_titanic.png` | 4-panel EDA — counts, sex, class, age distribution |
| `lr_results.png` | Logistic Regression confusion matrix + feature coefficients |
| `rf_results.png` | Random Forest confusion matrix + Gini feature importance |
| `dl_results.png` | Neural Network loss/accuracy curves + confusion matrix |
| `model_comparison.png` | ROC curves + accuracy bar chart for all three models |

---

## Project structure

```
titanic_survival/
├── main.py              # Orchestrator — runs the full pipeline
├── src/
│   ├── data.py          # Load + preprocess Titanic data
│   ├── models.py        # Train LR, RF, Keras NN
│   └── evaluate.py      # Metrics, plots, final comparison
├── outputs/             # Generated figures (git-ignored)
├── requirements.txt
├── .python-version
├── README.md
└── .gitignore
```

---

## Key concepts demonstrated

- Supervised Learning / Binary Classification  
- Feature engineering (sex encoding, median imputation)  
- Train / Test split (80 / 20, stratified)  
- StandardScaler (fit on train only)  
- Logistic Regression — sigmoid boundary  
- Random Forest — 200 decision trees, Gini importance  
- Keras Dense layers — ReLU, Sigmoid, Dropout, BatchNorm  
- EarlyStopping callback  
- Confusion Matrix, Precision / Recall / F1  
- ROC curve + AUC comparison  

---

*K21 Academy — Machine Learning Hands-On Series*
