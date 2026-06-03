# Bitcoin Price Prediction

Machine learning pipeline that predicts whether Bitcoin's price will go **up or down** the next day, trained on OHLC data from 2014 to 2022.

## Models
| Model | Notes |
|---|---|
| Logistic Regression | Balanced; best generalisation |
| SVM (poly kernel) | Moderate overfitting |
| XGBoost | Highest train AUC; prone to overfit |

**Evaluation metric:** ROC-AUC (soft probabilities)

---

## Project Structure

```
bitcoin_price_prediction/
├── data/
│   └── bitcoin.csv          # Raw OHLC dataset
├── outputs/                 # Generated charts + model_results.csv
├── main.py                  # Full pipeline (EDA → FE → train → evaluate)
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Python version
Python **3.10+** required.

### 2. Create & activate a virtual environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the pipeline
```bash
python main.py
```

All plots and the model results CSV are written to `./outputs/`.

---

## Outputs

| File | Description |
|---|---|
| `01_close_price.png` | Bitcoin close price over time |
| `02_distributions.png` | OHLC distribution histograms |
| `03_boxplots.png` | OHLC boxplots |
| `04_yearly_averages.png` | Yearly mean OHLC bar charts |
| `05_target_distribution.png` | Up/Down class balance pie chart |
| `06_correlation_heatmap.png` | High-correlation feature heatmap |
| `07_confusion_matrix.png` | Confusion matrix (Logistic Regression) |
| `model_results.csv` | Train & val ROC-AUC for all 3 models |

---

## Feature Engineering

| Feature | Description |
|---|---|
| `open-close` | Open − Close (daily momentum) |
| `low-high` | Low − High (daily range, always ≤ 0) |
| `is_quarter_end` | 1 if month ∈ {3, 6, 9, 12} |
| `target` | 1 if next-day Close > today's Close |

---

## Notes
- Train/validation split is **chronological** (70 % / 30 %) to avoid data leakage.
- `Adj Close` is dropped because it is identical to `Close` in this dataset.
- Model accuracy is close to 50 % — consistent with the efficient-market hypothesis for short-horizon crypto prediction with minimal features.
