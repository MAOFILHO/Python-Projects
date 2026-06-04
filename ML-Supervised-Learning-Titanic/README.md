# 🎯 Titanic Survival Prediction — Supervised Learning

Machine Learning Hands-On Series  
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

## Screenshots

<img width="1275" height="783" alt="Screenshot 2026-06-03 at 8 26 02 PM" src="https://github.com/user-attachments/assets/566f83fa-77e1-47ba-8d71-e0edc1448d5a" />

<img width="1028" height="717" alt="Screenshot 2026-06-03 at 8 28 44 PM" src="https://github.com/user-attachments/assets/a8cd7569-3c73-49c8-9745-123603a0fcd7" />

<img width="980" height="703" alt="Screenshot 2026-06-03 at 8 29 29 PM" src="https://github.com/user-attachments/assets/2cad8cbf-bcdc-4de0-9ee0-2f623f8ed08b" />

<img width="1357" height="774" alt="Screenshot 2026-06-03 at 8 29 54 PM" src="https://github.com/user-attachments/assets/2a910056-58ab-409c-a746-0f86b230c24f" />

<img width="1084" height="310" alt="Screenshot 2026-06-03 at 8 30 30 PM" src="https://github.com/user-attachments/assets/68030bfc-15af-408c-8058-6f51a95e69c0" />

<img width="572" height="378" alt="Screenshot 2026-06-03 at 8 30 43 PM" src="https://github.com/user-attachments/assets/01e363d6-230e-4967-9054-10ac473e46a9" />

<img width="1035" height="382" alt="Screenshot 2026-06-03 at 8 31 03 PM" src="https://github.com/user-attachments/assets/93ffba4e-359f-4903-bc32-1573ea7c33e3" />

<img width="1084" height="373" alt="Screenshot 2026-06-03 at 8 31 14 PM" src="https://github.com/user-attachments/assets/643b87f1-b9b9-44b1-be54-75073e17782c" />
