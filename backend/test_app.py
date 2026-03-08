"""
Comprehensive unit tests for Flask backend API (app.py)
Run with: pytest backend/test_app.py -v
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
import numpy as np

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app module
import app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Flask test client fixture"""
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def valid_features():
    """Valid feature dictionary with all 30 features"""
    return {
        "mean radius": 14.5,
        "mean texture": 19.2,
        "mean perimeter": 95.5,
        "mean area": 580.0,
        "mean smoothness": 0.1,
        "mean compactness": 0.2,
        "mean concavity": 0.3,
        "mean concave points": 0.15,
        "mean symmetry": 0.18,
        "mean fractal dimension": 0.06,
        "radius error": 0.5,
        "texture error": 0.9,
        "perimeter error": 3.0,
        "area error": 40.0,
        "smoothness error": 0.01,
        "compactness error": 0.02,
        "concavity error": 0.03,
        "concave points error": 0.01,
        "symmetry error": 0.02,
        "fractal dimension error": 0.003,
        "worst radius": 16.5,
        "worst texture": 25.0,
        "worst perimeter": 110.0,
        "worst area": 800.0,
        "worst smoothness": 0.15,
        "worst compactness": 0.35,
        "worst concavity": 0.45,
        "worst concave points": 0.28,
        "worst symmetry": 0.35,
        "worst fractal dimension": 0.09
    }


@pytest.fixture
def partial_features():
    """Partial feature dictionary (missing most features)"""
    return {
        "mean radius": 14.5,
        "mean texture": 19.2
    }


@pytest.fixture
def mock_models_loaded():
    """Mock the models being loaded successfully"""
    with patch('app.models', {
        'logistic_regression': MagicMock(),
        'random_forest': MagicMock(),
        'gradient_boosting': MagicMock()
    }), patch('app.metadata', {
        'feature_names': ['mean radius', 'mean texture'],
        'target_names': ['benign', 'malignant']
    }), patch('app.feature_stats', {
        'mean radius': {'mean': 14.5, 'min': 6.9, 'max': 28.1},
        'mean texture': {'mean': 19.2, 'min': 9.0, 'max': 39.3}
    }), patch('app.top_features', ['mean radius', 'mean texture']):
        yield


@pytest.fixture
def mock_models_not_loaded():
    """Mock the models failing to load"""
    with patch('app.models', None), \
         patch('app.metadata', None), \
         patch('app.feature_stats', None), \
         patch('app.top_features', None):
        yield


# ============================================================================
# Tests for /api/health
# ============================================================================

class TestHealthEndpoint:
    """Tests for GET /api/health"""

    def test_health_healthy_when_models_loaded(self, client):
        """Test health endpoint returns healthy when models are loaded"""
        response = client.get('/api/health')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['message'] == 'ok'

    def test_health_returns_error_when_models_not_loaded(self, client, mock_models_not_loaded):
        """Test health endpoint returns error when models fail to load"""
        # Reload app to pick up mocked state
        import importlib
        importlib.reload(app)

        with app.app.test_client() as client:
            response = client.get('/api/health')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['status'] == 'error'
            assert 'Models not loaded' in data['message']


# ============================================================================
# Tests for /api/metadata
# ============================================================================

class TestMetadataEndpoint:
    """Tests for GET /api/metadata"""

    def test_metadata_success(self, client):
        """Test metadata endpoint returns expected fields"""
        response = client.get('/api/metadata')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert 'feature_names' in data
        assert 'target_names' in data
        assert 'n_features' in data
        assert 'n_samples' in data
        assert 'class_distribution' in data
        assert 'top_features' in data

    def test_metadata_returns_lists(self, client):
        """Test metadata returns lists for feature names"""
        response = client.get('/api/metadata')
        data = json.loads(response.data)

        assert isinstance(data['feature_names'], list)
        assert isinstance(data['target_names'], list)
        assert len(data['feature_names']) == 30  # Breast cancer dataset has 30 features
        assert len(data['target_names']) == 2     # benign, malignant

    def test_metadata_models_not_loaded(self, client, mock_models_not_loaded):
        """Test metadata returns 503 when models not loaded"""
        import importlib
        importlib.reload(app)

        with app.app.test_client() as client:
            response = client.get('/api/metadata')
            assert response.status_code == 503


# ============================================================================
# Tests for /api/feature-stats
# ============================================================================

class TestFeatureStatsEndpoint:
    """Tests for GET /api/feature-stats"""

    def test_feature_stats_success(self, client):
        """Test feature stats returns statistics for all features"""
        response = client.get('/api/feature-stats')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert 'mean radius' in data

        # Check structure of feature stats
        feature_stat = data['mean radius']
        assert 'min' in feature_stat
        assert 'max' in feature_stat
        assert 'mean' in feature_stat
        assert 'std' in feature_stat

    def test_feature_stats_models_not_loaded(self, client, mock_models_not_loaded):
        """Test feature stats returns 503 when models not loaded"""
        import importlib
        importlib.reload(app)

        with app.app.test_client() as client:
            response = client.get('/api/feature-stats')
            assert response.status_code == 503


# ============================================================================
# Tests for /api/predict
# ============================================================================

class TestPredictEndpoint:
    """Tests for POST /api/predict"""

    def test_predict_logistic_regression_success(self, client, valid_features):
        """Test predict endpoint with logistic regression"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': valid_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data
        assert 'probabilities' in data
        assert 'feature_importance' in data
        assert data['probabilities']['benign'] + data['probabilities']['malignant'] == pytest.approx(1.0)

    def test_predict_random_forest(self, client, valid_features):
        """Test predict endpoint with random forest"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'random_forest',
                'features': valid_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data

    def test_predict_gradient_boosting(self, client, valid_features):
        """Test predict endpoint with gradient boosting"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'gradient_boosting',
                'features': valid_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data

    def test_predict_invalid_model(self, client, valid_features):
        """Test predict endpoint with invalid model name"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'invalid_model',
                'features': valid_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()

    def test_predict_partial_features_uses_defaults(self, client, partial_features):
        """Test predict with missing features uses mean values"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': partial_features
            }),
            content_type='application/json'
        )

        # Should still work, using mean values for missing features
        assert response.status_code == 200

    def test_predict_empty_body(self, client):
        """Test predict with empty request body"""
        response = client.post(
            '/api/predict',
            data=json.dumps({}),
            content_type='application/json'
        )

        # Should still work, using mean values for all features
        assert response.status_code == 200

    def test_predict_empty_features(self, client):
        """Test predict with empty features dict"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': {}
            }),
            content_type='application/json'
        )

        # Should work, using mean values for all features
        assert response.status_code == 200

    def test_predict_models_not_loaded(self, client, valid_features, mock_models_not_loaded):
        """Test predict returns 503 when models not loaded"""
        import importlib
        importlib.reload(app)

        with app.app.test_client() as client:
            response = client.post(
                '/api/predict',
                data=json.dumps({
                    'model': 'logistic_regression',
                    'features': valid_features
                }),
                content_type='application/json'
            )

            assert response.status_code == 503

    def test_predict_returns_valid_probabilities(self, client, valid_features):
        """Test probabilities sum to 1.0"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': valid_features
            }),
            content_type='application/json'
        )

        data = json.loads(response.data)
        probs = data['probabilities']
        assert probs['benign'] + probs['malignant'] == pytest.approx(1.0, abs=0.01)
        assert 0 <= probs['benign'] <= 1
        assert 0 <= probs['malignant'] <= 1

    def test_predict_prediction_is_binary(self, client, valid_features):
        """Test prediction is either 0 or 1"""
        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': valid_features
            }),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert data['prediction'] in [0, 1]


# ============================================================================
# Tests for /api/predict-all
# ============================================================================

class TestPredictAllEndpoint:
    """Tests for POST /api/predict-all"""

    def test_predict_all_success(self, client, valid_features):
        """Test predict-all returns all three models"""
        response = client.post(
            '/api/predict-all',
            data=json.dumps({
                'features': valid_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should have all three models
        assert 'logistic_regression' in data
        assert 'random_forest' in data
        assert 'gradient_boosting' in data

        # Each should have prediction, probabilities, feature_importance
        for model_name, result in data.items():
            assert 'prediction' in result
            assert 'probabilities' in result
            assert 'feature_importance' in result

    def test_predict_all_partial_features(self, client, partial_features):
        """Test predict-all with partial features"""
        response = client.post(
            '/api/predict-all',
            data=json.dumps({
                'features': partial_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_predict_all_empty_body(self, client):
        """Test predict-all with empty request body"""
        response = client.post(
            '/api/predict-all',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_predict_all_empty_features(self, client):
        """Test predict-all with empty features dict"""
        response = client.post(
            '/api/predict-all',
            data=json.dumps({
                'features': {}
            }),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_predict_all_models_not_loaded(self, client, valid_features, mock_models_not_loaded):
        """Test predict-all returns 503 when models not loaded"""
        import importlib
        importlib.reload(app)

        with app.app.test_client() as client:
            response = client.post(
                '/api/predict-all',
                data=json.dumps({
                    'features': valid_features
                }),
                content_type='application/json'
            )

            assert response.status_code == 503


# ============================================================================
# Tests for /api/dataset
# ============================================================================

class TestDatasetEndpoint:
    """Tests for GET /api/dataset"""

    def test_dataset_success(self, client):
        """Test dataset endpoint returns data"""
        response = client.get('/api/dataset')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert 'features' in data
        assert 'data' in data
        assert 'target' in data

    def test_dataset_returns_30_features(self, client):
        """Test dataset returns 30 features"""
        response = client.get('/api/dataset')
        data = json.loads(response.data)

        assert len(data['features']) == 30

    def test_dataset_returns_569_samples(self, client):
        """Test dataset returns correct number of samples"""
        response = client.get('/api/dataset')
        data = json.loads(response.data)

        assert len(data['data']) == 569
        assert len(data['target']) == 569

    def test_dataset_target_is_binary(self, client):
        """Test target values are 0 or 1"""
        response = client.get('/api/dataset')
        data = json.loads(response.data)

        unique_targets = set(data['target'])
        assert unique_targets.issubset({0, 1})


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================

class TestEdgeCases:
    """Edge case tests"""

    def test_predict_all_zeros(self, client):
        """Test prediction with all zeros (boundary case)"""
        all_zeros = {f: 0.0 for f in app.metadata['feature_names']}

        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': all_zeros
            }),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_predict_extreme_values(self, client):
        """Test prediction with extreme values"""
        extreme = {f: 999999.0 for f in app.metadata['feature_names']}

        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': extreme
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        # Should return some prediction, even if extreme

    def test_predict_negative_values(self, client):
        """Test prediction with negative values"""
        negative = {f: -100.0 for f in app.metadata['feature_names']}

        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': negative
            }),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_predict_none_values(self, client):
        """Test prediction with None values (should use mean)"""
        none_features = {f: None for f in app.metadata['feature_names']}

        response = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': none_features
            }),
            content_type='application/json'
        )

        assert response.status_code == 200


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full workflows"""

    def test_full_prediction_workflow(self, client, valid_features):
        """Test complete prediction workflow"""
        # 1. Check health
        health = client.get('/api/health')
        assert health.status_code == 200

        # 2. Get metadata
        metadata = client.get('/api/metadata')
        assert metadata.status_code == 200
        meta_data = json.loads(metadata.data)
        assert len(meta_data['feature_names']) == 30

        # 3. Get feature stats
        stats = client.get('/api/feature-stats')
        assert stats.status_code == 200

        # 4. Make prediction
        prediction = client.post(
            '/api/predict',
            data=json.dumps({
                'model': 'logistic_regression',
                'features': valid_features
            }),
            content_type='application/json'
        )
        assert prediction.status_code == 200
        pred_data = json.loads(prediction.data)
        assert 'prediction' in pred_data

        # 5. Compare all models
        compare = client.post(
            '/api/predict-all',
            data=json.dumps({
                'features': valid_features
            }),
            content_type='application/json'
        )
        assert compare.status_code == 200
        compare_data = json.loads(compare.data)
        assert len(compare_data) == 3

    def test_get_dataset_for_visualization(self, client):
        """Test dataset retrieval for visualization"""
        # 1. Get dataset
        dataset = client.get('/api/dataset')
        assert dataset.status_code == 200

        data = json.loads(dataset.data)

        # 2. Verify structure for visualization
        assert len(data['features']) > 0
        assert len(data['data']) > 0
        assert len(data['target']) == len(data['data'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
