import axios from 'axios'
import { showToast } from 'vant'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  // Try getting token from H5 or Admin
  const token = localStorage.getItem('token') || localStorage.getItem('adminToken')
  if (token) {
    config.headers['Authorization'] = token
  }
  return config
}, error => {
  return Promise.reject(error)
})

api.interceptors.response.use(res => {
  return res.data
}, error => {
  const msg = error.response?.data?.error || error.message || '请求失败'
  
  if (window.location.pathname.includes('/admin')) {
    ElMessage.error(msg)
  } else {
    showToast(msg)
  }

  if (error.response?.status === 401) {
    if (window.location.pathname.includes('/admin')) {
      localStorage.removeItem('adminToken')
      window.location.href = '/admin/login'
    } else {
      localStorage.removeItem('token')
      window.location.href = '/h5/login'
    }
  }
  
  return Promise.reject(error)
})

export default api