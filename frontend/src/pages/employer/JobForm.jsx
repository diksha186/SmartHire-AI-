import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { employerApi, jobApi, errorMessage } from '../../services/api'

const BLANK = {
  title: '', description: '', required_skills: '', preferred_skills: '',
  experience_required: 0, education_required: '', location: '',
  employment_type: 'Full-time', salary: '', deadline: '',
}

/** One component handles both "Post a job" and "Edit job". */
export default function JobForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(BLANK)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!id) return
    jobApi.details(id).then(({ data }) => setForm({
      title: data.title, description: data.description,
      required_skills: data.required_skills, preferred_skills: data.preferred_skills || '',
      experience_required: data.experience_required, education_required: data.education_required || '',
      location: data.location || '', employment_type: data.employment_type || 'Full-time',
      salary: data.salary || '', deadline: data.deadline ? data.deadline.slice(0, 10) : '',
    })).catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
  }, [id])

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setMessage(null)
    try {
      const payload = {
        ...form,
        experience_required: parseFloat(form.experience_required) || 0,
        deadline: form.deadline ? `${form.deadline}T23:59:59` : null,
      }
      if (id) await employerApi.updateJob(id, payload)
      else await employerApi.createJob(payload)
      navigate('/employer/jobs')
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container py-4" style={{ maxWidth: '860px' }}>
      <h3 className="fw-bold mb-3">{id ? 'Edit job' : 'Post a new job'}</h3>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}
      <form className="card p-4" onSubmit={submit}>
        <div className="row g-3">
          <div className="col-md-8">
            <label className="form-label small fw-semibold">Job title</label>
            <input className="form-control" name="title" value={form.title} onChange={change} required />
          </div>
          <div className="col-md-4">
            <label className="form-label small fw-semibold">Employment type</label>
            <select className="form-select" name="employment_type" value={form.employment_type} onChange={change}>
              <option>Full-time</option><option>Part-time</option>
              <option>Internship</option><option>Contract</option>
            </select>
          </div>
          <div className="col-12">
            <label className="form-label small fw-semibold">Description</label>
            <textarea className="form-control" rows="4" name="description" value={form.description}
                      onChange={change} minLength={10} required />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Required skills (comma separated)</label>
            <input className="form-control" name="required_skills" value={form.required_skills}
                   onChange={change} placeholder="python, fastapi, sql" required />
            <div className="form-text">These drive the AI candidate ranking.</div>
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Preferred skills</label>
            <input className="form-control" name="preferred_skills" value={form.preferred_skills}
                   onChange={change} placeholder="docker, aws" />
          </div>
          <div className="col-md-3">
            <label className="form-label small fw-semibold">Experience (years)</label>
            <input className="form-control" type="number" step="0.5" min="0" name="experience_required"
                   value={form.experience_required} onChange={change} />
          </div>
          <div className="col-md-3">
            <label className="form-label small fw-semibold">Education</label>
            <input className="form-control" name="education_required" value={form.education_required}
                   onChange={change} placeholder="BCA" />
          </div>
          <div className="col-md-3">
            <label className="form-label small fw-semibold">Location</label>
            <input className="form-control" name="location" value={form.location} onChange={change} />
          </div>
          <div className="col-md-3">
            <label className="form-label small fw-semibold">Salary</label>
            <input className="form-control" name="salary" value={form.salary}
                   onChange={change} placeholder="4-6 LPA" />
          </div>
          <div className="col-md-4">
            <label className="form-label small fw-semibold">Application deadline</label>
            <input className="form-control" type="date" name="deadline" value={form.deadline} onChange={change} />
          </div>
        </div>
        <button className="btn btn-primary mt-3" disabled={busy}>
          {busy ? 'Saving...' : id ? 'Update job' : 'Publish job'}
        </button>
      </form>
    </div>
  )
}
