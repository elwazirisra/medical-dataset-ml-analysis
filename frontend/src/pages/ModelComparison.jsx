import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getMetadata, getFeatureStats, predictAll } from '../services/api'
import './ModelComparison.css'

function ModelComparison() {
  const [metadata, setMetadata] = useState(null)
  const [featureStats, setFeatureStats] = useState(null)
  const [featureValues, setFeatureValues] = useState({})
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [meta, stats] = await Promise.all([
          getMetadata(),
          getFeatureStats()
        ])
        setMetadata(meta)
        setFeatureStats(stats)
        
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
      makePredictions()
    }
  }, [featureValues, metadata, featureStats])

  const makePredictions = async () => {
    try {
      const results = await predictAll(featureValues)
      setPredictions(results)
    } catch (error) {
      console.error('Error making predictions:', error)
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
  const modelNames = {
    'logistic_regression': 'Logistic Regression',
    'random_forest': 'Random Forest',
    'gradient_boosting': 'Gradient Boosting'
  }

  // Prepare comparison data
  const comparisonData = predictions ? Object.entries(predictions).map(([model, pred]) => ({
    model: modelNames[model],
    benign: pred.probabilities.benign,
    malignant: pred.probabilities.malignant
  })) : []

  // Prepare feature importance comparison
  const importanceData = predictions ? (() => {
    const allFeatures = metadata.feature_names
    const top15 = allFeatures.slice(0, 15) // Get top 15 for display
    
    return top15.map(feature => {
      const data = { feature: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()).substring(0, 20) }
      
      Object.entries(predictions).forEach(([model, pred]) => {
        if (pred.feature_importance && pred.feature_importance[feature] !== undefined) {
          data[modelNames[model]] = Math.abs(pred.feature_importance[feature])
        }
      })
      
      return data
    })
  })() : []

  return (
    <div className="page-container">
      <div className="comparison-hero">
        <h1 className="page-title">Model Comparison</h1>
        <p className="hero-subtitle">
          Compare predictions from multiple machine learning models on the same input.
          Each model may interpret the features differently, giving you insights into how different algorithms work!
        </p>
      </div>

      <div className="features-section">
        <div className="section-header">
          <h2 className="section-title">Input Features</h2>
          <p className="section-description">
            Adjust the top 10 most influential features to see how all models respond
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

      {predictions && (
        <>
          <div className="predictions-section">
            <h2 className="section-title">Model Predictions</h2>
            <p className="section-description">
              All three models make predictions on the same input features
            </p>
            
            <div className="models-grid">
              {Object.entries(predictions).map(([model, pred]) => {
                const predictionClass = pred.prediction === 1 ? 'Benign' : 'Malignant'
                const isUncertain = Math.abs(pred.probabilities.benign - pred.probabilities.malignant) < 0.15
                const boxClass = isUncertain ? 'uncertain' : (predictionClass === 'Benign' ? 'benign' : 'malignant')
                const confidence = Math.max(pred.probabilities.benign, pred.probabilities.malignant) * 100
                
                return (
                  <div key={model} className={`model-prediction-card ${boxClass}`}>
                    <div className="model-card-header">
                      <h3 className="model-name">{modelNames[model]}</h3>
                      <div className="model-icon">
                        {model === 'logistic_regression' ? '📊' : model === 'random_forest' ? '🌲' : '📈'}
                      </div>
                    </div>
                    <div className="prediction-result">
                      <div className="prediction-icon-large">
                        {predictionClass === 'Benign' ? '✅' : predictionClass === 'Malignant' ? '⚠️' : '❓'}
                      </div>
                      <div className="prediction-class-large">{predictionClass}</div>
                      <div className="prediction-confidence">
                        Confidence: {confidence.toFixed(1)}%
                      </div>
                    </div>
                    <div className="probability-breakdown">
                      <div className="prob-item">
                        <span className="prob-label">Benign</span>
                        <div className="prob-bar-wrapper">
                          <div 
                            className="prob-bar benign-prob"
                            style={{ width: `${pred.probabilities.benign * 100}%` }}
                          ></div>
                        </div>
                        <span className="prob-value">{(pred.probabilities.benign * 100).toFixed(1)}%</span>
                      </div>
                      <div className="prob-item">
                        <span className="prob-label">Malignant</span>
                        <div className="prob-bar-wrapper">
                          <div 
                            className="prob-bar malignant-prob"
                            style={{ width: `${pred.probabilities.malignant * 100}%` }}
                          ></div>
                        </div>
                        <span className="prob-value">{(pred.probabilities.malignant * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="comparison-charts-section">
            <div className="chart-section">
              <h2 className="section-title">Probability Comparison</h2>
              <p className="section-description">
                Side-by-side comparison of prediction probabilities across all models
              </p>
              <div className="chart-card">
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
                    <XAxis 
                      dataKey="model" 
                      stroke="#6c757d"
                      tick={{ fill: '#6c757d', fontSize: 12 }}
                    />
                    <YAxis 
                      domain={[0, 1]} 
                      stroke="#6c757d"
                      tick={{ fill: '#6c757d' }}
                      label={{ 
                        value: 'Probability', 
                        angle: -90, 
                        position: 'insideLeft',
                        style: { fill: '#6c757d', fontSize: 14 }
                      }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e9ecef',
                        borderRadius: '8px',
                        padding: '10px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="benign" fill="#28a745" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="malignant" fill="#dc3545" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-section">
              <h2 className="section-title">Feature Importance Comparison</h2>
              <div className="importance-info-box">
                <div className="info-item">
                  <div className="info-badge lr-badge">LR</div>
                  <span><strong>Logistic Regression:</strong> Uses coefficients to show feature influence</span>
                </div>
                <div className="info-item">
                  <div className="info-badge rf-badge">RF</div>
                  <span><strong>Random Forest:</strong> Uses mean decrease in impurity</span>
                </div>
                <div className="info-item">
                  <div className="info-badge gb-badge">GB</div>
                  <span><strong>Gradient Boosting:</strong> Uses feature importance scores</span>
                </div>
              </div>
              <div className="chart-card">
                <ResponsiveContainer width="100%" height={500}>
                  <BarChart data={importanceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
                    <XAxis 
                      dataKey="feature" 
                      angle={-45} 
                      textAnchor="end" 
                      height={150}
                      stroke="#6c757d"
                      tick={{ fill: '#6c757d', fontSize: 11 }}
                    />
                    <YAxis 
                      stroke="#6c757d"
                      tick={{ fill: '#6c757d' }}
                      label={{ 
                        value: 'Importance Score', 
                        angle: -90, 
                        position: 'insideLeft',
                        style: { fill: '#6c757d', fontSize: 14 }
                      }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e9ecef',
                        borderRadius: '8px',
                        padding: '10px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="Logistic Regression" fill="#007bff" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="Random Forest" fill="#28a745" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="Gradient Boosting" fill="#ffc107" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ModelComparison

