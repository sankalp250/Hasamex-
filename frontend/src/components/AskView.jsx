import { useState } from 'react'
import { api } from '../lib/api'
import EvidenceCard from './EvidenceCard'

const suggestions = [
  'What are the biggest barriers to adoption?',
  'How important is ROI?',
  'What is the purchasing constraint in Italy according to Dr. Rossi?',
  'How do the experts differ on purchase timelines?',
  'What role does surgeon training play in utilisation?',
]

export default function AskView({ transcripts = [] }) {
  const [question, setQuestion] = useState('')
  const [selectedScope, setSelectedScope] = useState('all')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event?.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    try {
      const scopeId = selectedScope === 'all' ? null : selectedScope
      setResult(await api.ask(question.trim(), scopeId))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="stack-lg">
      <div className="section-intro">
        <div>
          <div className="eyebrow">Ask the corpus</div>
          <h2>Ask one question across every interview.</h2>
          <p>The answer stays grounded in retrieved transcript evidence.</p>
        </div>
      </div>

      <div className="scope-bar">
        <span className="scope-label">Search scope:</span>
        <button
          type="button"
          className={`scope-pill ${selectedScope === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedScope('all')}
        >
          All interviews
        </button>
        {transcripts.map((t) => (
          <button
            type="button"
            key={t.id}
            className={`scope-pill ${selectedScope === t.id ? 'active' : ''}`}
            onClick={() => setSelectedScope(t.id)}
          >
            {t.market} ({t.expert_name})
          </button>
        ))}
      </div>

      <form className="ask-box" onSubmit={submit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={
            selectedScope === 'all'
              ? 'e.g. What factors make a robotic surgery programme financially viable?'
              : 'Ask a question specific to this interview...'
          }
          aria-label="Ask a question across the transcripts"
          rows={4}
        />
        <div className="ask-footer">
          <div className="suggestion-row">
            {suggestions.slice(0, 4).map((item) => (
              <button
                type="button"
                className="chip-button"
                key={item}
                onClick={() => setQuestion(item)}
              >
                {item}
              </button>
            ))}
          </div>
          <button
            className="button button-primary"
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? 'Analyzing…' : 'Ask question'}
          </button>
        </div>
      </form>

      {error && <div className="error-state">{error}</div>}

      {result && (
        <section className="answer-result">
          <div className="eyebrow">Grounded answer</div>
          <p className="large-answer">{result.answer}</p>
          <div className="result-source-heading">Supporting evidence</div>
          <div className="evidence-stack">
            {result.evidence && result.evidence.length > 0 ? (
              result.evidence.map((evidence) => (
                <EvidenceCard evidence={evidence} key={evidence.source_id} />
              ))
            ) : (
              <p className="subtle">No supporting evidence was matched for this query.</p>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
