import React, { useState, useEffect } from 'react'
import Sidebar from './components/Layout/Sidebar.jsx'
import TopBar from './components/Layout/TopBar.jsx'
import ScanView from './views/ScanView.jsx'
import PreviewView from './views/PreviewView.jsx'
import HistoryView from './views/HistoryView.jsx'
import SetupView from './views/SetupView.jsx'
import SettingsView from './views/SettingsView.jsx'
import { api } from './api/client.js'

export default function App() {
  const [view, setView]             = useState('scan')
  const [serverOnline, setOnline]   = useState(false)
  const [scanResult, setScanResult] = useState(null)   // last completed scan
  const [sortMode, setSortMode]     = useState('standard')
  const [pendingSort, setPending]   = useState(false)

  // Poll server health
  useEffect(() => {
    function check() {
      api.health()
        .then(() => setOnline(true))
        .catch(() => setOnline(false))
    }
    check()
    const id = setInterval(check, 10_000)
    return () => clearInterval(id)
  }, [])

  function handleScanComplete(result, mode) {
    setScanResult(result)
    setSortMode(mode)
    setPending(true)
    setView('preview')
  }

  function handleSortDone() {
    setPending(false)
  }

  const currentPath = scanResult?.directory || ''

  return (
    <div className="app-shell">
      <Sidebar
        view={view}
        onNavigate={setView}
        pendingCount={pendingSort ? 1 : 0}
      />

      <div className="main-content">
        <TopBar
          view={view}
          currentPath={currentPath}
          serverOnline={serverOnline}
        />

        {/* Views */}
        {view === 'scan' && (
          <ScanView onScanComplete={handleScanComplete} />
        )}
        {view === 'preview' && (
          <PreviewView
            scanResult={scanResult}
            sortMode={sortMode}
            onSortDone={handleSortDone}
            onNavigate={setView}
          />
        )}
        {view === 'history' && (
          <HistoryView currentDirectory={currentPath} />
        )}
        {view === 'setup' && (
          <SetupView />
        )}
        {view === 'settings' && (
          <SettingsView />
        )}
      </div>
    </div>
  )
}
