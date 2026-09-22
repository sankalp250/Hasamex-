import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import EvidenceCard from './EvidenceCard'

export default function CrossView({ cachedData, onDataLoaded }) {
  const [data, setData] = useState(cachedData || null)
  const [loading, setLoading] = useState(!cachedData)
  const [error, setError] = useState('')

  useEffect(() => {
    if (cachedData) {
      setData(cachedData)
      setLoading(false)
      return
    }
    let active = true
    api.crossAnalysis()
      .then((val) => {
        if (active) {
          setData(val)
          onDataLoaded?.(val)
        }
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [cachedData, onDataLoaded])

  if (loading) return <div className="loading-state"><span className="spinner" /> Comparing interviews…</div>
  if (error) return <div className="error-state">{error}</div>

  return (
    <div className="stack-lg">
      <div className="section-intro">
        <div>
          <div className="eyebrow">Cross-interview analysis</div>
          <h2>Where the interviews converge — and diverge.</h2>
          <p>Patterns are surfaced from the loaded evidence rather than outside knowledge.</p>
        </div>
      </div>

      <div className="analysis-grid">
        <section className="panel">
          <div className="panel-heading"><span>01</span><h3>Common themes</h3></div>
          <div className="stack-md">
            {data.themes.map((theme) => (
              <div className="theme-row" key={theme.name}>
                <div className="theme-title">{theme.name}</div>
                <p>{theme.summary}</p>
                <div className="evidence-stack">
                  {theme.evidence.slice(0, 2).map((evidence) => <EvidenceCard evidence={evidence} key={evidence.source_id} />)}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading"><span>02</span><h3>Key differences</h3></div>
          <div className="stack-md">
            {data.differences.map((item) => (
              <div className="theme-row" key={item.topic}>
                <div className="theme-title">{item.topic}</div>
                <p>{item.summary}</p>
                <div className="evidence-stack">
                  {item.evidence.slice(0, 3).map((evidence) => <EvidenceCard evidence={evidence} key={evidence.source_id} />)}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
