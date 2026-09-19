import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { employerApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    employerApi.dashboard()
      .then(({ data }) => setData(data))
      .catch((err) => setError(errorMessage(err)))
  }, [])

  if (error) return <div className="container py-4"><div className="alert alert-danger">{error}</div></div>
  if (!data) return <Loader />

  return (
    <div className="container py-4">
      <h3 className="fw-bold">{data.company_name}</h3>
      <p className="text-muted">Recruitment overview</p>

      <div className="row g-3 mb-4">
        {[['Total jobs', data.total_jobs], ['Active jobs', data.active_jobs],
          ['Applications', data.total_applications],
          ['Shortlisted', data.status_counts['Shortlisted'] || 0]].map(([label, value]) => (
          <div className="col-6 col-lg-3" key={label}>
            <div className="card stat-card p-3 text-center">
              <h2>{value}</h2><span className="small text-muted">{label}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="row g-4">
        <div className="col-lg-8">
          <div className="card p-3">
            <div className="d-flex justify-content-between mb-2">
              <h6 className="fw-bold mb-0">Recent job postings</h6>
              <Link className="btn btn-sm btn-primary" to="/employer/jobs/new">Post a new job</Link>
            </div>
            <table className="table table-sm align-middle mb-0">
              <thead><tr><th>Title</th><th>Status</th><th>Applicants</th><th></th></tr></thead>
              <tbody>
                {data.recent_jobs.map((j) => (
                  <tr key={j.id}>
                    <td>{j.title}</td>
                    <td><span className={`badge text-bg-${j.is_active ? 'success' : 'secondary'}`}>
                      {j.is_active ? 'Open' : 'Closed'}</span></td>
                    <td>{j.applicants}</td>
                    <td>
                      <Link className="btn btn-sm btn-outline-primary"
                            to={`/employer/jobs/${j.id}/applicants`}>Ranked applicants</Link>
                    </td>
                  </tr>
                ))}
                {data.recent_jobs.length === 0 && (
                  <tr><td colSpan="4" className="text-muted small">No jobs posted yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
        <div className="col-lg-4">
          <div className="card p-3">
            <h6 className="fw-bold">Applications by status</h6>
            {Object.keys(data.status_counts).length === 0 && (
              <p className="small text-muted mb-0">No applications yet.</p>
            )}
            {Object.entries(data.status_counts).map(([s, c]) => (
              <div className="d-flex justify-content-between small py-1" key={s}>
                <span>{s}</span><span className="badge text-bg-primary">{c}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
