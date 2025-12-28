"""
Flask backend API for Breast Cancer ML Explainability Demo
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
import os
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration - update with your frontend URL in production
import os
frontend_url = os.environ.get('FRONTEND_URL', '*')
if frontend_url == '*':
    CORS(app)  # Allow all origins (development only)
else:
    CORS(app, resources={r"/api/*": {"origins": [frontend_url]}})

# Load models and metadata
def load_models():
    """Load all trained models and metadata"""
    # Get the absolute path to models directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    models_dir = os.path.join(project_root, 'models')
    
    print(f"Looking for models in: {models_dir}")
    
    if not os.path.exists(models_dir):
        raise FileNotFoundError(f"Models directory not found: {models_dir}. Please run 'python train_models.py' first.")
    
    required_files = [
        'logistic_regression.pkl',
        'random_forest.pkl',
        'gradient_boosting.pkl',
        'metadata.pkl',
        'feature_stats.pkl',
        'top_features.pkl'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(models_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        raise FileNotFoundError(
            f"Missing model files: {', '.join(missing_files)}. "
            f"Please run 'python train_models.py' first."
        )
    
    try:
        print("Loading models...")
        # Try loading with compatibility mode for scikit-learn version differences
        try:
            models = {
                'logistic_regression': joblib.load(os.path.join(models_dir, 'logistic_regression.pkl')),
                'random_forest': joblib.load(os.path.join(models_dir, 'random_forest.pkl')),
                'gradient_boosting': joblib.load(os.path.join(models_dir, 'gradient_boosting.pkl'))
            }
        except (ValueError, TypeError) as e:
            if 'incompatible dtype' in str(e) or 'pickle' in str(e).lower():
                print("⚠️  Model compatibility issue detected. This usually means models were saved with a different scikit-learn version.")
                print("   Retraining models to fix compatibility...")
                raise Exception("Model compatibility error. Please retrain models by running: python train_models.py")
            else:
                raise
        
        print("Loading metadata...")
        metadata = joblib.load(os.path.join(models_dir, 'metadata.pkl'))
        feature_stats = joblib.load(os.path.join(models_dir, 'feature_stats.pkl'))
        top_features = joblib.load(os.path.join(models_dir, 'top_features.pkl'))
        
        return models, metadata, feature_stats, top_features
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Model file not found: {e}. Please run 'python train_models.py' first.")
    except Exception as e:
        if "Model compatibility error" in str(e):
            raise
        raise Exception(f"Error loading models: {e}")

# Load models once at startup
try:
    models, metadata, feature_stats, top_features = load_models()
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    models = None
    metadata = None
    feature_stats = None
    top_features = None

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    if models is None:
        return jsonify({'status': 'error', 'message': 'Models not loaded'}), 503
    return jsonify({'status': 'healthy'})

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Get dataset metadata"""
    if metadata is None:
        return jsonify({'error': 'Models not loaded. Please run python train_models.py first.'}), 503
    
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
    """Get feature statistics for slider ranges"""
    if feature_stats is None:
        return jsonify({'error': 'Models not loaded. Please run python train_models.py first.'}), 503
    return jsonify(feature_stats)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make prediction with a single model"""
    if models is None:
        return jsonify({'error': 'Models not loaded. Please run python train_models.py first.'}), 503
    
    data = request.json
    model_name = data.get('model', 'logistic_regression')
    feature_values = data.get('features', {})
    
    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not found'}), 400
    
    # Prepare input array
    all_features = metadata['feature_names']
    input_array = np.zeros(len(all_features))
    
    for i, feature in enumerate(all_features):
        if feature in feature_values:
            input_array[i] = feature_values[feature]
        else:
            # Use mean value if not provided
            input_array[i] = feature_stats[feature]['mean']
    
    # Make prediction
    model = models[model_name]
    prediction = model.predict(input_array.reshape(1, -1))[0]
    probabilities = model.predict_proba(input_array.reshape(1, -1))[0]
    
    # Get feature importance/coefficients if available
    feature_importance = None
    if model_name == 'logistic_regression':
        coef = model.named_steps['classifier'].coef_[0]
        feature_importance = {
            feature: float(coef[i]) 
            for i, feature in enumerate(all_features)
        }
    elif model_name in ['random_forest', 'gradient_boosting']:
        importance = model.named_steps['classifier'].feature_importances_
        feature_importance = {
            feature: float(importance[i]) 
            for i, feature in enumerate(all_features)
        }
    
    return jsonify({
        'prediction': int(prediction),
        'probabilities': {
            'benign': float(probabilities[1]),
            'malignant': float(probabilities[0])
        },
        'feature_importance': feature_importance
    })

@app.route('/api/predict-all', methods=['POST'])
def predict_all():
    """Get predictions from all models"""
    if models is None:
        return jsonify({'error': 'Models not loaded. Please run python train_models.py first.'}), 503
    
    data = request.json
    feature_values = data.get('features', {})
    
    # Prepare input array
    all_features = metadata['feature_names']
    input_array = np.zeros(len(all_features))
    
    for i, feature in enumerate(all_features):
        if feature in feature_values:
            input_array[i] = feature_values[feature]
        else:
            input_array[i] = feature_stats[feature]['mean']
    
    results = {}
    
    for model_name, model in models.items():
        prediction = model.predict(input_array.reshape(1, -1))[0]
        probabilities = model.predict_proba(input_array.reshape(1, -1))[0]
        
        # Get feature importance
        feature_importance = None
        if model_name == 'logistic_regression':
            coef = model.named_steps['classifier'].coef_[0]
            feature_importance = {
                feature: float(coef[i]) 
                for i, feature in enumerate(all_features)
            }
        elif model_name in ['random_forest', 'gradient_boosting']:
            importance = model.named_steps['classifier'].feature_importances_
            feature_importance = {
                feature: float(importance[i]) 
                for i, feature in enumerate(all_features)
            }
        
        results[model_name] = {
            'prediction': int(prediction),
            'probabilities': {
                'benign': float(probabilities[1]),
                'malignant': float(probabilities[0])
            },
            'feature_importance': feature_importance
        }
    
    return jsonify(results)

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """Get the full dataset for visualization"""
    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target
    
    # Convert to JSON-serializable format
    dataset_json = {
        'features': data.feature_names.tolist(),
        'data': df.values.tolist(),
        'target': data.target.tolist()
    }
    
    return jsonify(dataset_json)

if __name__ == '__main__':
    import socket
    
    def find_free_port(start_port=5000, max_attempts=10):
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")
    
    print("\n" + "="*50)
    print("Starting Flask Backend Server")
    print("="*50)
    
    if models is None:
        print("\n⚠️  WARNING: Models not loaded!")
        print("The server will start but API endpoints will return errors.")
        print("Please run 'python train_models.py' first.\n")
    else:
        print("\n✅ Server ready!")
    
    # Try to find a free port
    port = find_free_port(5000)
    if port != 5000:
        print(f"⚠️  Port 5000 is in use, using port {port} instead")
        print("   (On macOS, you may need to disable AirPlay Receiver)")
    
    print(f"Backend API available at: http://localhost:{port}")
    print("API endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/metadata")
    print("  - GET  /api/feature-stats")
    print("  - POST /api/predict")
    print("  - POST /api/predict-all")
    print("  - GET  /api/dataset")
    print("\n" + "="*50 + "\n")
    
    try:
        # Get port from environment variable (for production) or use found port
        port = int(os.environ.get('PORT', port))
        host = os.environ.get('HOST', '127.0.0.1')
        debug = os.environ.get('FLASK_ENV') != 'production'
        
        print(f"\n🚀 Starting Flask server on http://{host}:{port}")
        if not debug:
            print("   Production mode")
        else:
            print("   Press Ctrl+C to stop the server\n")
        app.run(debug=debug, port=port, host=host, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print(f"   Try using a different port or stop the process using port {port}")
            print(f"   On macOS: lsof -ti:{port} | xargs kill")
        else:
            print(f"\n❌ Error starting server: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure port is not already in use")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Verify models exist: python train_models.py")
        raise

