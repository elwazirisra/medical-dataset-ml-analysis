import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { getMetadata, getFeatureStats, predict } from '../services/api'
import './ModelDemo.css'

function ModelDemo() {
  const [metadata, setMetadata] = useState(null)
  const [featureStats, setFeatureStats] = useState(null)
  const [featureValues, setFeatureValues] = useState({})
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState('logistic_regression')
  
  const modelOptions = [
    { value: 'logistic_regression', label: 'Logistic Regression', description: 'Linear model with interpretable coefficients' },
    { value: 'random_forest', label: 'Random Forest', description: 'Ensemble of decision trees' },
    { value: 'gradient_boosting', label: 'Gradient Boosting', description: 'Sequential ensemble learning' }
  ]

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [meta, stats] = await Promise.all([
          getMetadata(),
          getFeatureStats()
        ])
        setMetadata(meta)
        setFeatureStats(stats)
        
        // Initialize feature values with means
        const initialValues = {}
        meta.top_features.slice(0, 10).forEach(feature => {
          initialValues[feature] = stats[feature].mean
        })
        setFeatureValues(initialValues)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    if (metadata && featureStats && Object.keys(featureValues).length > 0) {
      makePrediction()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [featureValues, metadata, featureStats, selectedModel])

  const makePrediction = async () => {
    try {
      const result = await predict(selectedModel, featureValues)
      setPrediction(result)
    } catch (error) {
      console.error('Error making prediction:', error)
    }
  }

  const handleSliderChange = (feature, value) => {
    setFeatureValues(prev => ({
      ...prev,
      [feature]: parseFloat(value)
    }))
  }

  if (loading || !metadata || !featureStats) {
    return <div className="page-container">Loading...</div>
  }

  const top10Features = metadata.top_features.slice(0, 10)
  const predictionClass = prediction ? (prediction.prediction === 1 ? 'Benign' : 'Malignant') : null
  const isUncertain = prediction && Math.abs(prediction.probabilities.benign - prediction.probabilities.malignant) < 0.15
  const predictionBoxClass = isUncertain ? 'uncertain' : (predictionClass === 'Benign' ? 'benign' : 'malignant')

  // Prepare feature importance data for chart
  const featureImportanceData = prediction?.feature_importance
    ? Object.entries(prediction.feature_importance)
        .map(([feature, value]) => ({
          feature: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          coefficient: selectedModel === 'logistic_regression' ? value : Math.abs(value), // For tree models, show absolute importance
        }))
        .sort((a, b) => Math.abs(b.coefficient) - Math.abs(a.coefficient))
        .slice(0, 15)
    : []

  const selectedModelInfo = modelOptions.find(m => m.value === selectedModel)

  return (
    <div className="page-container">
      <div className="demo-hero">
        <h1 className="page-title">Model Demo</h1>
        <p className="hero-subtitle">
          Select a model and adjust the feature values using the sliders below. The model will predict in real-time 
          whether the tumor is benign or malignant based on these measurements.
        </p>
        
        <div className="model-selector">
          <label className="model-selector-label">Select Model:</label>
          <div className="model-options">
            {modelOptions.map(option => (
              <button
                key={option.value}
                className={`model-option ${selectedModel === option.value ? 'active' : ''}`}
                onClick={() => setSelectedModel(option.value)}
              >
                <div className="model-option-name">{option.label}</div>
                <div className="model-option-desc">{option.description}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="section-header">
          <h2 className="section-title">Input Features</h2>
          <p className="section-description">
            Adjust the top 10 most influential features (based on model coefficients)
          </p>
        </div>

        <div className="sliders-grid">
          {top10Features.map((feature, index) => {
            const currentValue = featureValues[feature] || featureStats[feature].mean
            const stats = featureStats[feature]
            const percentage = ((currentValue - stats.min) / (stats.max - stats.min)) * 100
            
            return (
              <div key={feature} className="slider-card">
                <div className="slider-header">
                  <span className="slider-feature-name">
                    {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span className="slider-value">{currentValue.toFixed(2)}</span>
                </div>
                <div className="slider-wrapper">
                  <input
                    type="range"
                    className="slider-input"
                    min={stats.min}
                    max={stats.max}
                    step={(stats.max - stats.min) / 100}
                    value={currentValue}
                    onChange={(e) => handleSliderChange(feature, e.target.value)}
                    style={{
                      background: `linear-gradient(to right, #667eea 0%, #667eea ${percentage}%, #e9ecef ${percentage}%, #e9ecef 100%)`
                    }}
                  />
                </div>
                <div className="slider-stats">
                  <span className="stat-item">
                    <span className="stat-label">Min:</span>
                    <span className="stat-value">{stats.min.toFixed(2)}</span>
                  </span>
                  <span className="stat-item">
                    <span className="stat-label">Mean:</span>
                    <span className="stat-value">{stats.mean.toFixed(2)}</span>
                  </span>
                  <span className="stat-item">
                    <span className="stat-label">Max:</span>
                    <span className="stat-value">{stats.max.toFixed(2)}</span>
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {prediction && (
        <>
          <div className="prediction-section">
            <h2 className="section-title"> Prediction Results</h2>
            
            <div className="prediction-grid">
              <div className={`prediction-card ${predictionBoxClass}`}>
                <div className="prediction-icon">
                  {predictionClass === 'Benign' ? '✅' : predictionClass === 'Malignant' ? '⚠️' : '❓'}
                </div>
                <div className="prediction-content">
                  <div className="prediction-label">Predicted Class</div>
                  <div className="prediction-class">{predictionClass}</div>
                  <div className="prediction-confidence">
                    Confidence: {(Math.max(prediction.probabilities.benign, prediction.probabilities.malignant) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="probability-card">
                <h3 className="card-subtitle">Probability Distribution</h3>
                <div className="probability-bars">
                  <div className="probability-bar-wrapper">
                    <div className="probability-label-row">
                      <span className="probability-label">Benign</span>
                      <span className="probability-value">{(prediction.probabilities.benign * 100).toFixed(1)}%</span>
                    </div>
                    <div className="probability-bar-container">
                      <div 
                        className="probability-bar benign-bar"
                        style={{ width: `${prediction.probabilities.benign * 100}%` }}
                      >
                        <div className="probability-bar-fill"></div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="probability-bar-wrapper">
                    <div className="probability-label-row">
                      <span className="probability-label">Malignant</span>
                      <span className="probability-value">{(prediction.probabilities.malignant * 100).toFixed(1)}%</span>
                    </div>
                    <div className="probability-bar-container">
                      <div 
                        className="probability-bar malignant-bar"
                        style={{ width: `${prediction.probabilities.malignant * 100}%` }}
                      >
                        <div className="probability-bar-fill"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="influence-section">
            <div className="section-header">
              <h2 className="section-title">📊 Feature Influence Analysis</h2>
              <div className="legend-box">
                {selectedModel === 'logistic_regression' ? (
                  <>
                    <div className="legend-item">
                      <div className="legend-color positive"></div>
                      <span><strong>Positive coefficients</strong> → push toward <strong>Malignant</strong></span>
                    </div>
                    <div className="legend-item">
                      <div className="legend-color negative"></div>
                      <span><strong>Negative coefficients</strong> → push toward <strong>Benign</strong></span>
                    </div>
                    <div className="legend-note">
                      Larger absolute values = stronger influence
                    </div>
                  </>
                ) : (
                  <div className="legend-note">
                    <strong>Feature Importance:</strong> Shows how much each feature contributes to the model's predictions. 
                    Higher values indicate more important features.
                  </div>
                )}
              </div>
            </div>
            
            <div className="chart-card">
              <ResponsiveContainer width="100%" height={500}>
                <BarChart data={featureImportanceData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
                  <XAxis 
                    type="number" 
                    stroke="#6c757d"
                    tick={{ fill: '#6c757d' }}
                    label={{ 
                      value: selectedModel === 'logistic_regression' ? 'Coefficient Value' : 'Importance Score', 
                      position: 'insideBottom', 
                      offset: -5,
                      style: { fill: '#6c757d', fontSize: 14 }
                    }}
                  />
                  <YAxis 
                    dataKey="feature" 
                    type="category" 
                    width={200}
                    stroke="#6c757d"
                    tick={{ fill: '#6c757d', fontSize: 12 }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solidrgb(102, 104, 106)',
                      borderRadius: '8px',
                      padding: '10px'
                    }}
                  />
                  <Bar 
                    dataKey="coefficient" 
                    radius={[0, 8, 8, 0]}
                  >
                    {featureImportanceData.map((entry, index) => {
                      let fillColor = '#667eea'
                      if (selectedModel === 'logistic_regression') {
                        fillColor = entry.coefficient > 0 ? '#dc3545' : '#28a745'
                      } else {
                        // For tree-based models, use a gradient of one color
                        fillColor = '#667eea'
                      }
                      return (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={fillColor} 
                        />
                      )
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="info-card-educational">
            <div className="info-icon">💡</div>
            <div className="info-content">
              <strong>Why Scaling Matters</strong>
              <p>
                Logistic Regression is sensitive to feature scales. Features with larger values could 
                dominate the prediction. That's why we use StandardScaler to normalize all features to 
                have mean=0 and std=1 before training.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ModelDemo

