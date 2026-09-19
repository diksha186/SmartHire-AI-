import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { applicationApi, employerApi, errorMessage } from '../../services/api'
import SkillBadges from '../../components/SkillBadges'
import Loader from '../../components/Loader'

const STATUSES = ['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Rejected', 'Selected']

export default function Applicants() {
  const { id } = useParams()
  const [rows, setRows] = useState([])
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    employerApi.applicants(id)
      .then(({ data }) => setRows(data))
      .catch((err) => setMessage({ type: 'danger', text: errorMessage(err) }))
      .finally(() => setLoading(false))
  }

  useEffect(load, [id])

  const changeStatus = async (applicationId, status) => {
    try {
      await applicationApi.updateStatus(applicationId, status)
      setRows(rows.map((r) => r.application_id === applicationId
        ? { ...r, application_status: status } : r))
      setMessage({ type: 'success', text: `Status updated to "${status}".` })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    }
  }

  if (loading) return <Loader text="Ranking applicants with the AI engine..." />

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-1">AI-ranked applicants</h3>
      <p className="text-muted small">
        Sorted by match score. Skills 50%, experience 20%, education 10%, relevance 20%.
      </p>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}

      {rows.length === 0 ? (
        <div className="card p-5 text-center text-muted">No applications for this job yet.</div>
      ) : (
        <div className="row g-3">
          {rows.map((r, index) => (
            <div className="col-12" key={r.application_id}>
              <div className="card p-3">
                <div className="row align-items-center g-3">
                  <div className="col-md-1 text-center">
                    <span className="badge text-bg-dark fs-6">#{index + 1}</span>
                  </div>
                  <div className="col-md-3">
                    <h6 className="fw-bold mb-0">{r.name}</h6>
                    <p className="small text-muted mb-0">{r.email}</p>
                    <p className="small mb-0">
                      {r.education || 'Education n/a'} &middot; {r.experience ?? 0} yrs &middot; {r.location || 'n/a'}
                    </p>
                  </div>
                  <div className="col-md-2 text-center">
                    <div className="fw-bold fs-4 text-primary">{Math.round(r.match_score)}%</div>
                    <div className="small text-muted">Job match</div>
                    <div className="small">Resume: {r.resume_score ? Math.round(r.resume_score) : '--'}/100</div>
                  </div>
                  <div className="col-md-3">
                    <div className="small text-success mb-1">
                      Matching: <SkillBadges skills={r.matching_skills} variant="success" empty="none" />
                    </div>
                    <div className="small text-danger">
                      Missing: <SkillBadges skills={r.missing_skills} variant="danger" empty="none" />
                    </div>
                  </div>
                  <div className="col-md-3">
                    <label className="form-label small fw-semibold mb-1">Application status</label>
                    <select className="form-select form-select-sm"
                            value={r.application_status}
                            onChange={(e) => changeStatus(r.application_id, e.target.value)}>
                      {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
