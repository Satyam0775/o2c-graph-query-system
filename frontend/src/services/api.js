import axios from 'axios'

// ✅ BASE URL FROM ENV (Render backend)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// ✅ Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 min
})

// ✅ GLOBAL ERROR HANDLING
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// =========================
// ✅ API CALLS (FIXED)
// =========================

export const loadData = () => api.post('/api/load-data')

export const getHealth = () => api.get('/api/health')

export const getGraph = () => api.get('/api/graph')

export const getNode = (nodeId) =>
  api.get(`/api/node/${encodeURIComponent(nodeId)}`)

export const getNodeNeighbors = (nodeId) =>
  api.get(`/api/node/${encodeURIComponent(nodeId)}/neighbors`)

// ✅ QUERY
export const runQuery = async (question) => {
  const res = await api.post('/api/query', { question })
  return res.data
}

export default api
