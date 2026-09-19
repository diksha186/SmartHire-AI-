import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Jobs() {
  const [jobs, setJobs] = useState([])
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminApi.jobs()
      .then(({ data }) => setJobs(data))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
      .finally(() => setLoading(false))
  }, [])

  const remove = async (id) => {
    if (!window.confirm('Remove this job posting?')) return
    try {
      await adminApi.deleteJob(id)
      setJobs(jobs.filter((j) => j.id !== id))
      setMessage({ type: 'success', text: 'Job removed.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (loading) return <Loader />

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">All job postings</h3>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}
      <div className="card p-0">
        <table className="table table-hover align-middle mb-0">
          <thead className="table-light">
            <tr><th>Title</th><th>Company</th><th>Location</th><th>Applicants</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id}>
                <td><Link to={`/jobs/${j.id}`}>{j.title}</Link></td>
                <td className="small">{j.company_name}</td>
                <td className="small">{j.location || '--'}</td>
                <td>{j.applicant_count}</td>
                <td>
                  <span className={`badge text-bg-${j.is_active ? 'success' : 'secondary'}`}>
                    {j.is_active ? 'Open' : 'Closed'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => remove(j.id)}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
