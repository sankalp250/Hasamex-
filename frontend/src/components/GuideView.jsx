import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import EvidenceCard from './EvidenceCard'

export default function GuideView({ cachedData, onDataLoaded }) {
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
    api.analyzeGuide()
      .then((value) => {
        if (active) {
          setData(value)
          onDataLoaded?.(value)
        }
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [cachedData, onDataLoaded])

  if (loading) return <div className="loading-state"><span className="spinner" /> Building evidence-backed answers…</div>
  if (error) return <div className="error-state">{error}</div>

  return (
    <div className="stack-lg">
      <div className="section-intro">
        <div>
          <div className="eyebrow">Interview guide</div>
          <h2>Six questions, answered per expert.</h2>
          <p>Every answer is paired with source evidence from the original transcript.</p>
        </div>
      </div>
      <div className="guide-list">
        {data.questions.map((item, index) => (
          <section className="question-card" key={item.question}>
            <div className="question-number">0{index + 1}</div>
            <div className="question-body">
              <h3>{item.question}</h3>
              <div className="answer-grid">
                {item.answers.map((answer) => (
                  <article className="expert-answer" key={answer.transcript_id}>
                    <div className="expert-heading">
                      <div>
                        <div className="expert-name">{answer.expert}</div>
                        <div className="expert-role">{answer.role} · {answer.market}</div>
                      </div>
                    </div>
                    <p className="answer-text">{answer.answer}</p>
                    <div className="evidence-stack">
                      {answer.evidence.map((evidence) => <EvidenceCard evidence={evidence} key={evidence.source_id} />)}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
