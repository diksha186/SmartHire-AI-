/** Renders a list of skills as coloured Bootstrap badges. */
export default function SkillBadges({ skills = [], variant = 'primary', empty = 'None' }) {
  if (!skills.length) return <span className="text-muted small">{empty}</span>
  return (
    <>
      {skills.map((skill) => (
        <span key={skill} className={`badge rounded-pill text-bg-${variant} skill-badge`}>{skill}</span>
      ))}
    </>
  )
}
