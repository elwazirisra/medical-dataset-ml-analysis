import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from 'recharts'
import { getMetadata, getDataset } from '../services/api'
import './DatasetVisualization.css'

function DatasetVisualization() {
  const [metadata, setMetadata] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [selectedFeatures, setSelectedFeatures] = useState([])
  const [xFeature, setXFeature] = useState('')
  const [yFeature, setYFeature] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [meta, data] = await Promise.all([
          getMetadata(),
          getDataset()
        ])
        setMetadata(meta)
        setDataset(data)
        setSelectedFeatures(meta.feature_names.slice(0, 6))
        setXFeature(meta.feature_names[0])
        setYFeature(meta.feature_names[1])
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading || !metadata || !dataset) {
    return <div className="page-container">Loading...</div>
  }

  const pieData = [
    { name: 'Benign', value: metadata.class_distribution.benign, color: '#28a745' },
    { name: 'Malignant', value: metadata.class_distribution.malignant, color: '#dc3545' },
  ]

  // Prepare histogram data
  const prepareHistogramData = (featureIndex) => {
    const benignData = []
    const malignantData = []
    
    dataset.data.forEach((row, idx) => {
      const value = row[featureIndex]
      const target = dataset.target[idx]
      if (target === 1) {
        benignData.push(value)
      } else {
        malignantData.push(value)
      }
    })
    
    return { benign: benignData, malignant: malignantData }
  }

  // Prepare scatter plot data
  const scatterData = dataset.data.map((row, idx) => {
    const xIdx = metadata.feature_names.indexOf(xFeature)
    const yIdx = metadata.feature_names.indexOf(yFeature)
    return {
      x: row[xIdx],
      y: row[yIdx],
      target: dataset.target[idx]
    }
  })

  const benignScatter = scatterData.filter(d => d.target === 1)
  const malignantScatter = scatterData.filter(d => d.target === 0)

  return (
    <div className="page-container">
      <h1 className="page-title">Dataset Visualization</h1>
      <p className="page-subtitle">Explore the characteristics of the Breast Cancer Wisconsin dataset.</p>

      <h2>Class Distribution</h2>
      <div className="grid-2">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={100}
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
        <div>
          <h3>Statistics</h3>
          <div className="stats-list">
            <div className="stat-item">
              <strong>Total Samples:</strong> {metadata.n_samples}
            </div>
            <div className="stat-item">
              <strong>Benign Cases:</strong> {metadata.class_distribution.benign}
            </div>
            <div className="stat-item">
              <strong>Malignant Cases:</strong> {metadata.class_distribution.malignant}
            </div>
            <div className="stat-item">
              <strong>Benign Percentage:</strong> {(metadata.class_distribution.benign / metadata.n_samples * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      <h2>Feature Distributions</h2>
      <p>Select features to visualize their distributions:</p>
      <div className="feature-selector">
        <select
          multiple
          value={selectedFeatures}
          onChange={(e) => {
            const values = Array.from(e.target.selectedOptions, option => option.value)
            setSelectedFeatures(values)
          }}
          size="5"
          style={{ width: '100%', padding: '0.5rem' }}
        >
          {metadata.feature_names.map(feature => (
            <option key={feature} value={feature}>
              {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {selectedFeatures.length > 0 && (
        <div className="histogram-grid">
          {selectedFeatures.map(feature => {
            const featureIndex = metadata.feature_names.indexOf(feature)
            const histData = prepareHistogramData(featureIndex)
            
            // Create bins for histogram
            const allValues = [...histData.benign, ...histData.malignant]
            const min = Math.min(...allValues)
            const max = Math.max(...allValues)
            const bins = 20
            const binWidth = (max - min) / bins
            
            const binData = Array.from({ length: bins }, (_, i) => {
              const binStart = min + i * binWidth
              const binEnd = binStart + binWidth
              const benignCount = histData.benign.filter(v => v >= binStart && v < binEnd).length
              const malignantCount = histData.malignant.filter(v => v >= binStart && v < binEnd).length
              return {
                range: `${binStart.toFixed(1)}-${binEnd.toFixed(1)}`,
                benign: benignCount,
                malignant: malignantCount
              }
            })
            
            return (
              <div key={feature} className="histogram-chart">
                <h4>{feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={binData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="benign" stackId="a" fill="#28a745" />
                    <Bar dataKey="malignant" stackId="a" fill="#dc3545" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )
          })}
        </div>
      )}

      <h2>🔍 Feature Separation Analysis</h2>
      <p>Visualize how well features separate benign and malignant cases.</p>
      <div className="grid-2" style={{ marginBottom: '1rem' }}>
        <div>
          <label>X-axis feature:</label>
          <select
            value={xFeature}
            onChange={(e) => setXFeature(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
          >
            {metadata.feature_names.map(feature => (
              <option key={feature} value={feature}>
                {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Y-axis feature:</label>
          <select
            value={yFeature}
            onChange={(e) => setYFeature(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
          >
            {metadata.feature_names.map(feature => (
              <option key={feature} value={feature}>
                {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={500}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            dataKey="x" 
            name={xFeature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name={yFeature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          />
          <ZAxis type="number" dataKey="target" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter name="Benign" data={benignScatter} fill="#28a745" />
          <Scatter name="Malignant" data={malignantScatter} fill="#dc3545" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

export default DatasetVisualization

