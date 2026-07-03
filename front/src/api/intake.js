import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export const parseIntakeMessageApi = (data) => request.post('/intake/messages/parse', data)
export const getIntakeMessagesApi = (params = {}) => request.get('/intake/messages', { params })
export const getTencentDocsApi = (params = {}) => request.get('/intake/tencent-docs', { params })
export const getIntakeEventsApi = (params = {}) => request.get('/intake/events', { params })

export default {
  parseIntakeMessageApi,
  getIntakeMessagesApi,
  getTencentDocsApi,
  getIntakeEventsApi,
}
