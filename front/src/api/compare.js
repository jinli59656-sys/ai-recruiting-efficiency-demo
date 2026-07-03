import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

export const createCompareApi = (data) => request.post('/comparison/create', data)
export const analyzeCompareApi = (id) => request.post(`/comparison/${id}/analyze`)
export const getCompareDetailApi = (id) => request.get(`/comparison/${id}`)
export const getCompareHistoryApi = (params) => request.get('/comparison/history', { params })
export const exportCompareReportUrl = (id) => `/api/v1/comparison/${id}/export`

export default {
  createCompareApi,
  analyzeCompareApi,
  getCompareDetailApi,
  getCompareHistoryApi,
  exportCompareReportUrl,
}
