import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { candidateApi, errorMessage } from '../../services/api'
import ScoreBar from '../../components/ScoreBar'
import SkillBadges from '../../components/SkillBadges'

export default function ResumeUpload() {
  const [file, setFile] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    candidateApi.latestAnalysis()
      .then(({ data }) => setAnalysis(data))
      .catch(() => { /* nothing analysed yet - that is fine */ })
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    if (!file) return setMessage({ type: 'warning', text: 'Please choose a PDF or DOCX file first.' })
    setBusy(true); setMessage(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await candidateApi.uploadResume(formData)
      setAnalysis(data)
      setMessage({ type: 'success', text: 'Resume analysed successfully by the AI engine.' })
    } catch (err) {
      setMessage({ type: 'danger', text: errorMessage(err) })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-3">AI resume screening</h3>
      {message && <div className={`alert alert-${message.type} py-2 small`}>{message.text}</div>}

      <div className="row g-4">
        <div className="col-lg-5">
          <form className="card p-4" onSubmit={submit}>
            <h6 className="fw-bold">Upload your resume</h6>
            <p className="small text-muted">PDF or DOCX, maximum 5 MB. Text-based files only.</p>
            <input className="form-control mb-3" type="file" accept=".pdf,.docx"
                   onChange={(e) => setFile(e.target.files[0])} />
            <button className="btn btn-primary" disabled={busy}>
              {busy ? 'Analysing with spaCy...' : 'Upload & analyse'}
            </button>
            <hr />
            <p className="small mb-0 text-muted">
              Pipeline: text extraction &rarr; cleaning &rarr; NLP &rarr; skill / education / experience
              detection &rarr; weighted score &rarr; suggestions.
            </p>
          </form>
        </div>

        <div className="col-lg-7">
          {analysis ? (
            <div className="card p-4">
              <div className="d-flex align-items-center gap-4 mb-3">
                <div className="score-circle">{Math.round(analysis.resume_score)}</div>
                <div>
                  <h5 className="fw-bold mb-1">Resume score: {analysis.resume_score}/100</h5>
                  <p className="small text-muted mb-0">
                    Detected education: {analysis.education_detected || 'not found'} &middot;
                    Experience: {analysis.experience_years} yrs
                  </p>
                </div>
              </div>

              <h6 className="fw-bold">Why you got this score</h6>
              <ScoreBar label="Skills match" value={analysis.skills_score} weight="50%" />
              <ScoreBar label="Experience" value={analysis.experience_score} weight="20%" />
              <ScoreBar label="Education" value={analysis.education_score} weight="10%" />
              <ScoreBar label="Keywords / achievements" value={analysis.keyword_score} weight="20%" />

              <h6 className="fw-bold mt-3">Skills extracted from your resume</h6>
              <div className="mb-3"><SkillBadges skills={analysis.extracted_skills} /></div>

              <h6 className="fw-bold">Suggestions to improve</h6>
              <ul className="small">
                {analysis.suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>

              <Link className="btn btn-outline-primary btn-sm" to="/candidate/recommendations">
                See jobs matched to this resume
              </Link>
            </div>
          ) : (
            <div className="card p-5 text-center text-muted">
              <p className="mb-0">No resume analysed yet. Upload one to see your explainable AI score.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
