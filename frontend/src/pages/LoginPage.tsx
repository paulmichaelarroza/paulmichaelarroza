import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '../services/api'

export const LoginPage = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@kpi.local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    try {
      const response = await api.post('/auth/login', { email, password })
      localStorage.setItem('token', response.data.access_token)
      setToken(response.data.access_token)
      navigate('/')
    } catch {
      setError('Login failed.')
    }
  }

  return (
    <div className="login-card">
      <h1>KPI Tracker Login</h1>
      <p>Email/Password, Google OAuth, and Microsoft OAuth are supported by API.</p>
      <form onSubmit={onSubmit}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Sign In</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
