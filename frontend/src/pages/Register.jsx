import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth, homeForRole } from '../context/AuthContext'
import { errorMessage } from '../services/api'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', email: '', password: '', phone: '', role: 'candidate', company_name: '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      const payload = { ...form }
      if (payload.role !== 'employer') delete payload.company_name
      const user = await register(payload)
      navigate(homeForRole(user.role))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '520px' }}>
      <div className="card p-4">
        <h4 className="fw-bold mb-3">Create your account</h4>
        {error && <div className="alert alert-danger py-2 small">{error}</div>}
        <form onSubmit={submit}>
          <div className="mb-3">
            <label className="form-label small fw-semibold">I am a</label>
            <select className="form-select" name="role" value={form.role} onChange={change}>
              <option value="candidate">Candidate / Student</option>
              <option value="employer">Employer / Company</option>
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Full name</label>
            <input className="form-control" name="name" value={form.name} onChange={change} required />
          </div>
          {form.role === 'employer' && (
            <div className="mb-3">
              <label className="form-label small fw-semibold">Company name</label>
              <input className="form-control" name="company_name" value={form.company_name}
                     onChange={change} required />
            </div>
          )}
          <div className="mb-3">
            <label className="form-label small fw-semibold">Email</label>
            <input className="form-control" type="email" name="email" value={form.email}
                   onChange={change} required />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Phone</label>
            <input className="form-control" name="phone" value={form.phone} onChange={change} />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Password</label>
            <input className="form-control" type="password" name="password" value={form.password}
                   onChange={change} minLength={6} required />
            <div className="form-text">Minimum 6 characters. Stored only as a bcrypt hash.</div>
          </div>
          <button className="btn btn-primary w-100" disabled={busy}>
            {busy ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <p className="small text-center mt-3 mb-0">
          Already registered? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
