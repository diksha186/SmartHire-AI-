import { useEffect, useState } from 'react'
import { jobApi, errorMessage } from '../services/api'
import JobCard from '../components/JobCard'
import Loader from '../components/Loader'

const EMPTY = { q: '', location: '', employment_type: '', skill: '', min_experience: '' }

export default function Jobs() {
  const [filters, setFilters] = useState(EMPTY)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async (params = filters) => {
    setLoading(true); setError('')
    try {
      const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== ''))
      const { data } = await jobApi.list(clean)
      setJobs(data)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(EMPTY) }, [])

  const change = (e) => setFilters({ ...filters, [e.target.name]: e.target.value })

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">Browse jobs</h3>

      <div className="card p-3 mb-4">
        <form className="row g-2" onSubmit={(e) => { e.preventDefault(); load() }}>
          <div className="col-md-3">
            <input className="form-control" name="q" placeholder="Job title or keyword"
                   value={filters.q} onChange={change} />
          </div>
          <div className="col-md-2">
            <input className="form-control" name="location" placeholder="Location"
                   value={filters.location} onChange={change} />
          </div>
          <div className="col-md-2">
            <input className="form-control" name="skill" placeholder="Skill"
                   value={filters.skill} onChange={change} />
          </div>
          <div className="col-md-2">
            <select className="form-select" name="employment_type" value={filters.employment_type} onChange={change}>
              <option value="">Any type</option>
              <option>Full-time</option>
              <option>Part-time</option>
              <option>Internship</option>
              <option>Contract</option>
            </select>
          </div>
          <div className="col-md-2">
            <input className="form-control" type="number" step="0.5" min="0" name="min_experience"
                   placeholder="Min exp (yrs)" value={filters.min_experience} onChange={change} />
          </div>
          <div className="col-md-1 d-grid">
            <button className="btn btn-primary">Search</button>
          </div>
        </form>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {loading ? <Loader /> : (
        <div className="row g-4">
          {jobs.length === 0 && <p className="text-muted">No jobs match your filters.</p>}
          {jobs.map((job) => (
            <div className="col-md-6 col-lg-4" key={job.id}><JobCard job={job} /></div>
          ))}
        </div>
      )}
    </div>
  )
}
