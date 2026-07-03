import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

export const generateEvaluationApi = (summaryId) =>
  request.post('/evaluations/generate', { summary_id: summaryId })

export const getEvaluationApi = (id) =>
  request.get(`/evaluations/${id}`)

export const addHrCommentApi = (id, hrComment) =>
  request.put(`/evaluations/${id}/hr-comment`, { hr_comment: hrComment })

export const getEvaluationHistoryApi = (resumeId) =>
  request.get(`/evaluations/history/${resumeId}`)

export default {
  generateEvaluationApi,
  getEvaluationApi,
  addHrCommentApi,
  getEvaluationHistoryApi,
}
