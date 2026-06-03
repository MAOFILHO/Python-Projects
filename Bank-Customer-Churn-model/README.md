# Bank Customer Churn Model

In this project, we focus on solving a common problem in machine learning: class imbalance. Class imbalance occurs when the number of instances of one class significantly outweighs the other, leading to biased models that perform poorly on the minority class. The goal of this module is to apply various sampling techniques—oversampling and undersampling—and optimize a Support Vector Machine (SVM) model using GridSearchCV to enhance model performance.

To start, the dataset is split into training and testing sets, and we apply different sampling methods to balance the class distribution. Next, we standardize the data to ensure that features are on the same scale, allowing the SVM model to perform optimally. We then evaluate the model's performance by analyzing confusion matrices and classification reports to assess metrics like precision, recall, and F1-score.

Finally, hyperparameter tuning is performed using GridSearchCV to fine-tune the SVM model and find the best set of hyperparameters. This process ensures that the model is well-optimized for better predictive performance, especially on the minority class. The overall objective is to demonstrate how effective sampling techniques and hyperparameter tuning can improve the accuracy and generalization of classification models in imbalanced datasets.

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

---

## Screenshots

<img width="1302" height="949" alt="Screenshot 2026-06-03 at 2 05 22 PM" src="https://github.com/user-attachments/assets/ec9ee76b-e621-4d89-85a1-962391cd294c" />

<img width="1283" height="953" alt="Screenshot 2026-06-03 at 2 11 14 PM" src="https://github.com/user-attachments/assets/d5002b61-1e27-449f-8cb1-57c4ab52cfd3" />

<img width="753" height="553" alt="Screenshot 2026-06-03 at 2 12 36 PM" src="https://github.com/user-attachments/assets/5b52ac2c-aff9-4f6b-a296-ec0417f7199a" />

<img width="1081" height="381" alt="Screenshot 2026-06-03 at 2 12 47 PM" src="https://github.com/user-attachments/assets/eaf851d5-4fa8-4c0d-8c16-1c0788360d4a" />

<img width="712" height="556" alt="Screenshot 2026-06-03 at 2 13 02 PM" src="https://github.com/user-attachments/assets/49a9da06-ec04-48ea-9adf-93f2ea940d18" />

<img width="712" height="559" alt="Screenshot 2026-06-03 at 2 13 20 PM" src="https://github.com/user-attachments/assets/4e3ff90f-ac9f-440a-9172-ff9eda776b53" />

<img width="708" height="557" alt="Screenshot 2026-06-03 at 2 13 32 PM" src="https://github.com/user-attachments/assets/a5621329-cddb-4061-a735-acc7dd31d7b5" />
