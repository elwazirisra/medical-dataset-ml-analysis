# Breast Cancer ML Explainability Demo

**Beyond Accuracy: Explaining Predictions in Medical ML**

An interactive educational demonstration using the Breast Cancer Wisconsin (Diagnostic) dataset to show how machine learning models make predictions and explain feature influence.

> **⚠️ IMPORTANT**: This is an educational demo only — NOT a medical diagnostic tool.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [API Examples](#api-examples)
- [Model Details](#model-details)
- [Educational Notes](#educational-notes)
- [Troubleshooting](#troubleshooting)
- [Technology Stack](#technology-stack)
- [Disclaimer](#disclaimer)

---

## Features

- 🏠 **Home Page** — Introduction to the dataset and project purpose
- 🎯 **Model Demo** — Interactive Logistic Regression predictions with feature influence visualization
- ⚖️ **Model Comparison** — Compare predictions from multiple models (LR, Random Forest, Gradient Boosting)
- 📊 **Dataset Visualization** — Explore dataset characteristics with histograms, scatter plots, and box plots

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | Required for backend and model training |
| Node.js | 18+ | Required for frontend |
| npm | 9+ | Comes with Node.js |

Verify installations:

```bash
python --version    # Should show 3.8 or higher
node --version      # Should show 18 or higher
npm --version       # Should show 9 or higher
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd medical-dataset-ml-analysis

# 2. Train the ML models
python train_models.py

# 3. Start backend (Terminal 1)
cd backend
python app.py

# 4. Start frontend (Terminal 2)
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

---

## Project Structure

```
medical-dataset-ml-analysis/
├── backend/
│   ├── app.py                   # Flask API server with 6 endpoints
│   ├── models/                  # Serialized ML models
│   │   ├── logistic_regression.pkl
│   │   ├── random_forest.pkl
│   │   ├── gradient_boosting.pkl
│   │   ├── metadata.pkl
│   │   ├── feature_stats.pkl
│   │   └── top_features.pkl
│   ├── data/                    # Dataset files
│   │   └── breast_cancer_wisconsin.csv
│   ├── requirements.txt         # Python dependencies
│   ├── Procfile                 # Deployment config (Heroku)
│   └── runtime.txt              # Python version for deployment
├── frontend/
│   ├── src/
│   │   ├── pages/               # React page components
│   │   │   ├── Home.jsx
│   │   │   ├── ModelDemo.jsx
│   │   │   ├── ModelComparison.jsx
│   │   │   └── DatasetVisualization.jsx
│   │   ├── components/          # Reusable components
│   │   │   └── Disclaimer.jsx
│   │   ├── services/            # API service layer
│   │   │   └── api.js
│   │   ├── App.jsx              # Main app with routing
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx             # React entry point
│   ├── index.html
│   ├── package.json             # Node dependencies
│   ├── package-lock.json
│   └── vite.config.js           # Vite + proxy config
├── train_models.py              # ML training script
├── data/                        # Additional datasets
│   └── Breast Tissue Impedance Measurements.numbers
├── .gitignore
└── README.md
```

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)              │
│   Vite + React Router + Recharts + Axios                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP /api/* (via Vite proxy)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask Backend (Port 5000)               │
│   Flask + Flask-CORS + scikit-learn                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     ML Models (In-Memory)                   │
│   Pipeline = StandardScaler + Classifier                    │
│   logistic_regression.pkl, random_forest.pkl, gb.pkl       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Training**: `train_models.py` → sklearn dataset → trained pipelines → `.pkl` files
2. **Startup**: `app.py` loads `.pkl` models into memory
3. **Request**: Frontend → Vite proxy → Flask endpoint → model.predict() → JSON response
4. **Visualization**: Frontend fetches raw dataset → Recharts renders charts

---

## Setup Instructions

### Step 1: Train Models

```bash
python train_models.py
```

**Output:**
```
Using scikit-learn version: 1.x.x
Loading Breast Cancer Wisconsin dataset...
Training set size: 455
Test set size: 114
Number of features: 30

==================================================
Training Logistic Regression...
Train Accuracy: 0.9890
Test Accuracy: 0.9737
Saved: backend/models/logistic_regression.pkl

==================================================
Training Random Forest...
Train Accuracy: 1.0000
Test Accuracy: 0.9649
Saved: backend/models/random_forest.pkl

==================================================
Training Gradient Boosting...
Train Accuracy: 1.0000
Test Accuracy: 0.9561
Saved: backend/models/gradient_boosting.pkl

==================================================
Model training complete!
```

This creates the following files in `backend/models/`:
- `logistic_regression.pkl` — Linear model
- `random_forest.pkl` — Tree ensemble (100 trees)
- `gradient_boosting.pkl` — Boosted trees (100 estimators)
- `metadata.pkl` — Feature names, class distribution
- `feature_stats.pkl` — Min/max/mean/std for each feature
- `top_features.pkl` — Top 10 features by importance

### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Requirements:**
```
flask
flask-cors
scikit-learn
pandas
numpy
joblib
gunicorn
```

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## Running the Application

### Development Mode

**Terminal 1 — Backend:**
```bash
cd backend
python app.py
```

Expected output:
```
Looking for models in: /path/to/backend/models
✅ Models loaded successfully!
 * Running on http://0.0.0.0:5000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in 300 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

Open http://localhost:3000 in your browser.

### Production Mode (Vercel + Heroku)

**Frontend (Vercel):**
```bash
cd frontend
vercel deploy
```

**Backend (Heroku):**
```bash
cd backend
heroku create
git push heroku main
heroku web: python app.py
```

---

## Usage Guide

### 1. Home Page
- Learn about the Breast Cancer Wisconsin dataset
- Understand the project's educational purpose

### 2. Model Demo (Logistic Regression)
- **Adjust sliders** for any of the 30 features
- Click **Predict** to see the result
- View **Feature Coefficients** chart showing which features push toward Benign vs Malignant
- **Real-time updates**: coefficients are recalculated based on slider values

### 3. Model Comparison
- Enter feature values (or use defaults)
- Click **Compare All Models** to see predictions from:
  - Logistic Regression
  - Random Forest
  - Gradient Boosting
- Compare **Feature Importance** across all three models
- Understand how different algorithms interpret the same data

### 4. Dataset Visualization
- **Class Distribution**: Pie chart showing benign vs malignant count
- **Feature Histograms**: Compare distributions between classes
- **Scatter Plots**: Explore feature relationships and class separation
- **Box Plots**: View feature ranges and outliers

---

## API Reference

### Base URL

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:5000` |
| Production | `https://your-backend.herokuapp.com` |

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/metadata` | Dataset metadata (features, classes, distribution) |
| GET | `/api/feature-stats` | Feature statistics (min, max, mean, std) |
| POST | `/api/predict` | Single model prediction |
| POST | `/api/predict-all` | All models prediction |
| GET | `/api/dataset` | Full dataset for visualization |

### CORS

The API allows requests from:
- `http://localhost:3000` (development)
- `https://medical-dataset-ml-analysis.vercel.app` (production)

---

## API Examples

### Health Check

```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "ok"
}
```

### Get Metadata

```bash
curl http://localhost:5000/api/metadata
```

**Response:**
```json
{
  "feature_names": ["mean radius", "mean texture", ...],
  "target_names": ["benign", "malignant"],
  "n_features": 30,
  "n_samples": 569,
  "class_distribution": {
    "benign": 357,
    "malignant": 212
  },
  "top_features": ["worst perimeter", "worst radius", ...]
}
```

### Get Feature Stats

```bash
curl http://localhost:5000/api/feature-stats
```

**Response:**
```json
{
  "mean radius": {
    "min": 6.981,
    "max": 28.11,
    "mean": 14.127,
    "std": 3.524
  },
  ...
}
```

### Single Prediction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model": "logistic_regression",
    "features": {
      "mean radius": 14.5,
      "mean texture": 19.2,
      "mean perimeter": 95.5,
      ...
    }
  }'
```

**Response:**
```json
{
  "prediction": 1,
  "probabilities": {
    "benign": 0.15,
    "malignant": 0.85
  },
  "feature_importance": {
    "mean radius": 0.52,
    "mean texture": -0.21,
    ...
  }
}
```

### All Models Prediction

```bash
curl -X POST http://localhost:5000/api/predict-all \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "mean radius": 14.5,
      "mean texture": 19.2,
      ...
    }
  }'
```

**Response:**
```json
{
  "logistic_regression": {
    "prediction": 1,
    "probabilities": { "benign": 0.15, "malignant": 0.85 },
    "feature_importance": { ... }
  },
  "random_forest": {
    "prediction": 1,
    "probabilities": { "benign": 0.08, "malignant": 0.92 },
    "feature_importance": { ... }
  },
  "gradient_boosting": {
    "prediction": 1,
    "probabilities": { "benign": 0.12, "malignant": 0.88 },
    "feature_importance": { ... }
  }
}
```

### Get Dataset

```bash
curl http://localhost:5000/api/dataset
```

**Response:**
```json
{
  "features": ["mean radius", "mean texture", ...],
  "data": [[12.5, 18.2, ...], ...],
  "target": [0, 1, 0, ...]
}
```

---

## Model Details

### Dataset: Breast Cancer Wisconsin (Diagnostic)

| Property | Value |
|----------|-------|
| Samples | 569 |
| Features | 30 |
| Classes | 2 (benign: 357, malignant: 212) |
| Feature Types | Real-valued (measurements) |

### Models Trained

| Model | Train Accuracy | Test Accuracy | Type |
|-------|----------------|---------------|------|
| Logistic Regression | 98.9% | 97.4% | Linear |
| Random Forest | 100% | 96.5% | Tree Ensemble |
| Gradient Boosting | 100% | 95.6% | Boosted Trees |

### Pipeline Structure

Each model is a sklearn `Pipeline` with two steps:

```python
Pipeline([
    ('scaler', StandardScaler()),    # Normalize features
    ('classifier', Model())          # Classification
])
```

This ensures consistent preprocessing at training and inference time.

---

## Educational Notes

### Feature Scaling

The `StandardScaler` normalizes features to have zero mean and unit variance. This is critical for:
- **Logistic Regression**: Sensitive to feature scales; coefficients become comparable
- **Distance-based methods**: Not used here, but would require scaling

### Understanding Coefficients

**Logistic Regression:**
- Positive coefficient → Higher feature value pushes toward **Malignant (1)**
- Negative coefficient → Higher feature value pushes toward **Benign (0)**

**Tree-Based Models (RF, GB):**
- Feature importance = how much the feature reduces impurity across all splits
- Always positive; higher = more important

### Why Compare Models?

Different algorithms learn different patterns:
- **Linear models** find global linear boundaries
- **Tree ensembles** find complex non-linear boundaries
- Comparing helps understand model limitations and biases

---

## Troubleshooting

### Backend Issues

**"Cannot connect to backend server"**
```bash
# Make sure Flask is running
cd backend
python app.py
# Should show: Running on http://0.0.0.0:5000
```

**"Missing model files"**
```bash
# Run training script first
python train_models.py
# Should create backend/models/*.pkl files
```

**Port already in use**
```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>
```

### Frontend Issues

**"Cannot connect to API"**
- Ensure Flask backend is running on port 5000
- Check Vite proxy configuration in `vite.config.js`

**Build errors**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Model Issues

**"Models not loaded"**
- Verify `backend/models/` directory exists
- Run `python train_models.py` to create models

---

## Technology Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool & dev server |
| React Router | Client-side routing |
| Recharts | Data visualization |
| Axios | HTTP client |

### Backend

| Technology | Purpose |
|------------|---------|
| Flask | Web framework |
| Flask-CORS | Cross-origin requests |
| scikit-learn | ML models & preprocessing |
| pandas | Data manipulation |
| numpy | Numerical operations |
| joblib | Model serialization |

### Deployment

| Service | Component |
|---------|-----------|
| Vercel | Frontend |
| Heroku | Backend |

---

## Disclaimer

This application is for **educational purposes only** to demonstrate how machine learning models make predictions.

**It is NOT:**
- A medical diagnostic tool
- Approved for clinical use
- A replacement for professional medical advice

**Do NOT use this application for:**
- Actual medical diagnosis
- Treatment decisions
- Clinical screening

For any health concerns, consult a qualified healthcare professional.

---

## License

MIT License — Feel free to use this project for learning and demonstration purposes.
