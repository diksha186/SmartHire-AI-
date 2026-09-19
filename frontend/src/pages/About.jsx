export default function About() {
  return (
    <div className="container py-5" style={{ maxWidth: '820px' }}>
      <h2 className="fw-bold mb-3">About SmartHire AI</h2>
      <p>
        SmartHire AI is an intelligent recruitment platform built as a BCA major project. It connects
        candidates and employers and uses Natural Language Processing to remove the manual effort from
        resume screening.
      </p>
      <h5 className="fw-bold mt-4">How the AI works</h5>
      <ol className="small">
        <li>The resume (PDF or DOCX) is uploaded and validated.</li>
        <li>Text is extracted with pdfplumber / PyPDF2 / python-docx.</li>
        <li>spaCy cleans and lemmatises the text.</li>
        <li>Skills, education, experience and achievement keywords are detected.</li>
        <li>A weighted score is computed: skills 50%, experience 20%, education 10%, relevance 20%.</li>
        <li>The same formula scores the candidate against every open job.</li>
      </ol>
      <h5 className="fw-bold mt-4">Technology stack</h5>
      <p className="small mb-0">
        React.js, Bootstrap 5 &middot; FastAPI, PyJWT, SQLAlchemy &middot; MySQL &middot;
        spaCy, PyPDF2, pdfplumber, python-docx
      </p>
    </div>
  )
}
