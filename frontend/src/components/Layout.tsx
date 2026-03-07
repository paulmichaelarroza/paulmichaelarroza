import { Link, Outlet } from 'react-router-dom'

export const Layout = () => (
  <div className="layout">
    <aside className="sidebar">
      <h2>Enterprise KPI Tracker</h2>
      <nav>
        <Link to="/">Executive Dashboard</Link>
        <Link to="/kpi-entry">KPI Encoding</Link>
        <Link to="/projects">Project Monitoring</Link>
      </nav>
    </aside>
    <main className="content">
      <Outlet />
    </main>
  </div>
)
