import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000, // 🔥 FIX: increase timeout (3 min)
})

// GLOBAL ERROR HANDLING
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API CALLS

export const loadData = () => api.post('/load-data')

export const getHealth = () => api.get('/health')

export const getGraph = () => api.get('/graph')

export const getNode = (nodeId) =>
  api.get(`/node/${encodeURIComponent(nodeId)}`)

export const getNodeNeighbors = (nodeId) =>
  api.get(`/node/${encodeURIComponent(nodeId)}/neighbors`)

// 🔥 FINAL FIX
export const runQuery = async (question) => {
  const res = await api.post('/query', { question })
  return res.data  // already final data
}

export default api