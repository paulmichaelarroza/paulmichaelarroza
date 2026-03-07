import { FormEvent, useState } from 'react'
import { api, setToken } from '../services/api'

export const KPIEntryPage = () => {
  const [kpiId, setKpiId] = useState(1)
  const [year, setYear] = useState(2026)
  const [month, setMonth] = useState(5)
  const [actualValue, setActualValue] = useState(95)
  const [result, setResult] = useState<string>('')

  const submitKpi = async (event: FormEvent) => {
    event.preventDefault()
    const token = localStorage.getItem('token')
    if (token) setToken(token)
    const res = await api.post('/kpi/update', { kpi_id: kpiId, year, month, actual_value: actualValue })
    setResult(`Status: ${res.data.status} | Achievement: ${res.data.achievement_percentage}%`)
  }

  const uploadFile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = event.currentTarget
    const input = form.elements.namedItem('file') as HTMLInputElement
    if (!input.files?.length) return
    const body = new FormData()
    body.append('file', input.files[0])
    const token = localStorage.getItem('token')
    if (token) setToken(token)
    const res = await api.post('/kpi/upload', body)
    setResult(`Bulk import success: ${res.data.created} rows created.`)
  }

  return (
    <div>
      <h1>Raw KPI Data Encoding</h1>
      <form onSubmit={submitKpi} className="card form-grid">
        <input type="number" value={kpiId} onChange={(e) => setKpiId(Number(e.target.value))} placeholder="KPI ID" />
        <input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} placeholder="Year" />
        <input type="number" value={month} onChange={(e) => setMonth(Number(e.target.value))} placeholder="Month" />
        <input type="number" value={actualValue} onChange={(e) => setActualValue(Number(e.target.value))} placeholder="Actual Value" />
        <button type="submit">Submit KPI</button>
      </form>

      <form onSubmit={uploadFile} className="card">
        <h3>CSV / Excel Bulk Upload</h3>
        <input name="file" type="file" accept=".csv,.xlsx,.xls" />
        <button type="submit">Upload</button>
      </form>

      {result && <p>{result}</p>}
    </div>
  )
}
