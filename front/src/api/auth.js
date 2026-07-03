import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

export const loginApi = (data) => request.post('/hr/login', data)

export default {
  loginApi,
}
