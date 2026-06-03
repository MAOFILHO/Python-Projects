# Bank Customer Churn Model

SVM-based binary classifier that predicts whether a bank customer will churn.
Demonstrates **class-imbalance handling** (Random Under/Over-Sampling) and
**hyperparameter tuning** via `GridSearchCV`.

---

## Project structure

```
bank-churn-model/
├── data/
│   └── Bank_Churn_Modelling.csv   # raw dataset
├── outputs/                        # plots generated at runtime (git-ignored)
├── src/
│   ├── __init__.py
│   ├── preprocess.py               # load, encode, feature-engineer
│   ├── sampling.py                 # RUS / ROS helpers
│   ├── train.py                    # split, scale, SVM, GridSearchCV
│   └── evaluate.py                 # confusion matrix, reports, plots
├── main.py                         # pipeline entry-point
├── requirements.txt
├── .python-version                 # pins Python 3.11
├── .gitignore
└── README.md
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | **3.11** (see `.python-version`) |
| pandas | ≥ 2.0 |
| numpy | ≥ 1.26 |
| scikit-learn | ≥ 1.4 |
| imbalanced-learn | ≥ 0.12 |
| matplotlib | ≥ 3.8 |
| seaborn | ≥ 0.13 |

---

## Quick start (VS Code terminal on Mac)

### 1 — Clone / open the project folder

```bash
cd bank-churn-model
```

### 2 — Create and activate a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

> **Tip:** If you use `pyenv`, the `.python-version` file will auto-select Python 3.11.

### 3 — Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4 — Run the pipeline

```bash
# Full pipeline (includes GridSearchCV – takes ~5–15 min)
python main.py

# Quick smoke-test (skips GridSearchCV)
python main.py --skip-grid

# Custom data path or output directory
# python main.py --data path/to/data.csv --output-dir results/
```

---

## Pipeline steps

| Step | What happens |
|------|--------------|
| **1 – Preprocess** | Load CSV → set `CustomerId` as index → encode `Geography` & `Gender` → binarise `Num Of Products` → engineer `Zero Balance` feature |
| **2 – Sampling** | Apply **Random Under-Sampling** (RUS) and **Random Over-Sampling** (ROS) to balance the 80/20 churn class ratio |
| **3 – Split & Scale** | 70/30 train/test split for each of the three dataset variants; `StandardScaler` fitted on train, applied to test (no leakage) |
| **4 – Baseline SVM** | Default `SVC()` trained and evaluated on Original / RUS / ROS splits |
| **5 – GridSearchCV** | Exhaustive search over `C ∈ {0.1, 1, 10}`, `gamma ∈ {1, 0.1, 0.01}`, `kernel=rbf`, `class_weight=balanced` with 2-fold CV |

---

## Outputs

All plots are saved to `outputs/` (git-ignored):

| File | Description |
|------|-------------|
| `churn_distribution.png` | Target class counts before sampling |
| `zero_balance_histogram.png` | Engineered feature distribution |
| `class_distribution.png` | Side-by-side class balance after sampling |
| `confusion_matrix_Baseline_*.png` | Confusion matrices – default SVM |
| `confusion_matrix_GridSearch_*.png` | Confusion matrices – tuned SVM |

---

## Dataset

`Bank_Churn_Modelling.csv` — 10 000 rows, 13 columns.

| Column | Type | Notes |
|--------|------|-------|
| CustomerId | int | Set as DataFrame index |
| Surname | str | Dropped before modelling |
| CreditScore | int | Standardised |
| Geography | str → int | France=2, Germany=1, Spain=0 |
| Gender | str → int | Male=0, Female=1 |
| Age | int | Standardised |
| Tenure | int | Standardised |
| Balance | float | Standardised |
| Num Of Products | int | Binarised: 1→0, 2/3/4→1 |
| Has Credit Card | int | Already binary |
| Is Active Member | int | Already binary |
| Estimated Salary | float | Standardised |
| Churn | int | **Target** (0=stay, 1=churn) |

---

## Notes & improvements

- GridSearchCV uses `cv=2` (matches the notebook). Increase to `cv=5` for more robust estimates at the cost of extra runtime.
- The notebook used `svc.predict` for all three test sets, which is a bug (uses the original model for RUS/ROS test sets). This project correctly calls `svc_rus.predict` and `svc_ros.predict`.
- For production use, consider `joblib.dump` to serialise the best estimator.
