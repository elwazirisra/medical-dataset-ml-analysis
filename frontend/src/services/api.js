import axios from 'axios'

// Vite proxy is configured in vite.config.js to proxy /api to http://localhost:5000
// So we can use a relative URL, or the full URL if proxy doesn't work
// If backend is on a different port, update vite.config.js proxy target
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getMetadata = async () => {
  try {
    const response = await api.get('/metadata')
    return response.data
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to backend server. Make sure Flask backend is running on http://localhost:5000')
    }
    throw new Error(error.response?.data?.error || error.message || 'Failed to fetch metadata')
  }
}

export const getFeatureStats = async () => {
  try {
    const response = await api.get('/feature-stats')
    return response.data
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to backend server. Make sure Flask backend is running on http://localhost:5000')
    }
    throw new Error(error.response?.data?.error || error.message || 'Failed to fetch feature stats')
  }
}

export const predict = async (modelName, features) => {
  try {
    const response = await api.post('/predict', {
      model: modelName,
      features,
    })
    return response.data
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to backend server. Make sure Flask backend is running on http://localhost:5000')
    }
    throw new Error(error.response?.data?.error || error.message || 'Failed to make prediction')
  }
}

export const predictAll = async (features) => {
  try {
    const response = await api.post('/predict-all', {
      features,
    })
    return response.data
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to backend server. Make sure Flask backend is running on http://localhost:5000')
    }
    throw new Error(error.response?.data?.error || error.message || 'Failed to make predictions')
  }
}

export const getDataset = async () => {
  try {
    const response = await api.get('/dataset')
    return response.data
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to backend server. Make sure Flask backend is running on http://localhost:5000')
    }
    throw new Error(error.response?.data?.error || error.message || 'Failed to fetch dataset')
  }
}

export default api

