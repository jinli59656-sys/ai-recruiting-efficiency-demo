import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

export const getDepartmentOptionsApi = () => {
  return Promise.resolve({
    data: [
      { label: '技术部', value: '技术部' },
      { label: '产品部', value: '产品部' },
      { label: '设计部', value: '设计部' },
      { label: '市场部', value: '市场部' },
      { label: '人力资源部', value: '人力资源部' },
      { label: '财务部', value: '财务部' },
    ],
  })
}

export const getPositionListApi = (params) => request.get('/positions', { params })

export const getPositionDetailApi = (id) => request.get(`/positions/${id}`)

export const createPositionApi = (data) => request.post('/positions', data)

export const updatePositionApi = (id, data) => request.put(`/positions/${id}`, data)

export const deletePositionApi = (id) => request.delete(`/positions/${id}`)

export default {
  getDepartmentOptionsApi,
  getPositionListApi,
  getPositionDetailApi,
  createPositionApi,
  updatePositionApi,
  deletePositionApi,
}
