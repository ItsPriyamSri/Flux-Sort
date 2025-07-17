import React, { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client.js'

const ICON_MAP = {
  Images: '🖼️', Videos: '🎬', Documents: '📄', Audio: '🎵',
  Archives: '📦', Code: '💻', 'System Files': '⚙️', 'Mobile Apps': '📱',
  'Web Files': '🌐', 'Data Files': '📊', Fonts: '🔤',
  '3D Models': '🎮', Ebooks: '📚', Miscellaneous: '❓',
}

function ConfidenceBadge({ value }) {
  if (value >= 0.85) return <span className="badge badge-green" style={{ fontSize: 10 }}>✓ {Math.round(value * 100)}%</span>
  if (value >= 0.70) return <span className="badge badge-blue"  style={{ fontSize: 10 }}>~ {Math.round(value * 100)}%</span>
  return <span className="badge badge-amber" style={{ fontSize: 10 }}>⚠ {Math.round(value * 100)}%</span>
}

function FileRow({ file, allCategories, onReassign }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px',
      borderRadius: 'var(--radius-sm)', transition: 'background var(--transition)',
    }}
      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      <span style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {file.name}
      </span>
      {file.confidence !== undefined && <ConfidenceBadge value={file.confidence} />}
      {onReassign && (
        <select
          value={file.category}
          onChange={e => onReassign(file.path, e.target.value)}
          style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
            color: 'var(--text-secondary)', borderRadius: 'var(--radius-sm)',
            padding: '2px 6px', fontSize: 11, cursor: 'pointer',
          }}
        >
          {allCategories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      )}
    </div>
  )
}

function CategoryColumn({ name, files, allCategories, onReassign, color }) {
  const [expanded, setExpanded] = useState(false)
  const shown = expanded ? files : files.slice(0, 8)
  const hasLow = files.some(f => f.confidence !== undefined && f.confidence < 0.7)

  return (
    <div className="glass-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
      {/* Column header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{ fontSize: 20 }}>{ICON_MAP[name] || '📁'}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}>
            {name}
            {hasLow && <span className="badge badge-amber" style={{ fontSize: 9 }}>Review</span>}
          </div>
          <div className="text-muted" style={{ fontSize: 11 }}>{files.length} file{files.length !== 1 ? 's' : ''}</div>
        </div>
        {color && (
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, flexShrink: 0 }} />
        )}
      </div>

      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 8, display: 'flex', flexDirection: 'column' }}>
        {shown.map(f => (
          <FileRow key={f.path} file={f} allCategories={allCategories} onReassign={onReassign} />
        ))}
        {files.length > 8 && (
          <button
            className="btn btn-ghost btn-sm"
            style={{ marginTop: 6, alignSelf: 'flex-start' }}
            onClick={() => setExpanded(e => !e)}
          >
            {expanded ? '▲ Show less' : `▼ Show all ${files.length}`}
          </button>
        )}
      </div>
    </div>
  )
}

export default function PreviewView({ scanResult, sortMode, onSortDone, onNavigate }) {
  const [preview, setPreview]           = useState(null)   // { moves_by_category }
  const [aiResult, setAiResult]         = useState(null)   // { classifications }
  const [taxonomy, setTaxonomy]         = useState([])
  const [loading, setLoading]           = useState(true)
  const [aiLoading, setAiLoading]       = useState(false)
  const [overrides, setOverrides]       = useState({})     // path → new category
  const [executing, setExecuting]       = useState(false)
  const [doneResult, setDoneResult]     = useState(null)
  const [error, setError]               = useState('')

  const isAI = sortMode === 'ai'

  // Load standard preview + taxonomy on mount
  useEffect(() => {
    if (!scanResult) return
    setLoading(true)
    Promise.all([
      api.previewSort(scanResult.scan_id),
      api.getTaxonomy(),
    ])
      .then(([prev, tax]) => {
        setPreview(prev)
        setTaxonomy(tax.taxonomy || [])
        setLoading(false)
        if (isAI) runAIClassify(tax.taxonomy || [])
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [scanResult, isAI])

  async function runAIClassify(tax) {
    setAiLoading(true)
    try {
      const res = await api.classify(scanResult.scan_id, [])
      setAiResult(res)
    } catch (e) {
      setError('AI classification failed: ' + e.message)
    }
    setAiLoading(false)
  }

  // Build the categorised file list for display
  const displayData = useCallback(() => {
    const groups = {}

    if (isAI && aiResult) {
      for (const c of aiResult.classifications) {
        const cat = overrides[c.path] || c.category
        if (!groups[cat]) groups[cat] = []
        groups[cat].push({ ...c, category: cat })
      }
    } else if (preview) {
      for (const [cat, moves] of Object.entries(preview.moves_by_category)) {
        groups[cat] = moves.map(m => ({
          name: m.source.split('/').pop(),
          path: m.source,
          destination: m.destination,
          category: overrides[m.source] || cat,
          confidence: 0.97,
        }))
      }
    }
    return groups
  }, [isAI, aiResult, preview, overrides])

  function handleReassign(filePath, newCategory) {
    setOverrides(o => ({ ...o, [filePath]: newCategory }))
  }

  // Build final move list applying overrides
  function buildMoves() {
    const groups = displayData()
    const moves = []
    const baseDir = scanResult.directory

    for (const [cat, files] of Object.entries(groups)) {
      // Find folder name: taxonomy first, then use category name directly
      const taxEntry = taxonomy.find(t => t.name === cat)
      const folderName = taxEntry ? taxEntry.folder_name : cat

      for (const f of files) {
        const fileName = f.name || f.path.split('/').pop()
        moves.push({
          source: f.path,
          destination: `${baseDir}/${folderName}/${fileName}`,
          category: cat,
        })
      }
    }
    return moves
  }

  async function handleExecute() {
    setExecuting(true)
    setError('')
    try {
      const moves = buildMoves()
      const result = await api.executeSort(scanResult.scan_id, moves)
      setDoneResult(result)
      onSortDone(result)
    } catch (e) {
      setError(e.message)
    }
    setExecuting(false)
  }

  // All categories for the reassign dropdown
  const allCategories = isAI
    ? taxonomy.map(t => t.name)
    : Object.keys(displayData())

  if (!scanResult) {
    return (
      <div className="view-body">
        <div className="empty-state">
          <div className="empty-icon">👁️</div>
          <h3>No scan in progress</h3>
          <p>Run a scan first from the Scan &amp; Sort tab.</p>
          <button className="btn btn-primary" onClick={() => onNavigate('scan')}>Go to Scan</button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="view-body fade-in" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span className="spin" style={{ fontSize: 22 }}>⟳</span>
        <span className="text-secondary">Loading preview…</span>
      </div>
    )
  }

  if (doneResult) {
    return (
      <div className="view-body fade-in">
        <div className="glass-card" style={{ padding: 32, textAlign: 'center', maxWidth: 480, margin: '60px auto' }}>
          <div style={{ fontSize: 52, marginBottom: 16 }}>✨</div>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Sort Complete!</h2>
          <p className="text-secondary" style={{ marginBottom: 24 }}>
            {doneResult.successful_moves} files organised in {doneResult.duration_s}s
          </p>
          <div className="stat-grid" style={{ marginBottom: 24 }}>
            <div className="stat-card"><span className="stat-label">Moved</span><span className="stat-value text-success">{doneResult.successful_moves}</span></div>
            <div className="stat-card"><span className="stat-label">Failed</span><span className="stat-value text-danger">{doneResult.failed_moves}</span></div>
            <div className="stat-card"><span className="stat-label">Size</span><span className="stat-value">{doneResult.total_size_moved_mb} MB</span></div>
          </div>
          {doneResult.errors.length > 0 && (
            <div style={{ marginBottom: 16, textAlign: 'left' }}>
              {doneResult.errors.slice(0, 3).map((e, i) => (
                <div key={i} className="text-danger" style={{ fontSize: 11.5, marginBottom: 4 }}>⚠ {e}</div>
              ))}
            </div>
          )}
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            <button className="btn btn-ghost" onClick={() => onNavigate('history')}>View History & Undo</button>
            <button className="btn btn-primary" onClick={() => onNavigate('scan')}>Sort Another Folder</button>
          </div>
        </div>
      </div>
    )
  }

  const groups = displayData()
  const totalFiles = Object.values(groups).reduce((s, f) => s + f.length, 0)
  const lowConfidence = isAI
    ? Object.values(groups).flat().filter(f => f.confidence < 0.7).length
    : 0

  return (
    <div className="view-body fade-in">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
            {isAI ? '🤖 AI Sort Preview' : '👁️ Sort Preview'}
          </h1>
          <p className="text-secondary" style={{ fontSize: 13 }}>
            {totalFiles} files across {Object.keys(groups).length} categories
            {lowConfidence > 0 && (
              <span className="badge badge-amber" style={{ marginLeft: 10 }}>
                ⚠ {lowConfidence} need review
              </span>
            )}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-ghost" onClick={() => onNavigate('scan')}>← Back</button>
          <button
            className="btn btn-success btn-lg"
            onClick={handleExecute}
            disabled={executing || totalFiles === 0}
          >
            {executing
              ? <><span className="spin" style={{ display: 'inline-block' }}>⟳</span> Moving files…</>
              : `✓ Execute Sort (${totalFiles} files)`}
          </button>
        </div>
      </div>

      {/* AI status */}
      {isAI && aiLoading && (
        <div className="glass-card fade-in" style={{ padding: '14px 18px', marginBottom: 20, display: 'flex', gap: 12, alignItems: 'center', borderColor: 'var(--border-accent)' }}>
          <span className="spin" style={{ display: 'inline-block', fontSize: 18 }}>⟳</span>
          <span>Gemini is classifying your files with AI…</span>
        </div>
      )}
      {isAI && aiResult && (
        <div style={{ marginBottom: 16, fontSize: 12, color: 'var(--text-muted)' }}>
          🤖 {aiResult.ai_calls_made} API call{aiResult.ai_calls_made !== 1 ? 's' : ''} made · {aiResult.cached_results} from cache
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ padding: '10px 14px', background: 'var(--danger-dim)', borderRadius: 'var(--radius-md)', color: 'var(--danger)', fontSize: 13, marginBottom: 16 }}>
          ⚠️ {error}
        </div>
      )}

      {/* Category columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
        {Object.entries(groups).map(([cat, files]) => {
          const taxEntry = taxonomy.find(t => t.name === cat)
          return (
            <CategoryColumn
              key={cat}
              name={cat}
              files={files}
              allCategories={allCategories.length ? allCategories : Object.keys(groups)}
              onReassign={handleReassign}
              color={taxEntry?.color}
            />
          )
        })}
      </div>
    </div>
  )
}
