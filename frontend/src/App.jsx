import { useEffect, useState } from 'react'
import { api } from './lib/api'
import Sidebar from './components/Sidebar'
import Overview from './components/Overview'
import GuideView from './components/GuideView'
import CrossView from './components/CrossView'
import AskView from './components/AskView'

export default function App() {
  const [active, setActive] = useState('overview')
  const [transcripts, setTranscripts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [guideData, setGuideData] = useState(null)
  const [crossData, setCrossData] = useState(null)

  async function loadTranscripts() {
    const data = await api.listTranscripts()
    setTranscripts(data)
  }

  useEffect(() => {
    loadTranscripts().catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  async function onUpload(file) {
    await api.upload(file)
    setGuideData(null)
    setCrossData(null)
    await loadTranscripts()
    setActive('overview')
  }

  function content() {
    if (loading) return <div className="loading-state"><span className="spinner" /> Loading workspace…</div>
    if (error) return <div className="error-state">{error}<div className="subtle">Make sure the FastAPI server is running on port 8000.</div></div>
    if (active === 'guide') return <GuideView cachedData={guideData} onDataLoaded={setGuideData} />
    if (active === 'cross') return <CrossView cachedData={crossData} onDataLoaded={setCrossData} />
    if (active === 'ask') return <AskView transcripts={transcripts} />
    return <Overview transcripts={transcripts} onUpload={onUpload} />
  }

  return (
    <div className="app-shell">
      <Sidebar active={active} onChange={setActive} transcriptCount={transcripts.length} onUploadClick={() => setDrawerOpen(true)} />
      <main className="main-content">
        <header className="topbar">
          <div className="topbar-title">European Robotic Surgery Market</div>
          <div className="topbar-status"><span className="status-dot" /> Evidence workspace</div>
        </header>
        <div className="content-wrap">{content()}</div>
      </main>
      {drawerOpen && (
        <div className="drawer-backdrop" role="presentation" onClick={() => setDrawerOpen(false)}>
          <div className="drawer" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <div className="drawer-header"><div><div className="eyebrow">Expand corpus</div><h2>Add a new interview</h2></div><button className="icon-button" onClick={() => setDrawerOpen(false)} aria-label="Close">×</button></div>
            <OverviewUpload onUpload={async (file) => { await onUpload(file); setDrawerOpen(false) }} />
          </div>
        </div>
      )}
    </div>
  )
}

function OverviewUpload({ onUpload }) {
  const [error, setError] = useState('')
  async function pick(event) {
    const file = event.target.files?.[0]
    if (!file) return
    try { await onUpload(file) } catch (err) { setError(err.message) }
  }
  return (
    <div className="drawer-upload">
      <label className="drop-zone">
        <input type="file" accept=".txt" onChange={pick} />
        <span className="drop-title">Choose a .txt transcript</span>
        <span className="drop-copy">The parser will extract expert, role, market, speakers and timestamps.</span>
      </label>
      {error && <div className="form-error">{error}</div>}
    </div>
  )
}
