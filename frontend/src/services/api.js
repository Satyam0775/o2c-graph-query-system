import axios from 'axios'

// ✅ Use env OR fallback (IMPORTANT)
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://o2c-graph-query-system-1.onrender.com"

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 sec
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
// ✅ API CALLS (FINAL)
// =========================

export const loadData = () => api.post('/api/load-data')

export const getHealth = () => api.get('/api/health')

export const getGraph = () => api.get('/api/graph')

export const getNode = (nodeId) =>
  api.get(`/api/node/${encodeURIComponent(nodeId)}`)

export const getNodeNeighbors = (nodeId) =>
  api.get(`/api/node/${encodeURIComponent(nodeId)}/neighbors`)

export const runQuery = async (question) => {
  const res = await api.post('/api/query', { question })
  return res.data
}

export default api
