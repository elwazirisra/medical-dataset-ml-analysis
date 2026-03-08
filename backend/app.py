"""
Flask backend API for Breast Cancer ML Explainability Demo
"""

import os
import joblib
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.datasets import load_breast_cancer

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://medical-dataset-ml-analysis.vercel.app",
                "http://localhost:3000",
            ]
        }
    },
)

models = None
metadata = None
feature_stats = None
top_features = None


def load_models():
    """Load trained models and metadata from backend/models."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, "models")

    print(f"Looking for models in: {models_dir}")

    if not os.path.exists(models_dir):
        raise FileNotFoundError(f"Models directory not found: {models_dir}")

    required_files = [
        "logistic_regression.pkl",
        "random_forest.pkl",
        "gradient_boosting.pkl",
        "metadata.pkl",
        "feature_stats.pkl",
    ]

    missing_files = [
        filename
        for filename in required_files
        if not os.path.exists(os.path.join(models_dir, filename))
    ]
    if missing_files:
        raise FileNotFoundError(f"Missing model files: {', '.join(missing_files)}")

    loaded_models = {
        "logistic_regression": joblib.load(
            os.path.join(models_dir, "logistic_regression.pkl")
        ),
        "random_forest": joblib.load(
            os.path.join(models_dir, "random_forest.pkl")
        ),
        "gradient_boosting": joblib.load(
            os.path.join(models_dir, "gradient_boosting.pkl")
        ),
    }

    loaded_metadata = joblib.load(os.path.join(models_dir, "metadata.pkl"))
    loaded_feature_stats = joblib.load(os.path.join(models_dir, "feature_stats.pkl"))
    loaded_top_features = loaded_metadata.get("top_features", [])

    return loaded_models, loaded_metadata, loaded_feature_stats, loaded_top_features


def build_input_array(feature_values):
    """Build model input in the exact training feature order."""
    all_features = metadata.get("feature_names", [])
    if not all_features:
        raise ValueError("Metadata is missing feature_names")

    missing_stats = [
        feature
        for feature in all_features
        if feature not in feature_stats or "mean" not in feature_stats[feature]
    ]
    if missing_stats:
        raise ValueError(
            f"Feature stats missing for features: {', '.join(missing_stats)}"
        )

    input_values = []
    for feature in all_features:
        raw_value = feature_values.get(feature, feature_stats[feature]["mean"])
        input_values.append(float(raw_value))

    return np.array(input_values, dtype=float).reshape(1, -1), all_features


def build_feature_importance(model_name, model, all_features):
    """Return feature importance/coefficient map for the selected model."""
    if model_name == "logistic_regression":
        coef = model.named_steps["classifier"].coef_[0]
        return {feature: float(coef[i]) for i, feature in enumerate(all_features)}

    if model_name in ["random_forest", "gradient_boosting"]:
        importance = model.named_steps["classifier"].feature_importances_
        return {feature: float(importance[i]) for i, feature in enumerate(all_features)}

    return None


try:
    models, metadata, feature_stats, top_features = load_models()
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    models = None
    metadata = None
    feature_stats = None
    top_features = None


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "healthy" if models else "error",
            "message": "ok" if models else "Models not loaded",
        }
    )


@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    if not metadata:
        return jsonify({"error": "Models not loaded"}), 503

    return jsonify(
        {
            "feature_names": metadata.get("feature_names", []),
            "target_names": metadata.get("target_names", []),
            "n_features": metadata.get("n_features", 0),
            "n_samples": metadata.get("n_samples", 0),
            "class_distribution": metadata.get("class_distribution", {}),
            "top_features": metadata.get("top_features", top_features or []),
            "feature_labels": metadata.get("feature_labels", {}),
        }
    )


@app.route("/api/feature-stats", methods=["GET"])
def get_feature_stats():
    if not feature_stats:
        return jsonify({"error": "Models not loaded"}), 503
    return jsonify(feature_stats)


@app.route("/api/predict", methods=["POST"])
def predict():
    if not models:
        return jsonify({"error": "Models not loaded"}), 503

    try:
        data = request.get_json(silent=True) or {}
        model_name = data.get("model", "logistic_regression")
        feature_values = data.get("features", {})

        if not isinstance(feature_values, dict):
            return jsonify({"error": "features must be an object"}), 400

        if model_name not in models:
            return jsonify({"error": f"Model {model_name} not found"}), 400

        input_array, all_features = build_input_array(feature_values)

        model = models[model_name]
        prediction_value = int(model.predict(input_array)[0])
        probabilities = model.predict_proba(input_array)[0]
        feature_importance = build_feature_importance(model_name, model, all_features)

        return jsonify(
            {
                "prediction": prediction_value,
                "probabilities": {
                    "benign": float(probabilities[0]),
                    "malignant": float(probabilities[1]),
                },
                "feature_importance": feature_importance,
            }
        )

    except Exception as e:
        print("PREDICT ERROR:", repr(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict-all", methods=["POST"])
def predict_all():
    if not models:
        return jsonify({"error": "Models not loaded"}), 503

    try:
        data = request.get_json(silent=True) or {}
        feature_values = data.get("features", {})

        if not isinstance(feature_values, dict):
            return jsonify({"error": "features must be an object"}), 400

        input_array, all_features = build_input_array(feature_values)

        results = {}
        for model_name, model in models.items():
            prediction_value = int(model.predict(input_array)[0])
            probabilities = model.predict_proba(input_array)[0]
            feature_importance = build_feature_importance(
                model_name, model, all_features
            )

            results[model_name] = {
                "prediction": prediction_value,
                "probabilities": {
                    "benign": float(probabilities[0]),
                    "malignant": float(probabilities[1]),
                },
                "feature_importance": feature_importance,
            }

        return jsonify(results)

    except Exception as e:
        print("PREDICT-ALL ERROR:", repr(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/dataset", methods=["GET"])
def get_dataset():
    dataset = load_breast_cancer()
    return jsonify(
        {
            "features": dataset.feature_names.tolist(),
            "data": dataset.data.tolist(),
            "target": dataset.target.tolist(),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    app.run(host=host, port=port, debug=False, use_reloader=False)