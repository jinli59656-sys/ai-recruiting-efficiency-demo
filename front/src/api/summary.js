import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

export const generateSummaryApi = (recordingId) =>
  request.post('/summaries/generate', { recordingId })

export const getSummaryApi = (recordingId) =>
  request.get(`/summaries/${recordingId}`)

export const updateSummaryApi = (id, data) =>
  request.put(`/summaries/${id}`, data)

export const regenerateSummaryApi = (id) =>
  request.post(`/summaries/${id}/regenerate`)

export default {
  generateSummaryApi,
  getSummaryApi,
  updateSummaryApi,
  regenerateSummaryApi,
}
