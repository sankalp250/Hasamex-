const rawBase = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').trim().replace(/\/+$/, '')
const API_BASE = rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || 'Request failed.')
  }
  return payload
}

export const api = {
  listTranscripts: () => request('/transcripts'),
  getGuideQuestions: () => request('/guide/questions'),
  analyzeGuide: () => request('/guide/analyze', { method: 'POST' }),
  crossAnalysis: () => request('/analysis/cross'),
  ask: (question, transcriptId = null) => request('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, transcript_id: transcriptId || undefined }),
  }),
  upload: async (file) => {
    const body = new FormData()
    body.append('file', file)
    return request('/transcripts/upload', { method: 'POST', body })
  },
}
