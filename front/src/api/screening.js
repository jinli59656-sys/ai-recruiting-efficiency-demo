import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

export const positionMatchApi = (data) =>
  request.post('/screening/match', data, {
    timeout: 60000,
  })

export const getPositionAnalysisApi = (resumeId, positionId) =>
  request.get(`/screening/analysis/${resumeId}`, {
    params: { position_id: positionId },
    timeout: 60000,
  })

export const batchMarkResumeApi = (resumeIds, mark) =>
  request.post('/screening/batch-mark', {
    resume_ids: resumeIds,
    mark,
  })

export default {
  positionMatchApi,
  getPositionAnalysisApi,
  batchMarkResumeApi,
}
