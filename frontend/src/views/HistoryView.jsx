import React, { useState, useEffect } from 'react'
import { api } from '../api/client.js'

function groupByOperation(operations) {
  const map = {}
  for (const op of operations) {
    if (!map[op.operation_id]) {
      map[op.operation_id] = {
        operation_id: op.operation_id,
        timestamp: op.timestamp,
        files: [],
        source_dir: op.source_dir,
      }
    }
    map[op.operation_id].files.push(op)
  }
  return Object.values(map).sort((a, b) => b.timestamp.localeCompare(a.timestamp))
}

function OperationGroup({ group, onUndo, directory }) {
  const [expanded, setExpanded] = useState(false)
  const [undoing, setUndoing]   = useState(false)
  const [undoResult, setUndoResult] = useState(null)

  const ts = new Date(group.timestamp).toLocaleString()
  const byCategory = {}
  for (const f of group.files) {
    if (!byCategory[f.category]) byCategory[f.category] = 0
    byCategory[f.category]++
  }

  async function handleUndo() {
    if (!confirm(`Undo this operation? This will move ${group.files.length} file(s) back.`)) return
    setUndoing(true)
    try {
      const res = await api.undoOperation(group.operation_id, directory)
      setUndoResult(res)
      onUndo()
    } catch (e) {
      setUndoResult({ error: e.message })
    }
    setUndoing(false)
  }

  return (
    <div className="glass-card" style={{ padding: '16px 18px' }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>
              #{group.operation_id.slice(0, 8)}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{ts}</span>
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {Object.entries(byCategory).map(([cat, count]) => (
              <span key={cat} className="badge badge-muted">
                {count} {cat}
              </span>
            ))}
          </div>
          <div className="font-mono text-muted" style={{ fontSize: 11, marginTop: 4 }}>
            {group.source_dir}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setExpanded(e => !e)}
          >
            {expanded ? '▲' : '▼'} {group.files.length} files
          </button>
          {!undoResult && (
            <button
              className="btn btn-danger btn-sm"
              onClick={handleUndo}
              disabled={undoing}
            >
              {undoing ? '⟳' : '↩'} Undo
            </button>
          )}
        </div>
      </div>

      {/* Undo result */}
      {undoResult && (
        <div style={{
          marginTop: 12, padding: '8px 12px', borderRadius: 'var(--radius-sm)',
          background: undoResult.error ? 'var(--danger-dim)' : 'var(--success-dim)',
          color: undoResult.error ? 'var(--danger)' : 'var(--success)',
          fontSize: 12,
        }}>
          {undoResult.error
            ? `⚠ Undo failed: ${undoResult.error}`
            : `✓ Reverted ${undoResult.successful_undos} file(s) successfully`}
        </div>
      )}

      {/* File list */}
      {expanded && (
        <div style={{ marginTop: 12, borderTop: '1px solid var(--border)', paddingTop: 10, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {group.files.map((f, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 12 }}>
              <span className="badge badge-muted" style={{ flexShrink: 0 }}>{f.category}</span>
              <span className="font-mono text-secondary" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {f.file_name}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function HistoryView({ currentDirectory }) {
  const [groups, setGroups]     = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')

  function load() {
    setLoading(true)
    api.getHistory(currentDirectory || '', 100)
      .then(r => { setGroups(groupByOperation(r.operations || [])); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }
  useEffect(load, [currentDirectory])

  return (
    <div className="view-body fade-in">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Operation History</h1>
          <p className="text-secondary" style={{ fontSize: 13.5 }}>
            Every sort operation is logged. Undo any of them at any time.
          </p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={load} disabled={loading}>
          {loading ? '⟳' : '↻'} Refresh
        </button>
      </div>

      {error && <div className="text-danger" style={{ marginBottom: 16 }}>⚠ {error}</div>}

      {loading ? (
        <div style={{ display: 'flex', gap: 10, color: 'var(--text-secondary)' }}>
          <span className="spin">⟳</span> Loading history…
        </div>
      ) : groups.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🕐</div>
          <h3>No operations yet</h3>
          <p>Sort a directory to see it appear here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {groups.map(g => (
            <OperationGroup
              key={g.operation_id}
              group={g}
              onUndo={load}
              directory={currentDirectory}
            />
          ))}
        </div>
      )}
    </div>
  )
}
