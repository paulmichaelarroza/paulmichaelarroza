import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export const api = axios.create({ baseURL: API_BASE })

export const setToken = (token: string) => {
  api.defaults.headers.common.Authorization = `Bearer ${token}`
}
