import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import ModelDemo from './pages/ModelDemo'
import ModelComparison from './pages/ModelComparison'
import DatasetVisualization from './pages/DatasetVisualization'
import Disclaimer from './components/Disclaimer'
import './App.css'

function Navigation() {
  const location = useLocation()
  
  return (
    <nav className="sidebar">
      <h1>🔬 ML Demo</h1>
      <ul>
        <li className={location.pathname === '/' ? 'active' : ''}>
          <Link to="/">Home</Link>
        </li>
        <li className={location.pathname === '/model-demo' ? 'active' : ''}>
          <Link to="/model-demo">Model Demo</Link>
        </li>
        <li className={location.pathname === '/model-comparison' ? 'active' : ''}>
          <Link to="/model-comparison">Model Comparison</Link>
        </li>
        <li className={location.pathname === '/visualization' ? 'active' : ''}>
          <Link to="/visualization">Dataset Visualization</Link>
        </li>
      </ul>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <main className="main-content">
          <Disclaimer />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/model-demo" element={<ModelDemo />} />
            <Route path="/model-comparison" element={<ModelComparison />} />
            <Route path="/visualization" element={<DatasetVisualization />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

