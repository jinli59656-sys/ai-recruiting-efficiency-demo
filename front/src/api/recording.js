import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 20000,
})

export const getRecordingListApi = (params) => request.get('/recordings', { params })
export const uploadRecordingApi = (formData, config = {}) =>
  request.post('/recordings/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...config,
  })
export const startTranscribeApi = (id) => request.post(`/recordings/${id}/transcribe`)
export const getRecordingDetailApi = (id) => request.get(`/recordings/${id}`)
export const getRecordingStatusApi = (id) => request.get(`/recordings/${id}/status`)
export const getRecordingTranscriptApi = (id) => request.get(`/recordings/${id}/transcript`)
export const updateRecordingTranscriptApi = (id, transcript) =>
  request.put(`/recordings/${id}/transcript`, { transcript })
export const deleteRecordingApi = (id) => request.delete(`/recordings/${id}`)
export const getRecordingStreamUrl = (id) => `/api/v1/recordings/${id}/stream`

export default {
  getRecordingListApi,
  uploadRecordingApi,
  startTranscribeApi,
  getRecordingDetailApi,
  getRecordingStatusApi,
  getRecordingTranscriptApi,
  updateRecordingTranscriptApi,
  deleteRecordingApi,
  getRecordingStreamUrl,
}
