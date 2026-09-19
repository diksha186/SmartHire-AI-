import { useEffect, useState } from 'react'
import { employerApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function CompanyProfile() {
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    employerApi.getCompany()
      .then(({ data }) => setForm({
        company_name: data.company_name || '', description: data.description || '',
        website: data.website || '', location: data.location || '', industry: data.industry || '',
      }))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
  }, [])

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    try {
      await employerApi.updateCompany(form)
      setMessage({ type: 'success', text: 'Company profile saved.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (!form) return <Loader />

  return (
    <div className="container py-4" style={{ maxWidth: '760px' }}>
      <h3 className="fw-bold mb-3">Company profile</h3>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}
      <form className="card p-4" onSubmit={submit}>
        <div className="row g-3">
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Company name</label>
            <input className="form-control" name="company_name" value={form.company_name} onChange={change} required />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Industry</label>
            <input className="form-control" name="industry" value={form.industry} onChange={change} />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Location</label>
            <input className="form-control" name="location" value={form.location} onChange={change} />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Website</label>
            <input className="form-control" name="website" value={form.website} onChange={change} />
          </div>
          <div className="col-12">
            <label className="form-label small fw-semibold">About the company</label>
            <textarea className="form-control" rows="4" name="description" value={form.description} onChange={change} />
          </div>
        </div>
        <button className="btn btn-primary mt-3">Save</button>
      </form>
    </div>
  )
}
