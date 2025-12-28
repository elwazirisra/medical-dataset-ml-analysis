import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { getMetadata } from '../services/api'
import './Home.css'

function Home() {
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const data = await getMetadata()
        setMetadata(data)
      } catch (error) {
        console.error('Error fetching metadata:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchMetadata()
  }, [])

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  if (!metadata) {
    return <div className="page-container">Error loading metadata</div>
  }

  const pieData = [
    { name: 'Benign', value: metadata.class_distribution.benign, color: '#28a745' },
    { name: 'Malignant', value: metadata.class_distribution.malignant, color: '#dc3545' },
  ]

  return (
    <div className="page-container">
      <div className="home-hero">
        <h1 className="page-title">🔬 Breast Cancer ML Explainability Demo</h1>
        <p className="hero-subtitle">
          An interactive educational demonstration exploring how machine learning models 
          make predictions and explain feature influence in medical diagnosis.
        </p>
      </div>

      <div className="stats-section">
        <h2 className="section-title">Dataset Overview</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{metadata.n_samples}</div>
            <div className="stat-label">Total Samples</div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🔢</div>
            <div className="stat-value">{metadata.n_features}</div>
            <div className="stat-label">Features</div>
          </div>
          <div className="stat-card stat-card-benign">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{metadata.class_distribution.benign}</div>
            <div className="stat-label">Benign Cases</div>
          </div>
          <div className="stat-card stat-card-malignant">
            <div className="stat-icon">⚠️</div>
            <div className="stat-value">{metadata.class_distribution.malignant}</div>
            <div className="stat-label">Malignant Cases</div>
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: '3rem' }}>
        <div className="info-card">
          <h2 className="card-title">📋 About the Dataset</h2>
          <div className="card-content">
            <div className="dataset-header">
              <h3>Breast Cancer Wisconsin (Diagnostic) Dataset</h3>
            </div>
            
            <div className="info-row">
              <span className="info-label">Features:</span>
              <span className="info-value">{metadata.n_features} numeric tumor characteristics</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Samples:</span>
              <span className="info-value">{metadata.n_samples} cases</span>
            </div>

            <div className="class-info">
              <div className="class-item">
                <span className="class-badge benign-badge">Benign</span>
                <span className="class-description">(non-cancerous): {metadata.class_distribution.benign} cases</span>
              </div>
              <div className="class-item">
                <span className="class-badge malignant-badge">Malignant</span>
                <span className="class-description">(cancerous): {metadata.class_distribution.malignant} cases</span>
              </div>
            </div>

            <div className="features-section">
              <h4>Feature Measurements Include:</h4>
              <div className="feature-tags">
                <span className="feature-tag">Radius</span>
                <span className="feature-tag">Texture</span>
                <span className="feature-tag">Perimeter</span>
                <span className="feature-tag">Area</span>
                <span className="feature-tag">Smoothness</span>
                <span className="feature-tag">Compactness</span>
                <span className="feature-tag">Concavity</span>
                <span className="feature-tag">Concave Points</span>
                <span className="feature-tag">And more...</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="info-card">
          <h2 className="card-title">🎯 Purpose of This Demo</h2>
          <div className="card-content">
            <p className="purpose-intro">
              This interactive application demonstrates key concepts in machine learning explainability:
            </p>
            
            <div className="purpose-items">
              <div className="purpose-item">
                <div className="purpose-icon">🤖</div>
                <div className="purpose-content">
                  <strong>How ML models make predictions</strong>
                  <span>using tumor feature measurements</span>
                </div>
              </div>
              
              <div className="purpose-item">
                <div className="purpose-icon">📈</div>
                <div className="purpose-content">
                  <strong>Feature influence</strong>
                  <span>which features push predictions toward benign vs. malignant</span>
                </div>
              </div>
              
              <div className="purpose-item">
                <div className="purpose-icon">⚖️</div>
                <div className="purpose-content">
                  <strong>Model comparison</strong>
                  <span>how different algorithms interpret the same data</span>
                </div>
              </div>
              
              <div className="purpose-item">
                <div className="purpose-icon">📊</div>
                <div className="purpose-content">
                  <strong>Data exploration</strong>
                  <span>visualizations of the dataset characteristics</span>
                </div>
              </div>
            </div>

            <div className="cta-section">
              <p className="cta-text">
                Use the navigation sidebar to explore different aspects of the models!
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-section">
        <h2 className="section-title">Class Distribution</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default Home

