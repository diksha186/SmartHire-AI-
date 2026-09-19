/** Small reusable labelled progress bar used across all AI screens. */
export default function ScoreBar({ label, value = 0, weight }) {
  const pct = Math.max(0, Math.min(100, Number(value) || 0))
  const colour = pct >= 75 ? 'bg-success' : pct >= 50 ? 'bg-info' : pct >= 30 ? 'bg-warning' : 'bg-danger'
  return (
    <div className="mb-3">
      <div className="d-flex justify-content-between small fw-semibold">
        <span>{label} {weight && <span className="text-muted">(weight {weight})</span>}</span>
        <span>{pct.toFixed(0)}%</span>
      </div>
      <div className="progress" style={{ height: '9px' }}>
        <div className={`progress-bar ${colour}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
