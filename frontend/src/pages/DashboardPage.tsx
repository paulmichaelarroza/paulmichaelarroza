import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, setToken } from '../services/api'
import { Dashboard } from '../types'

export const DashboardPage = () => {
  const [data, setData] = useState<Dashboard | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setToken(token)
      api.get('/dashboard').then((res) => setData(res.data))
    }
  }, [])

  if (!data) return <p>Loading dashboard...</p>

  const siteData = Object.entries(data.site_comparison).map(([site, score]) => ({ site, score }))

  return (
    <div>
      <h1>Executive Dashboard</h1>
      <section className="metrics-grid">
        <article><h3>Company KPI Score</h3><p>{data.company_score}%</p></article>
        <article><h3>Missed KPIs</h3><p>{data.missed_kpis}</p></article>
        <article><h3>Forecast Alerts</h3><p>{data.forecast_alerts.length}</p></article>
      </section>

      <div className="chart-card">
        <h3>Site Comparison</h3>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={siteData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="site" /><YAxis /><Tooltip /><Bar dataKey="score">{siteData.map((s) => <Cell key={s.site} fill={s.score >= 100 ? '#15803d' : s.score >= 90 ? '#eab308' : '#b91c1c'} />)}</Bar></BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <h3>Top KPI Achievements</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data.top_kpis}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="kpi_id" /><YAxis /><Tooltip /><Line type="monotone" dataKey="achievement" stroke="#2563eb" /></LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
