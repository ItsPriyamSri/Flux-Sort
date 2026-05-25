# FluxSort 🌊✨

> A smart, AI-powered file organizer with a clean web UI — cross-platform, local-first, and privacy-respecting.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

FluxSort v2 transforms cluttered directories into organized beauty. Unlike dumb extension-only sorters, it learns **your personal folder taxonomy** — define categories like "Work", "Gaming", "College" — and uses **Gemini AI** to map files into them intelligently.

---

## ✨ What's New in v2

| Feature | Description |
|---|---|
| **Web UI** | Beautiful dark-mode browser interface at `localhost:8765` |
| **AI Smart Sort** | Gemini 3.1 Flash Lite classifies files against your custom categories |
| **Custom Taxonomy** | Define your own folder system with descriptions, icons, and colors |
| **Human-in-the-loop** | AI proposes, you review and approve — files never move without you |
| **30-day AI cache** | Same files aren't re-classified on repeat runs |
| **Full Undo** | Every operation is logged; one-click revert from the History tab |

---

## 🏗️ Architecture

```
Browser (localhost:8765)
    │  HTTP / WebSocket
    ▼
FastAPI server (src/api/)        ← thin adapter, zero business logic
    │  Python function calls
    ▼
Core (src/)                      ← unchanged from v1
  file_detector.py  →  extension map (fast path, zero API calls)
  file_scanner.py   →  directory traversal + manifest builder
  file_sorter.py    →  file moves + collision handling + undo history
  config.py         →  settings + taxonomy + API key (local only)
    │
    ▼
AI Classifier (src/ai_classifier.py)
  gemini-3.1-flash-lite  ←  only called for ambiguous/unknown files
  30-day local cache     ←  ~/.config/fluxsort/ai_cache.json
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for the web UI)
- A Gemini API key (optional — AI features degrade gracefully without one)

### Install

```bash
git clone https://github.com/ItsPriyamSri/Flux-Sort.git
cd Flux-Sort
pip install -e .
```

This installs all Python dependencies and registers two CLI commands:
- `fluxsort` — the original interactive CLI (unchanged)
- `fluxsort-serve` — starts the web UI

### Build the Frontend (one-time)

```bash
cd frontend
npm install
npm run build
cd ..
```

### Run

**Option A — Production (single command)**
```bash
fluxsort-serve
# → Opens http://localhost:8765 in your browser automatically
```

**Option B — Dev mode (hot-reload frontend)**
```bash
# Terminal 1
python -m uvicorn src.api.server:app --port 8765

# Terminal 2
cd frontend && npm run dev
# → Open http://localhost:5173
```

**Option C — Legacy CLI (no UI needed)**
```bash
fluxsort
```

---

## 🧭 Web UI Walkthrough

### 1. Scan & Sort
Choose a directory (quick-select Downloads, Desktop, or type a custom path).  
Hit **⚡ Scan** — watch the live progress bar fill as files are discovered.  
Then choose your sort mode:
- **👁️ Preview & Sort** — standard extension-based categories
- **🤖 AI Smart Sort** — uses your custom taxonomy + Gemini

### 2. Preview
Review the sort plan before anything is moved.  
Each file is shown in its target category column.  
AI-classified files show a confidence badge (green ✓ / amber ⚠).  
**Reassign any file** by changing its category in the dropdown.  
Click **✓ Execute Sort** when you're happy — a confirmation step protects you.

### 3. History
Every sort operation is logged with a full file list.  
Click **↩ Undo** on any past operation to move all its files back instantly.

### 4. My Categories
Define your personal folder taxonomy for AI Smart Sort:
- Give each category a name, description, color, and icon
- The description is what the AI reads to make decisions — be specific
- Example: `Work` → *"PDFs from college, project proposals, meeting notes, invoices, spreadsheets"*

### 5. Settings
- Paste your **Gemini API key** (stored locally at `~/.config/fluxsort/fluxsort.json`, never transmitted except to Google's API directly)
- Configure the **weekly scheduler** (day + time)
- Set your **conflict resolution strategy** (rename / skip / overwrite)

---

## 📊 File Categories (Extension-Map Mode)

| Category | Examples |
|---|---|
| 🖼️ Images | jpg, png, svg, heic, raw, webp |
| 🎬 Videos | mp4, mkv, mov, avi, webm |
| 📄 Documents | pdf, docx, txt, md, xlsx, pptx |
| 🎵 Audio | mp3, flac, wav, aac, ogg |
| 📦 Archives | zip, rar, 7z, tar.gz |
| 💻 Code | py, js, ts, go, rs, cpp, sh |
| ⚙️ System | exe, iso, dmg, deb, appimage |
| 📱 Mobile | apk, ipa, aab |
| 🌐 Web | html, css, scss |
| 📊 Data | json, yaml, sql, db, csv |
| 🔤 Fonts | ttf, otf, woff2 |
| 🎮 3D Models | obj, fbx, stl, blend |
| 📚 Ebooks | epub, mobi, azw3 |
| ❓ Miscellaneous | everything else |

---

## 🔑 Gemini API Key

1. Get a free key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Open FluxSort → **Settings** → paste key → **Save Settings**
3. Your key is stored at `~/.config/fluxsort/fluxsort.json` — never committed, never sent anywhere except Google's API

> Without a key, FluxSort falls back to extension-map sorting silently. All other features work normally.

---

## 🛡️ Safety Guarantees

- **No file moves without approval** — the Preview screen is always shown first
- **Immediate-directory only** — never touches files inside sub-folders
- **Full undo** — every move is logged to `.fluxsort_history.json` in the sorted directory
- **Conflict handling** — duplicate filenames are auto-renamed (`file (1).txt`) by default
- **AI cache** — 30-day local cache means the same files aren't re-sent to Gemini on repeat runs

---

## 🗂️ Project Structure

```
Flux-Sort/
├── src/                        # Core Python modules
│   ├── file_detector.py        # Extension-map classifier (14 categories)
│   ├── file_scanner.py         # Directory traversal + ScanResult
│   ├── file_sorter.py          # File moves + undo history (.fluxsort_history.json)
│   ├── config.py               # Config + TaxonomyCategory dataclass
│   ├── ai_classifier.py        # Gemini 3.1 Flash Lite + local cache
│   └── api/                    # FastAPI adapter layer
│       ├── server.py           # App + CORS + static file serving
│       ├── models.py           # Pydantic v2 request/response models
│       └── routes/             # scan, sort, history, taxonomy, settings, ai, browse
├── frontend/                   # React 18 + Vite 5
│   ├── src/
│   │   ├── views/              # ScanView, PreviewView, SetupView, HistoryView, SettingsView
│   │   ├── components/Layout/  # Sidebar, TopBar
│   │   └── api/client.js       # All fetch + WebSocket calls
│   └── dist/                   # Production build (gitignored, run npm run build)
├── tests/
│   └── test_file_detector.py   # Existing unit tests (still pass)
├── flux_sort.py                # Legacy interactive CLI (unchanged)
├── fluxsort_serve.py           # Web UI entry point
└── pyproject.toml              # Package config + entry points
```

---

## 🗺️ Roadmap

### ✅ Phase 1 — CLI (Complete)
Extension-map sorting, preview, undo, cross-platform CLI

### ✅ Phase 2 — Web UI + AI (Complete)
FastAPI backend, React frontend, Gemini AI classifier, custom taxonomy, weekly scheduler config

### 🔄 Phase 3 — Scheduler (Next)
Background scheduler that auto-scans watched folders weekly and queues files for review without moving them

### 📅 Phase 4 — Packaging
PyInstaller single-binary for Windows / macOS / Linux (no Python required)

### 🌟 Phase 5 — Tauri Native App
Wrap the React frontend in a Tauri shell for a proper native desktop experience (~5 MB binary, system tray, OS notifications)

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

*"FluxSort learns how **you** think about your files — not how a generic algorithm does."* 🌊
