# Breast Cancer ML Explainability Demo

**Beyond Accuracy: Explaining Predictions in Medical ML**

An interactive educational demonstration using the Breast Cancer Wisconsin (Diagnostic) dataset to show how machine learning models make predictions and explain feature influence.

⚠️ **IMPORTANT**: This is an educational demo only — NOT a medical diagnostic tool.

## Features

- 🏠 **Home Page**: Introduction to the dataset and project purpose
- 🎯 **Model Demo**: Interactive Logistic Regression predictions with feature influence visualization
- ⚖️ **Model Comparison**: Compare predictions from multiple models (LR, Random Forest, Gradient Boosting)
- 📊 **Dataset Visualization**: Explore dataset characteristics with histograms, scatter plots, and box plots

## Architecture

This project uses a **React frontend** with a **Flask backend API**:
- **Frontend**: React + Vite with React Router for navigation
- **Backend**: Flask REST API serving ML model predictions
- **Visualization**: Recharts for interactive charts and graphs

## Setup Instructions

### 1. Train Models

First, train and save the models:

```bash
python train_models.py
```

This will:
- Load the Breast Cancer Wisconsin dataset
- Train three models: Logistic Regression, Random Forest, and Gradient Boosting
- Save models to the `models/` directory
- Generate feature statistics and metadata

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Start the Flask backend:**
```bash
cd backend
python app.py
```
The backend will run on `http://localhost:5000`

**Terminal 2 - Start the React frontend:**
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000` and automatically open in your browser.

## Project Structure

```
medical-dataset-ml-analysis/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/          # React page components
│   │   ├── components/     # Reusable components
│   │   ├── services/       # API service layer
│   │   └── App.jsx         # Main app component
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── train_models.py         # Model training script
├── models/                 # Saved models (created after training)
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── gradient_boosting.pkl
│   ├── metadata.pkl
│   ├── feature_stats.pkl
│   └── top_features.pkl
└── README.md
```

## Usage

1. **Home Page**: Learn about the dataset and project purpose
2. **Model Demo (LR)**: 
   - Adjust feature sliders to see how predictions change in real-time
   - View feature coefficients and their influence
   - Understand how positive/negative coefficients affect predictions
3. **Model Comparison**:
   - Compare predictions from all three models side-by-side
   - See how different algorithms interpret the same features
   - View feature importance comparisons across models
4. **Dataset Visualization**:
   - Explore class distributions with pie charts
   - Compare feature distributions between benign and malignant cases
   - Analyze feature separation with interactive scatter plots

## API Endpoints

The Flask backend provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/metadata` - Get dataset metadata
- `GET /api/feature-stats` - Get feature statistics for sliders
- `POST /api/predict` - Get prediction from a single model
- `POST /api/predict-all` - Get predictions from all models
- `GET /api/dataset` - Get full dataset for visualization

## Educational Notes

- **Feature Scaling**: The models use StandardScaler to normalize features. This is important for Logistic Regression, which is sensitive to feature scales.
- **Feature Influence**: 
  - Positive coefficients → push toward Malignant
  - Negative coefficients → push toward Benign
- **Model Differences**: Different algorithms (linear vs. tree-based) may interpret features differently, which is why comparing models is valuable.

## Disclaimer

This application is for **educational purposes only** to demonstrate how machine learning models make predictions. It is **NOT a medical diagnostic tool** and should **NOT be used** for actual medical diagnosis or treatment decisions.

## Technologies Used

**Frontend:**
- **React**: UI framework
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing
- **Recharts**: Chart library
- **Axios**: HTTP client

**Backend:**
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **scikit-learn**: Machine learning models and preprocessing
- **pandas & numpy**: Data manipulation
- **joblib**: Model serialization

