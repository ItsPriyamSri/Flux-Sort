import React, { useState, useEffect, useRef } from 'react'
import { api, openProgressSocket } from '../api/client.js'

const ICON_MAP = {
  Images: '🖼️', Videos: '🎬', Documents: '📄', Audio: '🎵',
  Archives: '📦', Code: '💻', 'System Files': '⚙️', 'Mobile Apps': '📱',
  'Web Files': '🌐', 'Data Files': '📊', Fonts: '🔤',
  '3D Models': '🎮', Ebooks: '📚', Miscellaneous: '❓',
}

export default function ScanView({ onScanComplete }) {
  const [path, setPath] = useState('')
  const [defaults, setDefaults] = useState({})
  const [scanning, setScanning] = useState(false)
  const [progress, setProgress] = useState(null)   // { current, total, percent }
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const wsRef = useRef(null)

  useEffect(() => {
    api.defaults().then(d => setDefaults(d.directories || {})).catch(() => {})
  }, [])

  async function handleScan() {
    if (!path.trim()) { setError('Please enter a directory path.'); return }
    setError('')
    setResult(null)
    setProgress({ current: 0, total: 0, percent: 0 })
    setScanning(true)

    try {
      const { scan_id } = await api.startScan(path.trim())

      wsRef.current = openProgressSocket(scan_id, {
        onProgress: (ev) => setProgress({ current: ev.current, total: ev.total, percent: ev.percent }),
        onDone: async () => {
          wsRef.current?.close()
          const res = await api.getScan(scan_id)
          setResult(res)
          setScanning(false)
          setProgress(null)
        },
        onError: (ev) => {
          setError(ev.message || 'Scan failed')
          setScanning(false)
          setProgress(null)
        },
      })
    } catch (e) {
      setError(e.message)
      setScanning(false)
      setProgress(null)
    }
  }

  function handleProceed(mode) {
    onScanComplete(result, mode)
  }

  return (
    <div className="view-body fade-in">
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>
          Scan a Directory
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5 }}>
          Choose a folder to scan. Files are never moved until you approve.
        </p>
      </div>

      {/* Quick-select */}
      {Object.keys(defaults).length > 0 && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
          {Object.entries(defaults).map(([label, p]) => (
            <button
              key={label}
              className="btn btn-ghost btn-sm"
              onClick={() => setPath(p)}
              disabled={scanning}
            >
              {label === 'Downloads' ? '📥' : label === 'Desktop' ? '🖥️' : label === 'Documents' ? '📄' : '🏠'}{' '}
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Path input */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 24 }}>
        <input
          className="input input-mono"
          placeholder="/home/user/Downloads"
          value={path}
          onChange={e => setPath(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !scanning && handleScan()}
          disabled={scanning}
        />
        <button
          className="btn btn-primary"
          onClick={handleScan}
          disabled={scanning || !path.trim()}
          style={{ minWidth: 110 }}
        >
          {scanning ? <><span className="spin" style={{ display: 'inline-block' }}>⟳</span> Scanning…</> : '⚡ Scan'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="glass-card fade-in" style={{
          padding: '12px 16px', borderColor: 'var(--danger-dim)', marginBottom: 20,
          color: 'var(--danger)', fontSize: 13
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Progress */}
      {scanning && progress && (
        <div className="glass-card fade-in" style={{ padding: '20px 24px', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
            <span style={{ fontWeight: 500 }}>Scanning…</span>
            <span className="text-muted font-mono" style={{ fontSize: 12 }}>
              {progress.current} / {progress.total || '?'} files
            </span>
          </div>
          <div className="progress-track">
            <div
              className={`progress-fill ${progress.total === 0 ? 'pulse' : ''}`}
              style={{ width: `${progress.total > 0 ? progress.percent : 100}%` }}
            />
          </div>
          {progress.total > 0 && (
            <div className="text-muted" style={{ fontSize: 12, marginTop: 8, textAlign: 'right' }}>
              {progress.percent}%
            </div>
          )}
        </div>
      )}

      {/* Results */}
      {result && !scanning && (
        <div className="fade-in">
          {/* Stats */}
          <div className="stat-grid">
            <div className="stat-card">
              <span className="stat-label">Files Found</span>
              <span className="stat-value">{result.total_files}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Size</span>
              <span className="stat-value">{result.total_size_mb}</span>
              <span className="stat-sub">MB</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Categories</span>
              <span className="stat-value">{result.categories.length}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Scan Time</span>
              <span className="stat-value">{result.scan_duration_s}s</span>
            </div>
          </div>

          {/* Category breakdown */}
          <div className="section-heading">
            <h2>Category Breakdown</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12, marginBottom: 28 }}>
            {result.categories.map(cat => (
              <div key={cat.category} className="glass-card" style={{ padding: '14px 16px' }}>
                <div style={{ fontSize: 22, marginBottom: 6 }}>
                  {ICON_MAP[cat.category] || '📁'}
                </div>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 3 }}>{cat.category}</div>
                <div className="text-secondary" style={{ fontSize: 12 }}>
                  {cat.file_count} file{cat.file_count !== 1 ? 's' : ''} · {cat.total_size_mb} MB
                </div>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button className="btn btn-primary btn-lg" onClick={() => handleProceed('standard')}>
              👁️ Preview & Sort →
            </button>
            <button className="btn btn-ghost" onClick={() => handleProceed('ai')}>
              🤖 AI Smart Sort →
            </button>
            <span className="text-muted" style={{ fontSize: 12 }}>
              AI Smart Sort uses your custom categories
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
