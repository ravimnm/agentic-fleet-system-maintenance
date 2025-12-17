import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 8000,
})

export const fetchFleetOverview = () => api.get('/fleet/overview')
export const fetchTopRisk = () => api.get('/fleet/top-risk')
export const fetchAgentActions = () => api.get('/fleet/agent-actions')
export const fetchVehicles = (userVehicleId) => {
  if (userVehicleId) {
    return api.get('/vehicles/list', { params: { userVehicleId } })
  }
  return api.get('/vehicles/list')
}
export const fetchRisk = (vehicleId) => api.get(`/risk/${vehicleId}`)
export const fetchPrediction = (vehicleId) => api.get(`/predict/${vehicleId}`)
export const fetchTelemetry = (vehicleId) => api.get(`/telemetry/latest/${vehicleId}`)
export const postPredict = (payload) => api.post('/predict', payload)
export const postFeedback = (payload) => api.post('/feedback', payload)
export const fetchAlerts = () => api.get('/alerts')
export const fetchAgentTimeline = (vehicleId) => api.get(`/agent-timeline/${vehicleId}`)
export const fetchRecommendations = (vehicleId) => api.get(`/recommendations/${vehicleId}`)
export const ingestTelemetryFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/telemetry/ingest', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export default api

