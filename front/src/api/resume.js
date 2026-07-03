import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

export const getResumeListApi = (params) => request.get('/resumes', { params })
export const getResumeDetailApi = (id) => request.get(`/resumes/${id}`)
export const uploadResumesApi = (formData, config = {}) =>
  request.post('/resumes/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...config,
  })
export const downloadResumeApi = (id) =>
  request.get(`/resumes/${id}/download`, { responseType: 'blob' })
export const batchDownloadResumeApi = (ids) =>
  request.post('/resumes/batch-download', { ids }, { responseType: 'blob' })
export const deleteResumeApi = (id) => request.delete(`/resumes/${id}`)
export const updateResumeStatusApi = (id, status) =>
  request.patch(`/resumes/${id}/status`, { status })
export const bindResumePositionApi = (id, positionId) =>
  request.put(`/resumes/${id}/bindPosition`, { positionId })
export const reparseResumeApi = (id) => request.post(`/resumes/${id}/reparse`)

export default {
  getResumeListApi,
  getResumeDetailApi,
  uploadResumesApi,
  downloadResumeApi,
  batchDownloadResumeApi,
  deleteResumeApi,
  updateResumeStatusApi,
  bindResumePositionApi,
  reparseResumeApi,
}
