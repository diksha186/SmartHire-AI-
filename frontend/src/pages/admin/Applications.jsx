import { useEffect, useState } from 'react'
import { adminApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Applications() {
  const [apps, setApps] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.applications()
      .then(({ data }) => setApps(data))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loader />

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">All applications</h3>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="card p-0">
        <table className="table table-hover align-middle mb-0">
          <thead className="table-light">
            <tr><th>#</th><th>Candidate</th><th>Job</th><th>Company</th><th>Match</th><th>Status</th><th>Date</th></tr>
          </thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.id}>
                <td className="small">{a.id}</td>
                <td>{a.candidate_name}</td>
                <td className="small">{a.job_title}</td>
                <td className="small">{a.company_name}</td>
                <td>{a.match_score != null ? `${Math.round(a.match_score)}%` : '--'}</td>
                <td><span className="badge text-bg-info">{a.application_status}</span></td>
                <td className="small">{new Date(a.applied_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {apps.length === 0 && <tr><td colSpan="7" className="text-muted small">No applications yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
