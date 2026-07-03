import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
})

export const generateQuestionsApi = (data) => request.post('/questions/generate', data)
export const getQuestionListApi = (params) => request.get('/questions', { params })
export const updateQuestionApi = (id, data) => request.put(`/questions/${id}`, data)
export const deleteQuestionApi = (id) => request.delete(`/questions/${id}`)
export const saveQuestionsToBankApi = (ids) => request.post('/questions/save-to-bank', { ids })

export default {
  generateQuestionsApi,
  getQuestionListApi,
  updateQuestionApi,
  deleteQuestionApi,
  saveQuestionsToBankApi,
}
