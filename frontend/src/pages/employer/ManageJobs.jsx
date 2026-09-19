import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { employerApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function ManageJobs() {
  const [jobs, setJobs] = useState([])
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    employerApi.myJobs()
      .then(({ data }) => setJobs(data))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const remove = async (id) => {
    if (!window.confirm('Delete this job and all its applications?')) return
    try {
      await employerApi.deleteJob(id)
      setJobs(jobs.filter((j) => j.id !== id))
      setMessage({ type: 'success', text: 'Job deleted.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  const close = async (id) => {
    try {
      await employerApi.closeJob(id)
      load()
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (loading) return <Loader />

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="fw-bold mb-0">Manage jobs</h3>
        <Link className="btn btn-primary" to="/employer/jobs/new">Post a new job</Link>
      </div>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}

      <div className="card p-0">
        <table className="table table-hover align-middle mb-0">
          <thead className="table-light">
            <tr><th>Title</th><th>Location</th><th>Type</th><th>Applicants</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id}>
                <td><Link to={`/jobs/${j.id}`}>{j.title}</Link></td>
                <td className="small">{j.location || '--'}</td>
                <td className="small">{j.employment_type}</td>
                <td>{j.applicant_count}</td>
                <td>
                  <span className={`badge text-bg-${j.is_active ? 'success' : 'secondary'}`}>
                    {j.is_active ? 'Open' : 'Closed'}
                  </span>
                </td>
                <td className="text-nowrap">
                  <Link className="btn btn-sm btn-outline-primary me-1"
                        to={`/employer/jobs/${j.id}/applicants`}>Applicants</Link>
                  <Link className="btn btn-sm btn-outline-secondary me-1"
                        to={`/employer/jobs/${j.id}/edit`}>Edit</Link>
                  {j.is_active === 1 && (
                    <button className="btn btn-sm btn-outline-warning me-1" onClick={() => close(j.id)}>Close</button>
                  )}
                  <button className="btn btn-sm btn-outline-danger" onClick={() => remove(j.id)}>Delete</button>
                </td>
              </tr>
            ))}
            {jobs.length === 0 && <tr><td colSpan="6" className="text-muted small">No jobs yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
