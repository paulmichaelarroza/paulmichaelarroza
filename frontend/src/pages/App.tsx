import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { DashboardPage } from './DashboardPage'
import { KPIEntryPage } from './KPIEntryPage'
import { LoginPage } from './LoginPage'
import { ProjectsPage } from './ProjectsPage'

const hasToken = () => !!localStorage.getItem('token')

export const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route
      path="/"
      element={hasToken() ? <Layout /> : <Navigate to="/login" replace />}
    >
      <Route index element={<DashboardPage />} />
      <Route path="kpi-entry" element={<KPIEntryPage />} />
      <Route path="projects" element={<ProjectsPage />} />
    </Route>
  </Routes>
)
