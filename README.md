# FluxSort 🌊✨

> Transform your cluttered Downloads folder into organized beauty with terminal aesthetics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

FluxSort is a **CLI-first file organization tool** that brings the aesthetic appeal of modern terminal applications to file management. Inspired by tools like `btop`, `lazygit`, and `ranger`, FluxSort makes organizing your digital chaos both functional and visually delightful.

## ✨ Features

### 🚀 Core Functionality
- **Interactive menu-driven interface** with guided workflow
- **Lightning-fast file scanning** with beautiful progress indicators
- **14 intelligent file categories** covering all common file types
- **Safe immediate-directory scanning** (protects existing organized folders)
- **Complete preview system** - see exactly what will happen before any changes
- **Comprehensive undo functionality** with operation history and selective reversal
- **Cross-platform** support (Windows, macOS, Linux)

### 🎨 Beautiful Interface
- **Stunning ASCII banner** with neon terminal aesthetics
- **Interactive menus** with emoji icons and intuitive navigation
- **Real-time progress tracking** with animated progress bars
- **Color-coded file categories** for easy visual identification
- **Detailed operation summaries** with file counts, sizes, and timing

### 🛡️ Advanced Safety Features
- **Preview-first workflow** - always see changes before applying
- **Immediate directory only** - never touches files in subdirectories
- **Smart conflict resolution** with automatic file renaming
- **Complete operation logging** for full audit trail
- **Permission error handling** with graceful fallbacks
- **Hidden file detection** with optional inclusion
- **Confirmation prompts** for all destructive operations

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- No external dependencies (uses only Python standard library)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/FluxSort.git
cd FluxSort

# Make the script executable (optional)
chmod +x flux_sort.py
```

### Basic Usage

**FluxSort now features a beautiful interactive interface! Simply run the script and follow the guided prompts.**

1. **Launch FluxSort**:
   ```bash
   python /path/to/flux_sort.py
   ```

2. **Follow the interactive workflow**:
   - 🏠 **Choose your directory** (current directory or custom path)
   - 📁 **View directory contents** (files and folders preview)
   - 🔍 **Automatic scanning** (immediate directory files only)
   - 🎛️ **Select your action** from the main menu

3. **Main Menu Options**:
   - **Option 1**: 👁️ **Preview Mode** - See what would be organized (safe preview)
   - **Option 2**: 🚀 **Organize Files** - Move files for real (with confirmation)
   - **Option 3**: ↩️ **View & Revert** - Undo any previous operations
   - **Option 4**: 🔄 **Change Directory** - Switch to a different folder
   - **Option 5**: ❌ **Exit** - Close FluxSort

4. **Example workflow**:
   ```bash
   # Run FluxSort
   python flux_sort.py
   
   # Choose directory (e.g., Downloads)
   # View file listing and scan results
   # Select Option 1 to preview organization
   # Select Option 2 to actually organize files
   # Optionally use Option 3 to undo if needed
   ```

## 📊 File Categories

FluxSort intelligently categorizes files into 14 distinct categories:

| Category | Icon | File Types | Examples |
|----------|------|------------|----------|
| **Images** | 🖼️ | JPG, PNG, GIF, SVG, WebP, RAW | photos, screenshots, graphics |
| **Videos** | 🎬 | MP4, AVI, MKV, MOV, WebM | movies, tutorials, recordings |
| **Documents** | 📄 | PDF, DOC, TXT, MD, XLS | reports, notes, spreadsheets |
| **Audio** | 🎵 | MP3, WAV, FLAC, AAC | music, podcasts, recordings |
| **Archives** | 📦 | ZIP, RAR, 7Z, TAR | compressed files, backups |
| **Code** | 💻 | PY, JS, CPP, HTML | source code, scripts |
| **System** | ⚙️ | EXE, ISO, DMG | executables, disk images |
| **Mobile** | 📱 | APK, IPA | mobile applications |
| **Web** | 🌐 | HTML, CSS | web development files |
| **Data** | 📊 | JSON, XML, CSV | data and configuration files |
| **Fonts** | 🔤 | TTF, OTF, WOFF | typography files |
| **3D Models** | 🎮 | OBJ, FBX, STL | 3D modeling files |
| **Ebooks** | 📚 | EPUB, MOBI | digital books |
| **Miscellaneous** | ❓ | * | unrecognized file types |

## 📁 Output Structure

After running FluxSort, your directory will be beautifully organized:

```
Downloads/
├── Images/
│   ├── vacation_photo.jpg
│   ├── screenshot.png
│   └── diagram.svg
├── Videos/
│   ├── tutorial.mp4
│   └── meeting_recording.mov
├── Documents/
│   ├── important_report.pdf
│   ├── meeting_notes.txt
│   └── budget_spreadsheet.xlsx
├── Audio/
│   ├── favorite_podcast.mp3
│   └── music_collection.flac
├── Archives/
│   ├── project_backup.zip
│   └── source_code.tar.gz
├── Code/
│   ├── automation_script.py
│   └── website_template.html
└── Miscellaneous/
    └── unknown_file.xyz
```

## 🛠️ How to Use FluxSort

### Interactive Mode (Recommended)
```bash
python flux_sort.py
```
FluxSort will launch with a beautiful interactive interface that guides you through:
- **Path selection** (current directory or custom path)
- **Directory preview** (see files and folders before scanning)
- **File scanning** (immediate directory only, protects subdirectories)
- **Menu options** (preview, organize, undo, or change directory)

### Legacy Command Line Options
For backwards compatibility, you can still use command line arguments:
```bash
python flux_sort.py [OPTIONS]

Options:
  -d, --directory PATH    Directory to organize (default: current directory)
  --dry-run              Preview changes without moving files (default: True)
  --no-dry-run           Actually move files instead of just previewing
  -v, --verbose          Show detailed progress and information
  --help                 Show this message and exit
```

**⚠️ Note**: The interactive mode is much safer and more user-friendly than command line options!

## 🔧 Advanced Usage

### Configuration
FluxSort automatically creates configuration files in your system's config directory:
- **Windows**: `%APPDATA%\fluxsort\fluxsort.json`
- **macOS**: `~/Library/Application Support/fluxsort/fluxsort.json`
- **Linux**: `~/.config/fluxsort/fluxsort.json`

### Safety Features
- **Always use dry-run first**: Never skip the preview step
- **Conflict resolution**: Files with same names are automatically renamed
- **Operation history**: All moves are logged for potential undo operations
- **Error handling**: Graceful handling of permission issues and file locks

## 🗺️ Project Roadmap

FluxSort follows a phased development approach:

### ✅ Phase 1: Basic Sorting Script (Completed)
- Core file detection and categorization
- Safe immediate-directory scanning
- Comprehensive safety features
- Operation history and logging

### ✅ Phase 1.5: Interactive Interface (Completed)
- **Beautiful menu-driven interface** with ASCII banner
- **Guided workflow** with path selection and directory preview
- **Complete preview system** showing exactly what will be organized
- **Real-time progress tracking** with animated progress bars
- **Comprehensive undo system** with operation history
- **Smart safety features** protecting existing organized folders

### 🔄 Phase 2: Enhanced CLI Interface (Next)
- Rich terminal output with colors and animations
- Command-line interface with Typer framework
- Advanced configuration management
- Watch mode for automatic directory monitoring

### 📅 Phase 3: TUI Interface (Future)
- Interactive terminal UI with Textual
- Arrow key navigation and file browser
- Real-time preview of operations
- Advanced rule customization interface

### 🌟 Phase 4: GUI Interface (Future)
- Desktop application for broader adoption
- Drag-and-drop functionality
- System tray integration
- Visual file previews and thumbnails

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Project Structure
```
FluxSort/
├── src/                    # Core library modules
│   ├── file_detector.py    # File type detection and categorization
│   ├── file_scanner.py     # Directory scanning and analysis
│   ├── file_sorter.py      # File moving operations with safety
│   └── config.py           # Configuration management
├── tests/                  # Test suite
├── examples/               # Usage examples and documentation
├── docs/                   # Project documentation
└── flux_sort.py           # Main executable script
```

## 🤝 Contributing

FluxSort is open-source and welcomes contributions! Whether you're interested in:
- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation and examples
- 🎨 UI/UX improvements

Please feel free to open issues and submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

FluxSort draws inspiration from the beautiful terminal aesthetics of:
- **btop** - Resource monitor with amazing visuals
- **lazygit** - Terminal UI for git commands
- **ranger** - Vim-inspired file manager

---

**Made with ❤️ for developers and power users who appreciate beautiful terminal interfaces**

> *"Transform chaos into organized beauty, one file at a time"* ✨
