/**
 * Thin API client — all fetch calls go through here.
 * In dev, Vite proxies /api → http://localhost:8765
 * In production, FastAPI serves everything from one origin.
 */

const BASE = '/api'

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== null) opts.body = JSON.stringify(body)

  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  health: ()                        => request('GET', '/health'),

  // Browse
  browse: (path = '')              => request('GET', `/directory/browse?path=${encodeURIComponent(path)}`),
  defaults: ()                      => request('GET', '/directory/defaults'),

  // Scan
  startScan: (directory, includeHidden = false) =>
    request('POST', '/scan', { directory, include_hidden: includeHidden }),
  getScan: (scanId)                 => request('GET', `/scan/${scanId}`),

  // AI classify
  classify: (scanId, taxonomyIds = []) =>
    request('POST', '/classify', { scan_id: scanId, taxonomy_ids: taxonomyIds }),

  // Sort
  previewSort: (scanId)            => request('GET', `/sort/preview/${scanId}`),
  executeSort: (scanId, moves)     => request('POST', '/sort/execute', { scan_id: scanId, moves }),

  // History
  getHistory: (directory = '', limit = 50) =>
    request('GET', `/history?directory=${encodeURIComponent(directory)}&limit=${limit}`),
  undoOperation: (opId, directory = '') =>
    request('POST', `/history/undo/${opId}?directory=${encodeURIComponent(directory)}`),

  // Taxonomy
  getTaxonomy: ()                   => request('GET', '/taxonomy'),
  createCategory: (body)            => request('POST', '/taxonomy', body),
  updateCategory: (id, body)        => request('PUT', `/taxonomy/${id}`, body),
  deleteCategory: (id)              => request('DELETE', `/taxonomy/${id}`),

  // Settings
  getSettings: ()                   => request('GET', '/settings'),
  updateSettings: (body)            => request('PUT', '/settings', body),
  clearApiKey: ()                   => request('DELETE', '/settings/api-key'),
}

/**
 * Open a WebSocket for scan progress events.
 * Returns an object with a `close()` method.
 */
export function openProgressSocket(scanId, { onProgress, onDone, onError }) {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host  = import.meta.env.DEV ? 'localhost:8765' : window.location.host
  const ws    = new WebSocket(`${proto}://${host}/ws/progress/${scanId}`)

  ws.onmessage = (e) => {
    const ev = JSON.parse(e.data)
    if (ev.type === 'progress') onProgress?.(ev)
    if (ev.type === 'done')     onDone?.(ev)
    if (ev.type === 'error')    onError?.(ev)
  }
  ws.onerror = () => onError?.({ message: 'WebSocket error' })

  return { close: () => ws.close() }
}
