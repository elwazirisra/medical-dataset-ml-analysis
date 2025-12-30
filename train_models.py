"""
Train and save ML models for Breast Cancer Wisconsin dataset.
Includes preprocessing pipeline and multiple model types.
"""

import joblib
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import os
import sklearn
print(f"Using scikit-learn version: {sklearn.__version__}")

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Load dataset
print("Loading Breast Cancer Wisconsin dataset...")
data = load_breast_cancer()
X, y = data.data, data.target
feature_names = data.feature_names

# Convert to DataFrame for easier handling
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")
print(f"Number of features: {X_train.shape[1]}")

# Define preprocessing pipeline
preprocessor = StandardScaler()

# 1. Logistic Regression
print("\n" + "="*50)
print("Training Logistic Regression...")
lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000))
])
lr_pipeline.fit(X_train, y_train)
lr_train_acc = accuracy_score(y_train, lr_pipeline.predict(X_train))
lr_test_acc = accuracy_score(y_test, lr_pipeline.predict(X_test))
print(f"Train Accuracy: {lr_train_acc:.4f}")
print(f"Test Accuracy: {lr_test_acc:.4f}")

joblib.dump(lr_pipeline, 'backend/models/logistic_regression.pkl')
print("Saved: backend/models/logistic_regression.pkl")

# 2. Random Forest
print("\n" + "="*50)
print("Training Random Forest...")
rf_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10))
])
rf_pipeline.fit(X_train, y_train)
rf_train_acc = accuracy_score(y_train, rf_pipeline.predict(X_train))
rf_test_acc = accuracy_score(y_test, rf_pipeline.predict(X_test))
print(f"Train Accuracy: {rf_train_acc:.4f}")
print(f"Test Accuracy: {rf_test_acc:.4f}")

joblib.dump(rf_pipeline, 'backend/models/random_forest.pkl')
print("Saved: backend/models/random_forest.pkl")

# 3. Gradient Boosting
print("\n" + "="*50)
print("Training Gradient Boosting...")
gb_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5))
])
gb_pipeline.fit(X_train, y_train)
gb_train_acc = accuracy_score(y_train, gb_pipeline.predict(X_train))
gb_test_acc = accuracy_score(y_test, gb_pipeline.predict(X_test))
print(f"Train Accuracy: {gb_train_acc:.4f}")
print(f"Test Accuracy: {gb_test_acc:.4f}")

joblib.dump(gb_pipeline, 'backend/models/gradient_boosting.pkl')
print("Saved: backend/models/gradient_boosting.pkl")

# Save feature names and metadata
metadata = {
    'feature_names': feature_names.tolist(),
    'target_names': data.target_names.tolist(),
    'n_features': len(feature_names),
    'n_samples': len(X),
    'class_distribution': {
        'benign': int(np.sum(y == 0)),
        'malignant': int(np.sum(y == 1))
    }
}
joblib.dump(metadata, 'backend/models/metadata.pkl')
print("Saved: backend/models/metadata.pkl")

# Save dataset statistics for slider ranges
feature_stats = {}
for i, feature in enumerate(feature_names):
    feature_stats[feature] = {
        'min': float(X[:, i].min()),
        'max': float(X[:, i].max()),
        'mean': float(X[:, i].mean()),
        'std': float(X[:, i].std())
    }
joblib.dump(feature_stats, 'backend/models/feature_stats.pkl')
print("Saved: backend/models/feature_stats.pkl")

# Get top features from Logistic Regression
lr_coef = lr_pipeline.named_steps['classifier'].coef_[0]
feature_importance_lr = pd.DataFrame({
    'feature': feature_names,
    'coefficient': lr_coef,
    'abs_coefficient': np.abs(lr_coef)
}).sort_values('abs_coefficient', ascending=False)

top_features = feature_importance_lr.head(10)['feature'].tolist()
joblib.dump(top_features, 'backend/models/top_features.pkl')
print("Saved: backend/models/top_features.pkl")

print("\n" + "="*50)
print("Model training complete!")
print("="*50)

