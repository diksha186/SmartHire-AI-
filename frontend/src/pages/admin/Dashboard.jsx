import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    adminApi.statistics()
      .then(({ data }) => setStats(data))
      .catch((err) => setError(errorMessage(err)))
  }, [])

  if (error) return <div className="container py-4"><div className="alert alert-danger">{error}</div></div>
  if (!stats) return <Loader />

  const cards = [
    ['Candidates', stats.total_candidates], ['Employers', stats.total_employers],
    ['Jobs', stats.total_jobs], ['Active jobs', stats.active_jobs],
    ['Applications', stats.total_applications],
    ['Selected', stats.applications_by_status['Selected'] || 0],
  ]

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">Admin dashboard</h3>

      <div className="row g-3 mb-4">
        {cards.map(([label, value]) => (
          <div className="col-6 col-lg-2" key={label}>
            <div className="card stat-card p-3 text-center">
              <h2>{value}</h2><span className="small text-muted">{label}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card p-3">
            <div className="d-flex justify-content-between mb-2">
              <h6 className="fw-bold mb-0">Recent registrations</h6>
              <Link className="btn btn-sm btn-outline-primary" to="/admin/users">Manage users</Link>
            </div>
            <table className="table table-sm mb-0">
              <thead><tr><th>Name</th><th>Role</th><th>Email</th></tr></thead>
              <tbody>
                {stats.recent_registrations.map((u) => (
                  <tr key={u.id}>
                    <td>{u.name}</td>
                    <td><span className="badge text-bg-secondary">{u.role}</span></td>
                    <td className="small">{u.email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card p-3">
            <div className="d-flex justify-content-between mb-2">
              <h6 className="fw-bold mb-0">Recent applications</h6>
              <Link className="btn btn-sm btn-outline-primary" to="/admin/applications">View all</Link>
            </div>
            <table className="table table-sm mb-0">
              <thead><tr><th>Candidate</th><th>Job</th><th>Status</th></tr></thead>
              <tbody>
                {stats.recent_applications.map((a) => (
                  <tr key={a.id}>
                    <td className="small">{a.candidate_name}</td>
                    <td className="small">{a.job_title}</td>
                    <td><span className="badge text-bg-info">{a.application_status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="col-12">
          <div className="card p-3">
            <h6 className="fw-bold">Applications by status</h6>
            {Object.entries(stats.applications_by_status).map(([s, c]) => (
              <div key={s} className="mb-2">
                <div className="d-flex justify-content-between small"><span>{s}</span><span>{c}</span></div>
                <div className="progress" style={{ height: '7px' }}>
                  <div className="progress-bar" style={{
                    width: `${stats.total_applications ? (c / stats.total_applications) * 100 : 0}%`,
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
