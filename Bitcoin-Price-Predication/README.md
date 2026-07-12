# Bitcoin Price Prediction

Bitcoin price prediction has garnered significant attention due to its volatile nature and the potential for lucrative trading opportunities. With the rise of **Machine Learning (ML)**, predicting market trends has become increasingly feasible. This project explores how ML can be utilized to predict Bitcoin's price movement, specifically whether a trade will result in a profitable outcome. By leveraging various ML models, such as **Logistic Regression**, **Support Vector Machines (SVM)**, and **XGBoost**, we aim to analyze Bitcoin price data to forecast future trends.

We begin by loading and exploring Bitcoin price data, focusing on OHLC (Open, High, Low, Close) values from 2014 to 2022. Next, we perform feature engineering, introducing variables such as \"open-close\" and \"low-high\" to better understand market behaviour. With preprocessed data, we train multiple ML models to predict the market's direction. The model's performance is evaluated using metrics like ROC-AUC, offering insights into the effectiveness of different algorithms in predicting Bitcoin price movements.

## Models
| Model | Notes |
|---|---|
| Logistic Regression | Balanced; best generalisation |
| SVM (poly kernel) | Moderate overfitting |
| XGBoost | Highest train AUC; prone to overfit |

**Evaluation metric:** ROC-AUC (soft probabilities)



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



## Feature Engineering

| Feature | Description |
|---|---|
| `open-close` | Open − Close (daily momentum) |
| `low-high` | Low − High (daily range, always ≤ 0) |
| `is_quarter_end` | 1 if month ∈ {3, 6, 9, 12} |
| `target` | 1 if next-day Close > today's Close |



## Notes
- Train/validation split is **chronological** (70 % / 30 %) to avoid data leakage.
- `Adj Close` is dropped because it is identical to `Close` in this dataset.
- Model accuracy is close to 50 % — consistent with the efficient-market hypothesis for short-horizon crypto prediction with minimal features.



## Screenshots

<img width="1306" height="948" alt="Screenshot 2026-06-03 at 3 21 50 PM" src="https://github.com/user-attachments/assets/24a9ab13-dedf-4dee-88a6-3e2cdc29fdca" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="886" height="886" alt="Screenshot 2026-06-03 at 3 26 14 PM" src="https://github.com/user-attachments/assets/e8be3105-2501-4df7-a4c5-18ee989733ee" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="865" height="806" alt="Screenshot 2026-06-03 at 3 26 27 PM" src="https://github.com/user-attachments/assets/2ada0eb9-ab62-45d6-bfe6-0ef9b9ca50d2" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="1082" height="385" alt="Screenshot 2026-06-03 at 3 26 58 PM" src="https://github.com/user-attachments/assets/3b76bc2a-c8e7-484c-8481-33ea70b89170" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="1086" height="555" alt="Screenshot 2026-06-03 at 3 27 08 PM" src="https://github.com/user-attachments/assets/ca773e26-cadd-4798-9b74-0abbe16ba233" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="1086" height="554" alt="Screenshot 2026-06-03 at 3 27 25 PM" src="https://github.com/user-attachments/assets/629a7098-909f-4633-a6ee-701a42e448c5" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="677" height="558" alt="Screenshot 2026-06-03 at 3 27 45 PM" src="https://github.com/user-attachments/assets/033c637f-74ac-4a8c-9557-de9069f69c9f" />

<img width="100%" height="1" alt="" src="https://github.com/user-attachments/assets/f2af28ee-a373-4488-89e5-2b84d5da9620" />
<br><br>
<img width="1205" height="477" alt="Screenshot 2026-06-03 at 3 27 50 PM" src="https://github.com/user-attachments/assets/787f1011-7925-45a7-a92d-b78ebe0d78a8" />

## Author

**Marcos Oliveira** — [LinkedIn](https://www.linkedin.com/in/mfilho1/) | [GitHub](https://github.com/MAOFILHO)
