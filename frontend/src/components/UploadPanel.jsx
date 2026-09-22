import { useRef, useState } from 'react'

export default function UploadPanel({ onUpload, compact = false }) {
  const inputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleFiles(fileList) {
    const files = [...fileList].filter((file) => file.name.toLowerCase().endsWith('.txt'))
    if (!files.length) {
      setError('Please choose one or more .txt transcript files.')
      return
    }
    setBusy(true)
    setError('')
    try {
      for (const file of files) await onUpload(file)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      className={`upload-panel ${compact ? 'upload-panel-compact' : ''} ${dragActive ? 'drag-active' : ''}`}
      onDragOver={(event) => { event.preventDefault(); setDragActive(true) }}
      onDragLeave={() => setDragActive(false)}
      onDrop={(event) => { event.preventDefault(); setDragActive(false); handleFiles(event.dataTransfer.files) }}
    >
      <input ref={inputRef} hidden type="file" accept=".txt" multiple onChange={(event) => handleFiles(event.target.files)} />
      <div className="upload-icon">＋</div>
      <div>
        <div className="upload-title">Add another transcript</div>
        <div className="upload-copy">Drop a .txt file here or browse. New interviews are indexed immediately.</div>
      </div>
      <button className="button button-secondary" onClick={() => inputRef.current?.click()} disabled={busy}>
        {busy ? 'Indexing…' : 'Choose files'}
      </button>
      {error && <div className="form-error">{error}</div>}
    </div>
  )
}
