import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { jobApi } from '../services/api'
import JobCard from '../components/JobCard'

export default function Home() {
  const [jobs, setJobs] = useState([])

  useEffect(() => {
    jobApi.list({ limit: 6 }).then(({ data }) => setJobs(data)).catch(() => setJobs([]))
  }, [])

  return (
    <>
      <section className="hero py-5 mb-5">
        <div className="container py-4">
          <div className="row align-items-center">
            <div className="col-lg-7">
              <h1 className="display-5 fw-bold">Get hired by the right company, faster.</h1>
              <p className="lead">
                SmartHire AI reads your resume with real NLP, scores it out of 100, tells you exactly
                what to improve, and recommends the jobs you actually match.
              </p>
              <Link className="btn btn-warning btn-lg fw-semibold me-2" to="/register">Create free account</Link>
              <Link className="btn btn-outline-light btn-lg" to="/jobs">Browse jobs</Link>
            </div>
            <div className="col-lg-5 text-center d-none d-lg-block">
              <div className="bg-white bg-opacity-10 rounded-4 p-4">
                <div className="score-circle mx-auto mb-3">82</div>
                <p className="mb-0 small">Sample resume score &mdash; skills 90%, education 85%, experience 75%</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="container">
        <div className="row g-4 mb-5">
          {[
            ['AI Resume Screening', 'PDF/DOCX text extraction with spaCy NLP, then an explainable 0-100 score.'],
            ['Job Recommendations', 'Weighted skill, experience, education and relevance matching.'],
            ['Candidate Ranking', 'Employers see applicants automatically ranked by fit.'],
          ].map(([title, text]) => (
            <div className="col-md-4" key={title}>
              <div className="card h-100 p-4">
                <h5 className="fw-bold">{title}</h5>
                <p className="text-muted mb-0 small">{text}</p>
              </div>
            </div>
          ))}
        </div>

        <h4 className="fw-bold mb-3">Latest openings</h4>
        <div className="row g-4">
          {jobs.length === 0 && <p className="text-muted">No jobs posted yet.</p>}
          {jobs.map((job) => (
            <div className="col-md-6 col-lg-4" key={job.id}><JobCard job={job} /></div>
          ))}
        </div>
      </div>
    </>
  )
}
