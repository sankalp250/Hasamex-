import Badge from './Badge'

export default function EvidenceCard({ evidence }) {
  return (
    <div className="evidence-card">
      <div className="evidence-topline">
        <div className="source-meta">
          <Badge>{evidence.market}</Badge>
          <span>{evidence.expert}</span>
          <span className="dot">•</span>
          <span>{evidence.timestamp}</span>
        </div>
        <span className="source-id">{evidence.source_id}</span>
      </div>
      <blockquote>“{evidence.quote}”</blockquote>
    </div>
  )
}
