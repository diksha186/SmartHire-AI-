/**
 * Single axios instance used by the whole application.
 * - baseURL comes from the .env file (never hard-coded)
 * - the JWT is attached automatically to every request
 * - a 401 response logs the user out
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('smarthire_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('smarthire_token')
      localStorage.removeItem('smarthire_user')
      if (!window.location.pathname.startsWith('/login')) window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/** Turn any FastAPI error into a readable string for the UI. */
export const errorMessage = (error) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ')
  return error?.message || 'Something went wrong. Please try again.'
}

/* ---------------- API service functions ---------------- */

export const authApi = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  me: () => api.get('/api/auth/me'),
}

export const candidateApi = {
  dashboard: () => api.get('/api/candidates/dashboard'),
  getProfile: () => api.get('/api/candidates/profile'),
  updateProfile: (data) => api.put('/api/candidates/profile', data),
  uploadResume: (formData) =>
    api.post('/api/candidates/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  latestAnalysis: () => api.get('/api/candidates/resume/analyze'),
  recommendations: (limit = 10) => api.get(`/api/candidates/recommendations?limit=${limit}`),
}

export const jobApi = {
  list: (params) => api.get('/api/jobs', { params }),
  details: (id) => api.get(`/api/jobs/${id}`),
  myMatch: (id) => api.get(`/api/jobs/${id}/match`),
  apply: (id, data) => api.post(`/api/jobs/${id}/apply`, data),
}

export const employerApi = {
  dashboard: () => api.get('/api/employers/dashboard'),
  getCompany: () => api.get('/api/employers/profile'),
  updateCompany: (data) => api.put('/api/employers/profile', data),
  myJobs: () => api.get('/api/employers/jobs'),
  createJob: (data) => api.post('/api/employers/jobs', data),
  updateJob: (id, data) => api.put(`/api/employers/jobs/${id}`, data),
  deleteJob: (id) => api.delete(`/api/employers/jobs/${id}`),
  closeJob: (id) => api.patch(`/api/employers/jobs/${id}/close`),
  applicants: (id) => api.get(`/api/employers/jobs/${id}/applicants`),
}

export const applicationApi = {
  mine: () => api.get('/api/applications'),
  details: (id) => api.get(`/api/applications/${id}`),
  updateStatus: (id, status) => api.put(`/api/applications/${id}/status`, { application_status: status }),
  withdraw: (id) => api.delete(`/api/applications/${id}`),
}

export const adminApi = {
  statistics: () => api.get('/api/admin/statistics'),
  users: (role) => api.get('/api/admin/users', { params: role ? { role } : {} }),
  toggleUser: (id) => api.patch(`/api/admin/users/${id}/toggle-active`),
  deleteUser: (id) => api.delete(`/api/admin/users/${id}`),
  jobs: () => api.get('/api/admin/jobs'),
  deleteJob: (id) => api.delete(`/api/admin/jobs/${id}`),
  applications: () => api.get('/api/admin/applications'),
}

export default api
