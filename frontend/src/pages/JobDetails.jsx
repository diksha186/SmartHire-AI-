import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { jobApi, errorMessage } from '../services/api'
import { useAuth } from '../context/AuthContext'
import ScoreBar from '../components/ScoreBar'
import SkillBadges from '../components/SkillBadges'
import Loader from '../components/Loader'

export default function JobDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [job, setJob] = useState(null)
  const [match, setMatch] = useState(null)
  const [note, setNote] = useState('')
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await jobApi.details(id)
        setJob(data)
        if (user?.role === 'candidate') {
          try {
            const res = await jobApi.myMatch(id)
            setMatch(res.data)
          } catch { /* candidate has no profile data yet */ }
        }
      } catch (err) {
        setMessage({ type: 'danger', text: errorMessage(err) })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id, user])

  const apply = async () => {
    try {
      await jobApi.apply(id, { cover_note: note })
      setMessage({ type: 'success', text: 'Application submitted! Track it under Applications.' })
      setTimeout(() => navigate('/candidate/applications'), 1200)
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (loading) return <Loader />
  if (!job) return <div className="container py-5"><div className="alert alert-danger">Job not found.</div></div>

  return (
    <div className="container py-4">
      {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}
      <div className="row g-4">
        <div className="col-lg-8">
          <div className="card p-4">
            <h3 className="fw-bold mb-1">{job.title}</h3>
            <p className="text-muted">
              {job.company_name} &middot; {job.location || 'Not specified'} &middot; {job.employment_type}
              {job.salary && <> &middot; {job.salary}</>}
            </p>
            <hr />
            <h6 className="fw-bold">Job description</h6>
            <p style={{ whiteSpace: 'pre-line' }}>{job.description}</p>

            <h6 className="fw-bold mt-3">Required skills</h6>
            <SkillBadges skills={(job.required_skills || '').split(',').filter(Boolean)} />

            <h6 className="fw-bold mt-3">Preferred skills</h6>
            <SkillBadges skills={(job.preferred_skills || '').split(',').filter(Boolean)} variant="secondary" />

            <div className="row mt-4 small">
              <div className="col-6 col-md-3"><strong>Experience</strong><br />{job.experience_required} yrs</div>
              <div className="col-6 col-md-3"><strong>Education</strong><br />{job.education_required || 'Any'}</div>
              <div className="col-6 col-md-3"><strong>Applicants</strong><br />{job.applicant_count ?? 0}</div>
              <div className="col-6 col-md-3"><strong>Status</strong><br />{job.is_active ? 'Open' : 'Closed'}</div>
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          {user?.role === 'candidate' ? (
            <div className="card p-4">
              <h6 className="fw-bold">Your AI match score</h6>
              {match ? (
                <>
                  <div className="text-center my-3">
                    <div className="score-circle mx-auto">{Math.round(match.match_score)}%</div>
                  </div>
                  <ScoreBar label="Skills" value={match.skill_score} weight="50%" />
                  <ScoreBar label="Experience" value={match.experience_score} weight="20%" />
                  <ScoreBar label="Education" value={match.education_score} weight="10%" />
                  <ScoreBar label="Relevance" value={match.keyword_score} weight="20%" />
                  <p className="small mb-1 text-success">
                    Matching: {match.matching_skills.join(', ') || 'none yet'}
                  </p>
                  <p className="small text-danger">
                    Missing: {match.missing_skills.join(', ') || 'none'}
                  </p>
                  <textarea className="form-control mb-2" rows="3" placeholder="Optional cover note"
                            value={note} onChange={(e) => setNote(e.target.value)} />
                  <button className="btn btn-primary w-100" onClick={apply}>Apply now</button>
                </>
              ) : (
                <p className="small text-muted">
                  Add skills or <Link to="/candidate/resume">upload your resume</Link> to see your match score.
                </p>
              )}
            </div>
          ) : (
            <div className="card p-4">
              <h6 className="fw-bold">Want your match score?</h6>
              <p className="small text-muted">
                Log in as a candidate to see how well your resume matches this job.
              </p>
              <Link className="btn btn-outline-primary w-100" to="/login">Login</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
