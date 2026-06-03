# train.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

def build_and_train_pipeline(data_path="AmesHousing.csv"):
    print("📦 Loading dataset...")
    data = pd.read_csv(data_path)

    # Separate feature matrix and target matrix
    X = data.drop(columns=['SalePrice'])
    y = data['SalePrice']

    # 1. Pipeline Feature Selection (Future-proofed for modern Pandas versions)
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'str']).columns

    # 2. Pipeline Transformers Definitions
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # 3. Combine Preprocessing Pipelines
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

    print("⚙️ Processing features and splitting data...")
    X_preprocessed = preprocessor.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed, y, test_size=0.2, random_state=42
    )

    # 4. Model Optimization & Training
    print("🧠 Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 5. Serialize Artifacts for Production Deployment
    print("💾 Exporting pipeline artifacts...")
    joblib.dump(preprocessor, 'preprocessor.pkl')
    joblib.dump(model, 'house_price_model.pkl')
    print("✅ Training complete! Model and preprocessor saved.")

if __name__ == "__main__":
    build_and_train_pipeline()