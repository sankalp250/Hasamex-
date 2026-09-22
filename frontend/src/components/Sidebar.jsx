export default function Sidebar({ active, onChange, transcriptCount, onUploadClick }) {
  const items = [
    ['overview', 'Overview'],
    ['guide', 'Interview guide'],
    ['cross', 'Cross analysis'],
    ['ask', 'Ask the corpus'],
  ]
  return (
    <aside className="sidebar">
      <div className="brand-mark">H</div>
      <div className="brand-lockup">
        <div className="brand-word">Hasamex</div>
        <div className="brand-sub">Research intelligence</div>
      </div>
      <nav className="nav-list" aria-label="Primary navigation">
        {items.map(([key, label]) => (
          <button key={key} className={`nav-button ${active === key ? 'active' : ''}`} onClick={() => onChange(key)}>
            <span className="nav-index">{String(items.findIndex((item) => item[0] === key) + 1).padStart(2, '0')}</span>
            {label}
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="corpus-card">
          <div className="eyebrow">Corpus</div>
          <strong>{transcriptCount} interviews</strong>
          <span>Indexed and ready</span>
        </div>
        <button className="button button-secondary full-width" onClick={onUploadClick}>＋ Add transcript</button>
      </div>
    </aside>
  )
}
