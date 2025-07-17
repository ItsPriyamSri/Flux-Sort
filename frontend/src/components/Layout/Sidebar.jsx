import React from 'react'
import './Sidebar.css'

const NAV_ITEMS = [
  { id: 'scan',     icon: '⚡', label: 'Scan & Sort' },
  { id: 'preview',  icon: '👁️', label: 'Preview' },
  { id: 'history',  icon: '🕐', label: 'History' },
  { id: 'setup',    icon: '🏷️', label: 'My Categories' },
  { id: 'settings', icon: '⚙️', label: 'Settings' },
]

export default function Sidebar({ view, onNavigate, pendingCount = 0 }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">🌊</div>
          <div>
            <div className="logo-text">FluxSort</div>
            <div className="logo-version">v2.0</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            className={`nav-item ${view === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {item.id === 'preview' && pendingCount > 0 && (
              <span className="nav-badge">{pendingCount}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          className={`nav-item ${view === 'settings' ? 'active' : ''}`}
          style={{ color: 'var(--text-muted)', fontSize: '12px' }}
          onClick={() => onNavigate('settings')}
        >
          <span className="nav-icon">🔑</span>
          <span className="nav-label">API Key</span>
        </button>
      </div>
    </aside>
  )
}
