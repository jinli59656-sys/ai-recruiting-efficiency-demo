import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 20000,
})

export const getDashboardOverviewApi = () => request.get('/dashboard/overview')

export default {
  getDashboardOverviewApi,
}
