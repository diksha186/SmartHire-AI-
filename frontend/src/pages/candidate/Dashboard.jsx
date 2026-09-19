import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { candidateApi, errorMessage } from '../../services/api'
import JobCard from '../../components/JobCard'
import SkillBadges from '../../components/SkillBadges'
import Loader from '../../components/Loader'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    candidateApi.dashboard()
      .then(({ data }) => setData(data))
      .catch((err) => setError(errorMessage(err)))
  }, [])

  if (error) return <div className="container py-4"><div className="alert alert-danger">{error}</div></div>
  if (!data) return <Loader text="Loading your dashboard..." />

  return (
    <div className="container py-4">
      <h3 className="fw-bold">Welcome back, {data.name}</h3>
      <p className="text-muted">Here is your hiring snapshot.</p>

      <div className="row g-3 mb-4">
        <div className="col-6 col-lg-3">
          <div className="card stat-card p-3 text-center">
            <h2>{data.resume_score != null ? Math.round(data.resume_score) : '--'}</h2>
            <span className="small text-muted">Resume score / 100</span>
          </div>
        </div>
        <div className="col-6 col-lg-3">
          <div className="card stat-card p-3 text-center">
            <h2>{data.profile_completion}%</h2>
            <span className="small text-muted">Profile completion</span>
          </div>
        </div>
        <div className="col-6 col-lg-3">
          <div className="card stat-card p-3 text-center">
            <h2>{data.total_applications}</h2>
            <span className="small text-muted">Applications sent</span>
          </div>
        </div>
        <div className="col-6 col-lg-3">
          <div className="card stat-card p-3 text-center">
            <h2>{data.skills.length}</h2>
            <span className="small text-muted">Skills detected</span>
          </div>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-lg-8">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <h5 className="fw-bold mb-0">Recommended for you</h5>
            <Link className="btn btn-sm btn-outline-primary" to="/candidate/recommendations">See all</Link>
          </div>
          <div className="row g-3">
            {data.top_recommendations.length === 0 && (
              <p className="text-muted small">
                Upload your resume to unlock AI job recommendations.
              </p>
            )}
            {data.top_recommendations.map((rec) => (
              <div className="col-md-6" key={rec.job_id}>
                <JobCard job={{ ...rec, id: rec.job_id, required_skills: rec.matching_skills.join(',') }}
                         matchScore={rec.match_score} matching={rec.matching_skills}
                         missing={rec.missing_skills} />
              </div>
            ))}
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card p-3 mb-3">
            <h6 className="fw-bold">Application status</h6>
            {Object.keys(data.status_counts).length === 0 && (
              <p className="small text-muted mb-0">No applications yet.</p>
            )}
            {Object.entries(data.status_counts).map(([status, count]) => (
              <div className="d-flex justify-content-between small py-1" key={status}>
                <span>{status}</span><span className="badge text-bg-primary">{count}</span>
              </div>
            ))}
          </div>

          <div className="card p-3 mb-3">
            <h6 className="fw-bold">Your skills</h6>
            <SkillBadges skills={data.skills} empty="No skills yet" />
          </div>

          <div className="card p-3">
            <h6 className="fw-bold">Quick actions</h6>
            <Link className="btn btn-sm btn-primary mb-2" to="/candidate/resume">Upload / analyse resume</Link>
            <Link className="btn btn-sm btn-outline-primary mb-2" to="/candidate/profile">Edit profile</Link>
            <Link className="btn btn-sm btn-outline-secondary" to="/jobs">Browse all jobs</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
