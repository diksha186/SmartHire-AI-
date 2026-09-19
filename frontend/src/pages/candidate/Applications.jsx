import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { applicationApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

const STATUS_COLOURS = {
  'Applied': 'secondary', 'Under Review': 'info', 'Shortlisted': 'primary',
  'Interview': 'warning', 'Rejected': 'danger', 'Selected': 'success',
}

export default function Applications() {
  const [apps, setApps] = useState([])
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    applicationApi.mine()
      .then(({ data }) => setApps(data))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const withdraw = async (id) => {
    if (!window.confirm('Withdraw this application?')) return
    try {
      await applicationApi.withdraw(id)
      setApps(apps.filter((a) => a.id !== id))
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (loading) return <Loader />

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">My applications</h3>
      {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}

      {apps.length === 0 ? (
        <div className="card p-5 text-center text-muted">
          <p>You have not applied to any job yet.</p>
          <Link className="btn btn-primary btn-sm mx-auto" to="/jobs">Browse jobs</Link>
        </div>
      ) : (
        <div className="card p-0">
          <table className="table table-hover align-middle mb-0">
            <thead className="table-light">
              <tr>
                <th>Job</th><th>Company</th><th>Match</th><th>Status</th><th>Applied on</th><th></th>
              </tr>
            </thead>
            <tbody>
              {apps.map((a) => (
                <tr key={a.id}>
                  <td><Link to={`/jobs/${a.job_id}`}>{a.job_title}</Link></td>
                  <td className="small">{a.company_name}</td>
                  <td>{a.match_score != null ? `${Math.round(a.match_score)}%` : '--'}</td>
                  <td>
                    <span className={`badge text-bg-${STATUS_COLOURS[a.application_status] || 'secondary'}`}>
                      {a.application_status}
                    </span>
                  </td>
                  <td className="small">{new Date(a.applied_at).toLocaleDateString()}</td>
                  <td>
                    <button className="btn btn-sm btn-outline-danger" onClick={() => withdraw(a.id)}>
                      Withdraw
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
