export type Dashboard = {
  company_score: number
  site_comparison: Record<string, number>
  missed_kpis: number
  top_kpis: { kpi_id: number; achievement: number }[]
  forecast_alerts: { kpi_id: number; forecast: number; target: number }[]
}

export type Project = {
  id: number
  project_name: string
  owner_id: number
  department_id: number
  site_id: number
  start_date: string
  end_date: string
  progress_percentage: number
  status: string
}
