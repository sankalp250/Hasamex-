import StatCard from './StatCard'
import UploadPanel from './UploadPanel'

export default function Overview({ transcripts, onUpload }) {
  return (
    <div className="stack-lg">
      <div className="hero">
        <div className="hero-copy">
          <div className="eyebrow">Expert interview intelligence</div>
          <h1>Turn interview transcripts into evidence you can trust.</h1>
          <p>Analyze the supplied European robotic surgery interviews, trace every claim back to a timestamp, and keep the corpus extensible with new uploads.</p>
        </div>
        <div className="hero-aside">
          <div className="hero-line" />
          <span>Source-grounded analysis</span>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard label="Expert interviews" value={transcripts.length} detail="France · Germany · UK + uploads" />
        <StatCard label="Interview guide" value="06" detail="Questions answered per expert" />
        <StatCard label="Evidence model" value="01" detail="Source → quote → timestamp" />
        <StatCard label="AI mode" value="RAG" detail="Retrieval before generation" />
      </div>

      <section className="panel">
        <div className="panel-heading"><span>01</span><h3>Loaded interviews</h3></div>
        <div className="transcript-list">
          {transcripts.map((item) => (
            <div className="transcript-row" key={item.id}>
              <div className="transcript-market">{item.market}</div>
              <div>
                <div className="transcript-name">{item.expert_name}</div>
                <div className="transcript-role">{item.role}</div>
              </div>
              <div className="transcript-count">{item.chunk_count} source turns</div>
            </div>
          ))}
        </div>
      </section>

      <UploadPanel onUpload={onUpload} />
    </div>
  )
}
