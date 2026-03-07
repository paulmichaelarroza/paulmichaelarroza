import { useEffect, useState } from 'react'
import { api, setToken } from '../services/api'
import { Project } from '../types'

export const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setToken(token)
      api.get('/projects').then((res) => setProjects(res.data))
    }
  }, [])

  return (
    <div>
      <h1>Project Monitoring</h1>
      <table className="card">
        <thead>
          <tr><th>Project</th><th>Site</th><th>Progress</th><th>Status</th><th>End Date</th></tr>
        </thead>
        <tbody>
          {projects.map((project) => (
            <tr key={project.id}>
              <td>{project.project_name}</td>
              <td>{project.site_id}</td>
              <td>{project.progress_percentage}%</td>
              <td>{project.status}</td>
              <td>{project.end_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
