import React from 'react'
import './TopBar.css'

const VIEW_TITLES = {
  scan:     'Scan & Sort',
  preview:  'Sort Preview',
  history:  'Operation History',
  setup:    'My Categories',
  settings: 'Settings',
}

export default function TopBar({ view, currentPath, serverOnline }) {
  return (
    <header className="topbar">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <span className="topbar-title">{VIEW_TITLES[view] || view}</span>
        {currentPath && (
          <span className="topbar-subtitle" title={currentPath}>{currentPath}</span>
        )}
      </div>

      <div className="topbar-right">
        <div className="topbar-status">
          <div className={`status-dot ${serverOnline ? 'online' : 'error'}`} />
          <span>{serverOnline ? 'Server running' : 'Server offline'}</span>
        </div>
      </div>
    </header>
  )
}
