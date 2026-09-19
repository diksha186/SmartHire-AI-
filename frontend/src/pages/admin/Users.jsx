import { useEffect, useState } from 'react'
import { adminApi, errorMessage } from '../../services/api'
import Loader from '../../components/Loader'

export default function Users() {
  const [users, setUsers] = useState([])
  const [role, setRole] = useState('')
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = (selectedRole = role) => {
    setLoading(true)
    adminApi.users(selectedRole || undefined)
      .then(({ data }) => setUsers(data))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load('') }, [])

  const toggle = async (id) => {
    try {
      const { data } = await adminApi.toggleUser(id)
      setUsers(users.map((u) => (u.id === id ? data : u)))
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  const remove = async (id) => {
    if (!window.confirm('Permanently delete this account and all its data?')) return
    try {
      await adminApi.deleteUser(id)
      setUsers(users.filter((u) => u.id !== id))
      setMessage({ type: 'success', text: 'Account deleted.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="fw-bold mb-0">Users</h3>
        <select className="form-select w-auto" value={role}
                onChange={(e) => { setRole(e.target.value); load(e.target.value) }}>
          <option value="">All roles</option>
          <option value="candidate">Candidates</option>
          <option value="employer">Employers</option>
          <option value="admin">Admins</option>
        </select>
      </div>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}

      {loading ? <Loader /> : (
        <div className="card p-0">
          <table className="table table-hover align-middle mb-0">
            <thead className="table-light">
              <tr><th>Name</th><th>Email</th><th>Role</th><th>Company</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.name}</td>
                  <td className="small">{u.email}</td>
                  <td><span className="badge text-bg-secondary">{u.role}</span></td>
                  <td className="small">{u.company_name || '--'}</td>
                  <td>
                    <span className={`badge text-bg-${u.is_active ? 'success' : 'danger'}`}>
                      {u.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="text-nowrap">
                    {u.role !== 'admin' && (
                      <>
                        <button className="btn btn-sm btn-outline-warning me-1" onClick={() => toggle(u.id)}>
                          {u.is_active ? 'Disable' : 'Enable'}
                        </button>
                        <button className="btn btn-sm btn-outline-danger" onClick={() => remove(u.id)}>
                          Delete
                        </button>
                      </>
                    )}
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
