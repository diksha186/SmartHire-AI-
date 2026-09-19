import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="container text-center py-5">
      <h1 className="display-4 fw-bold">404</h1>
      <p className="text-muted">The page you are looking for does not exist.</p>
      <Link className="btn btn-primary" to="/">Back to home</Link>
    </div>
  )
}
