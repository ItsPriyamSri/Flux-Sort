import React, { useState, useEffect } from 'react'
import { api } from '../api/client.js'

const COLORS = ['#3B82F6','#10B981','#F59E0B','#EF4444','#8B5CF6','#EC4899','#06B6D4','#84CC16']
const ICONS  = ['📁','💼','🎮','🎵','📚','🎬','💻','🏠','🖼️','📦','⚡','🎯','🔬','✈️']

function CategoryForm({ initial, onSave, onCancel }) {
  const [name, setName]     = useState(initial?.name || '')
  const [desc, setDesc]     = useState(initial?.description || '')
  const [color, setColor]   = useState(initial?.color || COLORS[0])
  const [icon, setIcon]     = useState(initial?.icon || '📁')
  const [folder, setFolder] = useState(initial?.folder_name || '')
  const [saving, setSaving] = useState(false)
  const [err, setErr]       = useState('')

  // Auto-generate folder name from category name
  useEffect(() => {
    if (!initial && name && !folder) setFolder(name.trim())
  }, [name])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim() || !desc.trim() || !folder.trim()) {
      setErr('All fields are required.')
      return
    }
    setSaving(true)
    setErr('')
    try {
      await onSave({ name: name.trim(), description: desc.trim(), color, icon, folder_name: folder.trim() })
    } catch (e) { setErr(e.message) }
    setSaving(false)
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>
            Category Name *
          </label>
          <input className="input" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Work" />
        </div>
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>
            Folder Name *
          </label>
          <input className="input input-mono" value={folder} onChange={e => setFolder(e.target.value)} placeholder="e.g. Work" />
        </div>
      </div>

      <div>
        <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>
          Description * <span className="text-muted">(AI uses this to classify files)</span>
        </label>
        <textarea
          className="input"
          rows={2}
          value={desc}
          onChange={e => setDesc(e.target.value)}
          placeholder='e.g. "Work PDFs, project files, spreadsheets, meeting notes"'
          style={{ resize: 'vertical', minHeight: 64 }}
        />
      </div>

      <div style={{ display: 'flex', gap: 20 }}>
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>Color</label>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {COLORS.map(c => (
              <button
                key={c} type="button"
                onClick={() => setColor(c)}
                style={{
                  width: 22, height: 22, borderRadius: '50%', background: c, border: 'none',
                  cursor: 'pointer', outline: color === c ? `2px solid white` : 'none',
                  outlineOffset: 2, transition: 'transform 0.1s',
                }}
              />
            ))}
          </div>
        </div>
        <div>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 5 }}>Icon</label>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {ICONS.map(ic => (
              <button
                key={ic} type="button"
                onClick={() => setIcon(ic)}
                style={{
                  width: 28, height: 28, borderRadius: 6, border: 'none',
                  background: icon === ic ? 'var(--accent-dim)' : 'var(--bg-elevated)',
                  cursor: 'pointer', fontSize: 14,
                  outline: icon === ic ? '1px solid var(--accent)' : 'none',
                }}
              >
                {ic}
              </button>
            ))}
          </div>
        </div>
      </div>

      {err && <div style={{ color: 'var(--danger)', fontSize: 12 }}>⚠ {err}</div>}

      <div style={{ display: 'flex', gap: 10 }}>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : initial ? '💾 Update' : '➕ Add Category'}
        </button>
        <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}

function CategoryCard({ cat, onEdit, onDelete }) {
  return (
    <div className="glass-card" style={{ padding: '16px 18px', display: 'flex', alignItems: 'flex-start', gap: 14 }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10, background: cat.color + '22',
        border: `1.5px solid ${cat.color}44`, display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: 20, flexShrink: 0,
      }}>
        {cat.icon}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 2, display: 'flex', alignItems: 'center', gap: 8 }}>
          {cat.name}
          <span className="font-mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>→ {cat.folder_name}/</span>
        </div>
        <div className="text-secondary" style={{ fontSize: 12, lineHeight: 1.5 }}>{cat.description}</div>
      </div>
      <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => onEdit(cat)}>Edit</button>
        <button className="btn btn-danger btn-sm" onClick={() => onDelete(cat.id)}>✕</button>
      </div>
    </div>
  )
}

export default function SetupView() {
  const [taxonomy, setTaxonomy] = useState([])
  const [loading, setLoading]   = useState(true)
  const [adding, setAdding]     = useState(false)
  const [editing, setEditing]   = useState(null)
  const [error, setError]       = useState('')

  function load() {
    setLoading(true)
    api.getTaxonomy()
      .then(r => { setTaxonomy(r.taxonomy || []); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }
  useEffect(load, [])

  async function handleAdd(body) {
    await api.createCategory(body)
    setAdding(false)
    load()
  }

  async function handleUpdate(body) {
    await api.updateCategory(editing.id, body)
    setEditing(null)
    load()
  }

  async function handleDelete(id) {
    if (!confirm('Remove this category?')) return
    await api.deleteCategory(id)
    load()
  }

  return (
    <div className="view-body fade-in">
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>My Categories</h1>
        <p className="text-secondary" style={{ fontSize: 13.5 }}>
          Define your personal folder taxonomy. The AI uses your descriptions to decide what goes where.
        </p>
      </div>

      {error && <div className="text-danger" style={{ marginBottom: 16 }}>⚠ {error}</div>}

      {/* Add form */}
      {adding && (
        <div className="glass-card fade-in" style={{ padding: '20px 22px', marginBottom: 20, borderColor: 'var(--border-accent)' }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>➕ New Category</h3>
          <CategoryForm onSave={handleAdd} onCancel={() => setAdding(false)} />
        </div>
      )}

      {/* Edit form */}
      {editing && (
        <div className="glass-card fade-in" style={{ padding: '20px 22px', marginBottom: 20, borderColor: 'var(--border-accent)' }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>✏️ Edit Category</h3>
          <CategoryForm initial={editing} onSave={handleUpdate} onCancel={() => setEditing(null)} />
        </div>
      )}

      {/* List */}
      {loading ? (
        <div style={{ display: 'flex', gap: 10, color: 'var(--text-secondary)' }}>
          <span className="spin">⟳</span> Loading…
        </div>
      ) : taxonomy.length === 0 && !adding ? (
        <div className="empty-state" style={{ marginBottom: 32 }}>
          <div className="empty-icon">🏷️</div>
          <h3>No categories yet</h3>
          <p>Create your first category to enable AI Smart Sort.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 24 }}>
          {taxonomy.map(cat => (
            <CategoryCard
              key={cat.id}
              cat={cat}
              onEdit={c => { setAdding(false); setEditing(c) }}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {!adding && !editing && (
        <button className="btn btn-primary" onClick={() => { setEditing(null); setAdding(true) }}>
          ➕ Add Category
        </button>
      )}

      {taxonomy.length > 0 && (
        <div className="glass-card" style={{ padding: '14px 18px', marginTop: 24, borderColor: 'var(--success-dim)' }}>
          <p className="text-secondary" style={{ fontSize: 12.5 }}>
            💡 <strong style={{ color: 'var(--text-primary)' }}>Tip:</strong> Write detailed descriptions.
            Instead of <em>"work files"</em>, write <em>"PDFs from college, project proposals, meeting notes, invoices"</em>.
            The AI uses this to make better decisions.
          </p>
        </div>
      )}
    </div>
  )
}
