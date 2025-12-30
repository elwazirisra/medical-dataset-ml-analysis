"""
Flask backend API for Breast Cancer ML Explainability Demo
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://medical-dataset-ml-analysis.vercel.app/",
            "http://localhost:3000" 
        ]
    }
})
# -----------------------------
# Load models
# -----------------------------
def load_models():
    """Load all trained models and metadata"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, 'models')  # models folder inside backend

    print(f"Looking for models in: {models_dir}")

    if not os.path.exists(models_dir):
        raise FileNotFoundError(f"Models directory not found: {models_dir}")

    required_files = [
        'logistic_regression.pkl',
        'random_forest.pkl',
        'gradient_boosting.pkl',
        'metadata.pkl',
        'feature_stats.pkl',
        'top_features.pkl'
    ]

    missing_files = [f for f in required_files if not os.path.exists(os.path.join(models_dir, f))]
    if missing_files:
        raise FileNotFoundError(f"Missing model files: {', '.join(missing_files)}")

    # Load models
    models = {
        'logistic_regression': joblib.load(os.path.join(models_dir, 'logistic_regression.pkl')),
        'random_forest': joblib.load(os.path.join(models_dir, 'random_forest.pkl')),
        'gradient_boosting': joblib.load(os.path.join(models_dir, 'gradient_boosting.pkl'))
    }

    # Load metadata
    metadata = joblib.load(os.path.join(models_dir, 'metadata.pkl'))
    feature_stats = joblib.load(os.path.join(models_dir, 'feature_stats.pkl'))
    top_features = joblib.load(os.path.join(models_dir, 'top_features.pkl'))

    return models, metadata, feature_stats, top_features

# Load models at startup
try:
    models, metadata, feature_stats, top_features = load_models()
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    models = metadata = feature_stats = top_features = None

# -----------------------------
# API Endpoints
# -----------------------------
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy' if models else 'error', 'message': 'Models not loaded' if not models else 'ok'})

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    if not metadata:
        return jsonify({'error': 'Models not loaded'}), 503
    return jsonify({
        'feature_names': metadata['feature_names'],
        'target_names': metadata['target_names'],
        'n_features': metadata['n_features'],
        'n_samples': metadata['n_samples'],
        'class_distribution': metadata['class_distribution'],
        'top_features': top_features
    })

@app.route('/api/feature-stats', methods=['GET'])
def get_feature_stats():
    if not feature_stats:
        return jsonify({'error': 'Models not loaded'}), 503
    return jsonify(feature_stats)

@app.route('/api/predict', methods=['POST'])
def predict():
    if not models:
        return jsonify({'error': 'Models not loaded'}), 503

    data = request.json
    model_name = data.get('model', 'logistic_regression')
    feature_values = data.get('features', {})

    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not found'}), 400

    all_features = metadata['feature_names']
    input_array = np.array([feature_values.get(f, feature_stats[f]['mean']) for f in all_features]).reshape(1, -1)

    model = models[model_name]
    prediction = int(model.predict(input_array)[0])
    probabilities = model.predict_proba(input_array)[0]

    # Feature importance
    feature_importance = None
    if model_name == 'logistic_regression':
        coef = model.named_steps['classifier'].coef_[0]
        feature_importance = {f: float(coef[i]) for i, f in enumerate(all_features)}
    elif model_name in ['random_forest', 'gradient_boosting']:
        importance = model.named_steps['classifier'].feature_importances_
        feature_importance = {f: float(importance[i]) for i, f in enumerate(all_features)}

    return jsonify({
        'prediction': prediction,
        'probabilities': {'benign': float(probabilities[0]), 'malignant': float(probabilities[1])},
        'feature_importance': feature_importance
    })

@app.route('/api/predict-all', methods=['POST'])
def predict_all():
    if not models:
        return jsonify({'error': 'Models not loaded'}), 503

    data = request.json
    feature_values = data.get('features', {})
    all_features = metadata['feature_names']
    input_array = np.array([feature_values.get(f, feature_stats[f]['mean']) for f in all_features]).reshape(1, -1)

    results = {}
    for model_name, model in models.items():
        prediction = int(model.predict(input_array)[0])
        probabilities = model.predict_proba(input_array)[0]

        # Feature importance
        feature_importance = None
        if model_name == 'logistic_regression':
            coef = model.named_steps['classifier'].coef_[0]
            feature_importance = {f: float(coef[i]) for i, f in enumerate(all_features)}
        elif model_name in ['random_forest', 'gradient_boosting']:
            importance = model.named_steps['classifier'].feature_importances_
            feature_importance = {f: float(importance[i]) for i, f in enumerate(all_features)}

        results[model_name] = {
            'prediction': prediction,
            'probabilities': {'benign': float(probabilities[0]), 'malignant': float(probabilities[1])},
            'feature_importance': feature_importance
        }

    return jsonify(results)

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data/raw/breast_cancer_wisconsin.csv'))
    df = data.copy()
    return jsonify({
        'features': df.columns.tolist(),
        'data': df.values.tolist()
    })

# -----------------------------
# Start server
# -----------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    app.run(host=host, port=port, debug=False, use_reloader=False)
