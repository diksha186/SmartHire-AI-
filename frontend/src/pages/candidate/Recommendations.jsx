import { useEffect, useState } from 'react'
import { candidateApi, errorMessage } from '../../services/api'
import JobCard from '../../components/JobCard'
import Loader from '../../components/Loader'

export default function Recommendations() {
  const [recs, setRecs] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    candidateApi.recommendations(20)
      .then(({ data }) => setRecs(data))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loader text="Matching you against every open job..." />

  return (
    <div className="container py-4">
      <h3 className="fw-bold mb-1">Recommended jobs</h3>
      <p className="text-muted small">
        Ranked by an explainable weighted score: skills 50%, experience 20%, education 10%, relevance 20%.
      </p>
      {error && <div className="alert alert-warning">{error}</div>}
      <div className="row g-4">
        {recs.map((rec) => (
          <div className="col-md-6 col-lg-4" key={rec.job_id}>
            <JobCard job={{ ...rec, id: rec.job_id, description: rec.explanation,
                            required_skills: rec.matching_skills.join(',') }}
                     matchScore={rec.match_score} matching={rec.matching_skills}
                     missing={rec.missing_skills} />
          </div>
        ))}
        {recs.length === 0 && !error && <p className="text-muted">No open jobs to recommend yet.</p>}
      </div>
    </div>
  )
}
