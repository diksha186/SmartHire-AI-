import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth, homeForRole } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark navbar-smarthire sticky-top shadow-sm">
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/">SmartHire<span className="text-warning"> AI</span></Link>
        <button className="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navmenu">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navmenu">
          <ul className="navbar-nav me-auto">
            <li className="nav-item"><NavLink className="nav-link" to="/">Home</NavLink></li>
            <li className="nav-item"><NavLink className="nav-link" to="/jobs">Jobs</NavLink></li>
            <li className="nav-item"><NavLink className="nav-link" to="/about">About</NavLink></li>
            {user?.role === 'candidate' && (
              <>
                <li className="nav-item"><NavLink className="nav-link" to="/candidate">Dashboard</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/candidate/resume">Resume AI</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/candidate/applications">Applications</NavLink></li>
              </>
            )}
            {user?.role === 'employer' && (
              <>
                <li className="nav-item"><NavLink className="nav-link" to="/employer">Dashboard</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/employer/jobs">My Jobs</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/employer/jobs/new">Post Job</NavLink></li>
              </>
            )}
            {user?.role === 'admin' && (
              <>
                <li className="nav-item"><NavLink className="nav-link" to="/admin">Dashboard</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/admin/users">Users</NavLink></li>
                <li className="nav-item"><NavLink className="nav-link" to="/admin/jobs">Jobs</NavLink></li>
              </>
            )}
          </ul>
          <ul className="navbar-nav">
            {user ? (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to={homeForRole(user.role)}>
                    <span className="badge bg-light text-dark me-1">{user.role}</span>{user.name}
                  </Link>
                </li>
                <li className="nav-item">
                  <button className="btn btn-outline-light btn-sm ms-2" onClick={handleLogout}>Logout</button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item"><NavLink className="nav-link" to="/login">Login</NavLink></li>
                <li className="nav-item">
                  <Link className="btn btn-warning btn-sm ms-2 fw-semibold" to="/register">Register</Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  )
}
