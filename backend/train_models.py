import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv("data/breast_cancer_wisconsin.csv")

print(df.head())
print(df.columns)

df = df.drop(columns=["Unnamed: 32"], errors="ignore")
df = df.drop(columns=["id"], errors="ignore")
df["diagnosis"] = df["diagnosis"].map({"M": 1, "B": 0})

COLUMN_RENAME_MAP = {
    "mean radius": "radius_mean",
    "mean texture": "texture_mean",
    "mean perimeter": "perimeter_mean",
    "mean area": "area_mean",
    "mean smoothness": "smoothness_mean",
    "mean compactness": "compactness_mean",
    "mean concavity": "concavity_mean",
    "mean concave points": "concave_points_mean",
    "mean symmetry": "symmetry_mean",
    "mean fractal dimension": "fractal_dimension_mean",

    "radius error": "radius_se",
    "texture error": "texture_se",
    "perimeter error": "perimeter_se",
    "area error": "area_se",
    "smoothness error": "smoothness_se",
    "compactness error": "compactness_se",
    "concavity error": "concavity_se",
    "concave points error": "concave_points_se",
    "symmetry error": "symmetry_se",
    "fractal dimension error": "fractal_dimension_se",

    "worst radius": "radius_worst",
    "worst texture": "texture_worst",
    "worst perimeter": "perimeter_worst",
    "worst area": "area_worst",
    "worst smoothness": "smoothness_worst",
    "worst compactness": "compactness_worst",
    "worst concavity": "concavity_worst",
    "worst concave points": "concave_points_worst",
    "worst symmetry": "symmetry_worst",
    "worst fractal dimension": "fractal_dimension_worst",
}

df = df.rename(columns=COLUMN_RENAME_MAP)

print("\nShape:")
print(df.shape)

print("\nData types:")
print(df.dtypes)

assert df.isnull().sum().sum() == 0, "Dataset contains missing values"
assert df.duplicated().sum() == 0, "Dataset contains duplicate rows"
assert df["diagnosis"].isin([0, 1]).all(), "Diagnosis column has unexpected values"

print("\nSummary statistics:")
print(df.describe())

X = df.drop(columns=["diagnosis"])
y = df["diagnosis"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

logistic_regression_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(max_iter=1000, random_state=42))
])

logistic_regression_pipeline.fit(X_train, y_train)
lg_train_acc = accuracy_score(y_train, logistic_regression_pipeline.predict(X_train))
lg_test_acc = accuracy_score(y_test, logistic_regression_pipeline.predict(X_test))

coef = logistic_regression_pipeline.named_steps["classifier"].coef_[0]

joblib.dump(logistic_regression_pipeline, os.path.join(MODEL_DIR, "logistic_regression.pkl"))
print("Saved: backend/models/logistic_regression.pkl")

random_forest_pipeline = Pipeline([
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10))
])

random_forest_pipeline.fit(X_train, y_train)
rf_train_acc = accuracy_score(y_train, random_forest_pipeline.predict(X_train))
rf_test_acc = accuracy_score(y_test, random_forest_pipeline.predict(X_test))

joblib.dump(random_forest_pipeline, os.path.join(MODEL_DIR, "random_forest.pkl"))
print("Saved: backend/models/random_forest.pkl")

gb_pipeline = Pipeline([
    ("classifier", GradientBoostingClassifier(n_estimators=100, random_state=42))
])

gb_pipeline.fit(X_train, y_train)
gb_train_acc = accuracy_score(y_train, gb_pipeline.predict(X_train))
gb_test_acc = accuracy_score(y_test, gb_pipeline.predict(X_test))

joblib.dump(gb_pipeline, os.path.join(MODEL_DIR, "gradient_boosting.pkl"))
print("Saved: backend/models/gradient_boosting.pkl")

feature_stats = {}
for col in X.columns:
    feature_stats[col] = {
        "min": float(X[col].min()),
        "max": float(X[col].max()),
        "mean": float(X[col].mean()),
        "std": float(X[col].std())
    }

joblib.dump(feature_stats, os.path.join(MODEL_DIR, "feature_stats.pkl"))
print("Saved: backend/models/feature_stats.pkl")

feature_importance_lr = pd.DataFrame({
    "feature": X.columns,
    "coefficient": coef,
    "abs_coefficient": np.abs(coef)
}).sort_values("abs_coefficient", ascending=False)

top_features = feature_importance_lr.head(10)["feature"].tolist()

feature_labels = {
    "radius_mean": "Average Radius",
    "texture_mean": "Average Texture",
    "perimeter_mean": "Average Perimeter",
    "area_mean": "Average Area",
    "smoothness_mean": "Average Smoothness",
    "compactness_mean": "Average Compactness",
    "concavity_mean": "Average Concavity",
    "concave_points_mean": "Average Concave Points",
    "symmetry_mean": "Average Symmetry",
    "fractal_dimension_mean": "Average Fractal Dimension",

    "radius_se": "Radius Variation",
    "texture_se": "Texture Variation",
    "perimeter_se": "Perimeter Variation",
    "area_se": "Area Variation",
    "smoothness_se": "Smoothness Variation",
    "compactness_se": "Compactness Variation",
    "concavity_se": "Concavity Variation",
    "concave_points_se": "Concave Points Variation",
    "symmetry_se": "Symmetry Variation",
    "fractal_dimension_se": "Fractal Dimension Variation",

    "radius_worst": "Largest Radius",
    "texture_worst": "Roughest Texture",
    "perimeter_worst": "Largest Perimeter",
    "area_worst": "Largest Area",
    "smoothness_worst": "Highest Smoothness",
    "compactness_worst": "Highest Compactness",
    "concavity_worst": "Highest Concavity",
    "concave_points_worst": "Most Concave Points",
    "symmetry_worst": "Highest Symmetry",
    "fractal_dimension_worst": "Highest Fractal Dimension",
}
metadata = {
    "feature_names": X.columns.tolist(),
    "top_features": top_features,
    "feature_labels": feature_labels,
    "target_mapping": {"B": 0, "M": 1},
    "target_names": ["benign", "malignant"],
    "n_features": int(X.shape[1]),
    "n_samples": int(len(X)),
    "class_distribution": {
        "benign": int(np.sum(y == 0)),
        "malignant": int(np.sum(y == 1))
    }
}

joblib.dump(metadata, os.path.join(MODEL_DIR, "metadata.pkl"))
print("Saved: backend/models/metadata.pkl")

joblib.dump(top_features, os.path.join(MODEL_DIR, "top_features.pkl"))
print("Saved: backend/models/top_features.pkl")

print("\nLogistic Regression Performance:")
print("Train Accuracy:", lg_train_acc)
print("Test Accuracy:", lg_test_acc)

print("\nRandom Forest Performance:")
print("Train Accuracy:", rf_train_acc)
print("Test Accuracy:", rf_test_acc)

print("\nGradient Boosting Performance:")
print("Train Accuracy:", gb_train_acc)
print("Test Accuracy:", gb_test_acc)