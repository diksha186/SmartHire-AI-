import { Link } from 'react-router-dom'
import SkillBadges from './SkillBadges'

export default function JobCard({ job, matchScore, matching = [], missing = [] }) {
  const score = matchScore ?? job.match_score
  return (
    <div className="card job-card h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h5 className="card-title mb-1">{job.title}</h5>
            <p className="text-muted mb-2 small">
              {job.company_name} &middot; {job.location || 'Not specified'} &middot; {job.employment_type}
            </p>
          </div>
          {score != null && (
            <span className={`badge fs-6 ${score >= 70 ? 'text-bg-success' : score >= 45 ? 'text-bg-info' : 'text-bg-secondary'}`}>
              {Math.round(score)}% match
            </span>
          )}
        </div>

        <p className="small mb-2">{(job.description || '').slice(0, 120)}...</p>

        <div className="mb-2">
          <SkillBadges skills={(job.required_skills || '').split(',').filter(Boolean)} variant="light" />
        </div>

        {matching.length > 0 && (
          <p className="small mb-1 text-success">Matching: {matching.join(', ')}</p>
        )}
        {missing.length > 0 && (
          <p className="small mb-1 text-danger">Missing: {missing.join(', ')}</p>
        )}

        <div className="d-flex justify-content-between align-items-center mt-3">
          <span className="small text-muted">{job.salary || 'Salary not disclosed'}</span>
          <Link className="btn btn-sm btn-primary" to={`/jobs/${job.id || job.job_id}`}>View details</Link>
        </div>
      </div>
    </div>
  )
}
