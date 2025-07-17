import React, { useState, useEffect } from 'react'
import { api } from '../api/client.js'

const DAYS   = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
const STRATS = [
  { value: 'rename',    label: 'Rename (file (1).ext)' },
  { value: 'skip',      label: 'Skip duplicates' },
  { value: 'overwrite', label: 'Overwrite' },
]

export default function SettingsView() {
  const [settings, setSettings]   = useState(null)
  const [loading, setLoading]     = useState(true)
  const [saving, setSaving]       = useState(false)
  const [apiKey, setApiKey]       = useState('')
  const [showKey, setShowKey]     = useState(false)
  const [msg, setMsg]             = useState({ type: '', text: '' })

  useEffect(() => {
    api.getSettings()
      .then(s => { setSettings(s); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setMsg({})
    try {
      const payload = { ...settings }
      if (apiKey.trim()) payload.gemini_api_key = apiKey.trim()
      await api.updateSettings(payload)
      setApiKey('')
      setMsg({ type: 'success', text: 'Settings saved.' })
    } catch (err) {
      setMsg({ type: 'error', text: err.message })
    }
    setSaving(false)
  }

  async function handleClearKey() {
    if (!confirm('Remove your API key?')) return
    await api.clearApiKey()
    setMsg({ type: 'success', text: 'API key removed.' })
  }

  if (loading || !settings) return (
    <div className="view-body fade-in" style={{ display: 'flex', gap: 10, color: 'var(--text-secondary)' }}>
      <span className="spin">⟳</span> Loading…
    </div>
  )

  return (
    <div className="view-body fade-in">
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>Settings</h1>
        <p className="text-secondary" style={{ fontSize: 13.5 }}>
          Configure your Gemini API key, scheduler, and sort preferences.
        </p>
      </div>

      <form onSubmit={handleSave} style={{ maxWidth: 600, display: 'flex', flexDirection: 'column', gap: 28 }}>

        {/* Gemini API Key */}
        <section className="glass-card" style={{ padding: '20px 22px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>🔑 Gemini API Key</h2>
          <p className="text-muted" style={{ fontSize: 12, marginBottom: 14 }}>
            Required for AI Smart Sort. Your key is stored locally and never sent anywhere except Google's API.{' '}
            <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" style={{ color: 'var(--text-accent)' }}>
              Get a free key →
            </a>
          </p>

          {settings.gemini_api_key === '••••••••' ? (
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 10 }}>
              <span className="badge badge-green">✓ API key configured</span>
              <button type="button" className="btn btn-danger btn-sm" onClick={handleClearKey}>Remove</button>
            </div>
          ) : (
            <div className="text-muted" style={{ fontSize: 12, marginBottom: 10 }}>
              No key configured. AI features will fall back to extension-based sorting.
            </div>
          )}

          <div style={{ position: 'relative' }}>
            <input
              className="input input-mono"
              type={showKey ? 'text' : 'password'}
              placeholder="AIza…"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            <button
              type="button"
              style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13 }}
              onClick={() => setShowKey(s => !s)}
            >
              {showKey ? '🙈' : '👁️'}
            </button>
          </div>
          <div className="text-muted" style={{ fontSize: 11, marginTop: 6 }}>
            Leave blank to keep the existing key. The key is never returned once saved.
          </div>
        </section>

        {/* Scheduler */}
        <section className="glass-card" style={{ padding: '20px 22px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>📅 Weekly Scheduler</h2>
              <p className="text-muted" style={{ fontSize: 12 }}>Automatically scan watched folders and queue files for your review.</p>
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings.scheduler_enabled}
                onChange={e => setSettings(s => ({ ...s, scheduler_enabled: e.target.checked }))}
              />
              <span style={{ fontSize: 13, color: settings.scheduler_enabled ? 'var(--success)' : 'var(--text-muted)' }}>
                {settings.scheduler_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </label>
          </div>

          {settings.scheduler_enabled && (
            <div style={{ display: 'flex', gap: 12 }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>Day</label>
                <select
                  className="input"
                  value={settings.scheduler_day}
                  onChange={e => setSettings(s => ({ ...s, scheduler_day: e.target.value }))}
                  style={{ textTransform: 'capitalize' }}
                >
                  {DAYS.map(d => <option key={d} value={d} style={{ textTransform: 'capitalize' }}>{d}</option>)}
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>Time</label>
                <input
                  className="input input-mono"
                  type="time"
                  value={settings.scheduler_time}
                  onChange={e => setSettings(s => ({ ...s, scheduler_time: e.target.value }))}
                />
              </div>
            </div>
          )}
        </section>

        {/* Conflict strategy */}
        <section className="glass-card" style={{ padding: '20px 22px' }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>⚔️ File Conflict Strategy</h2>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {STRATS.map(s => (
              <button
                key={s.value}
                type="button"
                className={`btn ${settings.conflicts_strategy === s.value ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setSettings(prev => ({ ...prev, conflicts_strategy: s.value }))}
              >
                {s.label}
              </button>
            ))}
          </div>
        </section>

        {/* Message */}
        {msg.text && (
          <div style={{
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            background: msg.type === 'error' ? 'var(--danger-dim)' : 'var(--success-dim)',
            color: msg.type === 'error' ? 'var(--danger)' : 'var(--success)',
            fontSize: 13,
          }}>
            {msg.type === 'error' ? '⚠ ' : '✓ '}{msg.text}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={saving} style={{ alignSelf: 'flex-start' }}>
          {saving ? 'Saving…' : '💾 Save Settings'}
        </button>
      </form>
    </div>
  )
}
