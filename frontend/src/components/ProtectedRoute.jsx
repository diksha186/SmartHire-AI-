import { Navigate, useLocation } from 'react-router-dom'
import { useAuth, homeForRole } from '../context/AuthContext'

/**
 * Route guard: blocks unauthenticated users and enforces role based access
 * on the frontend. (The backend enforces it again - never trust the client.)
 */
export default function ProtectedRoute({ allow, children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <div className="text-center py-5">Loading...</div>
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (allow && !allow.includes(user.role)) return <Navigate to={homeForRole(user.role)} replace />
  return children
}
