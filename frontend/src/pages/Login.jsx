import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth, homeForRole } from '../context/AuthContext'
import { errorMessage } from '../services/api'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      const user = await login(form.email, form.password)
      navigate(homeForRole(user.role))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container py-5" style={{ maxWidth: '440px' }}>
      <div className="card p-4">
        <h4 className="fw-bold mb-3">Login to SmartHire AI</h4>
        {error && <div className="alert alert-danger py-2 small">{error}</div>}
        <form onSubmit={submit}>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Email</label>
            <input className="form-control" type="email" name="email" value={form.email}
                   onChange={change} required />
          </div>
          <div className="mb-3">
            <label className="form-label small fw-semibold">Password</label>
            <input className="form-control" type="password" name="password" value={form.password}
                   onChange={change} required />
          </div>
          <button className="btn btn-primary w-100" disabled={busy}>
            {busy ? 'Signing in...' : 'Login'}
          </button>
        </form>
        <p className="small text-center mt-3 mb-0">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  )
}
