import { useEffect, useState } from 'react'
import { candidateApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Profile() {
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    candidateApi.getProfile()
      .then(({ data }) => setForm({
        name: data.name || '', phone: data.phone || '', education: data.education || '',
        location: data.location || '', skills: data.skills || '',
        experience: data.experience ?? 0, certifications: data.certifications || '',
        bio: data.bio || '', profile_completion: data.profile_completion,
      }))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
  }, [])

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setMessage(null)
    try {
      const payload = { ...form, experience: parseFloat(form.experience) || 0 }
      delete payload.profile_completion
      const { data } = await candidateApi.updateProfile(payload)
      setForm({ ...form, profile_completion: data.profile_completion })
      setMessage({ type: 'success', text: 'Profile updated. Your recommendations have been refreshed.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    } finally {
      setBusy(false)
    }
  }

  if (!form) return <Loader />

  return (
    <div className="container py-4" style={{ maxWidth: '800px' }}>
      <h3 className="fw-bold mb-1">My profile</h3>
      <div className="progress mb-3" style={{ height: '8px' }}>
        <div className="progress-bar bg-success" style={{ width: `${form.profile_completion}%` }} />
      </div>
      <p className="small text-muted">Profile completion: {form.profile_completion}%</p>

      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}

      <form className="card p-4" onSubmit={submit}>
        <div className="row g-3">
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Full name</label>
            <input className="form-control" name="name" value={form.name} onChange={change} />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Phone</label>
            <input className="form-control" name="phone" value={form.phone} onChange={change} />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Highest education</label>
            <input className="form-control" name="education" value={form.education}
                   onChange={change} placeholder="BCA / MCA / B.Tech" />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Location</label>
            <input className="form-control" name="location" value={form.location}
                   onChange={change} placeholder="Bulandshahr, Uttar Pradesh" />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Experience (years)</label>
            <input className="form-control" type="number" step="0.5" min="0" name="experience"
                   value={form.experience} onChange={change} />
          </div>
          <div className="col-md-6">
            <label className="form-label small fw-semibold">Certifications</label>
            <input className="form-control" name="certifications" value={form.certifications}
                   onChange={change} placeholder="Comma separated" />
          </div>
          <div className="col-12">
            <label className="form-label small fw-semibold">Skills (comma separated)</label>
            <textarea className="form-control" rows="2" name="skills" value={form.skills}
                      onChange={change} placeholder="python, sql, react, git" />
            <div className="form-text">These drive your match scores. Uploading a resume fills them automatically.</div>
          </div>
          <div className="col-12">
            <label className="form-label small fw-semibold">Bio</label>
            <textarea className="form-control" rows="3" name="bio" value={form.bio} onChange={change} />
          </div>
        </div>
        <button className="btn btn-primary mt-3" disabled={busy}>
          {busy ? 'Saving...' : 'Save profile'}
        </button>
      </form>
    </div>
  )
}
