"""File type detection and categorization module for FluxSort."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class FileCategory(Enum):
    """File categories for organization."""
    IMAGES = "Images"
    VIDEOS = "Videos"
    DOCUMENTS = "Documents"
    AUDIO = "Audio"
    ARCHIVES = "Archives"
    CODE = "Code"
    SYSTEM = "System"
    MOBILE = "Mobile"
    WEB = "Web"
    DATA = "Data"
    FONTS = "Fonts"
    MODELS_3D = "3D Models"
    EBOOKS = "Ebooks"
    MISCELLANEOUS = "Miscellaneous"


@dataclass
class FileInfo:
    """Information about a detected file."""
    path: Path
    name: str
    extension: str
    size: int
    category: FileCategory
    
    @property
    def size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.size / (1024 * 1024), 2)


class FileTypeDetector:
    """Detects and categorizes files based on their extensions."""
    
    def __init__(self):
        """Initialize the file type detector with categorization rules."""
        self.extension_map: Dict[str, FileCategory] = {
            # Images
            '.jpg': FileCategory.IMAGES,
            '.jpeg': FileCategory.IMAGES,
            '.png': FileCategory.IMAGES,
            '.gif': FileCategory.IMAGES,
            '.bmp': FileCategory.IMAGES,
            '.svg': FileCategory.IMAGES,
            '.webp': FileCategory.IMAGES,
            '.ico': FileCategory.IMAGES,
            '.tiff': FileCategory.IMAGES,
            '.tif': FileCategory.IMAGES,
            '.heic': FileCategory.IMAGES,
            '.heif': FileCategory.IMAGES,
            '.raw': FileCategory.IMAGES,
            '.cr2': FileCategory.IMAGES,
            '.nef': FileCategory.IMAGES,
            '.arw': FileCategory.IMAGES,
            '.dng': FileCategory.IMAGES,
            
            # Videos
            '.mp4': FileCategory.VIDEOS,
            '.avi': FileCategory.VIDEOS,
            '.mkv': FileCategory.VIDEOS,
            '.mov': FileCategory.VIDEOS,
            '.wmv': FileCategory.VIDEOS,
            '.flv': FileCategory.VIDEOS,
            '.webm': FileCategory.VIDEOS,
            '.m4v': FileCategory.VIDEOS,
            '.3gp': FileCategory.VIDEOS,
            '.mpeg': FileCategory.VIDEOS,
            '.mpg': FileCategory.VIDEOS,
            '.ogv': FileCategory.VIDEOS,
            '.ts': FileCategory.VIDEOS,
            '.vob': FileCategory.VIDEOS,
            
            # Documents
            '.pdf': FileCategory.DOCUMENTS,
            '.doc': FileCategory.DOCUMENTS,
            '.docx': FileCategory.DOCUMENTS,
            '.txt': FileCategory.DOCUMENTS,
            '.rtf': FileCategory.DOCUMENTS,
            '.odt': FileCategory.DOCUMENTS,
            '.pages': FileCategory.DOCUMENTS,
            '.md': FileCategory.DOCUMENTS,
            '.markdown': FileCategory.DOCUMENTS,
            '.rst': FileCategory.DOCUMENTS,
            '.tex': FileCategory.DOCUMENTS,
            '.ppt': FileCategory.DOCUMENTS,
            '.pptx': FileCategory.DOCUMENTS,
            '.odp': FileCategory.DOCUMENTS,
            '.xls': FileCategory.DOCUMENTS,
            '.xlsx': FileCategory.DOCUMENTS,
            '.ods': FileCategory.DOCUMENTS,
            '.csv': FileCategory.DOCUMENTS,
            
            # Audio
            '.mp3': FileCategory.AUDIO,
            '.wav': FileCategory.AUDIO,
            '.flac': FileCategory.AUDIO,
            '.aac': FileCategory.AUDIO,
            '.ogg': FileCategory.AUDIO,
            '.wma': FileCategory.AUDIO,
            '.m4a': FileCategory.AUDIO,
            '.opus': FileCategory.AUDIO,
            '.aiff': FileCategory.AUDIO,
            '.au': FileCategory.AUDIO,
            '.ra': FileCategory.AUDIO,
            
            # Archives
            '.zip': FileCategory.ARCHIVES,
            '.rar': FileCategory.ARCHIVES,
            '.7z': FileCategory.ARCHIVES,
            '.tar': FileCategory.ARCHIVES,
            '.gz': FileCategory.ARCHIVES,
            '.bz2': FileCategory.ARCHIVES,
            '.xz': FileCategory.ARCHIVES,
            '.tar.gz': FileCategory.ARCHIVES,
            '.tar.bz2': FileCategory.ARCHIVES,
            '.tar.xz': FileCategory.ARCHIVES,
            '.dmg': FileCategory.ARCHIVES,
            '.pkg': FileCategory.ARCHIVES,
            '.deb': FileCategory.ARCHIVES,
            '.rpm': FileCategory.ARCHIVES,
            
            # Code
            '.py': FileCategory.CODE,
            '.js': FileCategory.CODE,
            '.ts': FileCategory.CODE,
            '.jsx': FileCategory.CODE,
            '.tsx': FileCategory.CODE,
            '.java': FileCategory.CODE,
            '.c': FileCategory.CODE,
            '.cpp': FileCategory.CODE,
            '.cc': FileCategory.CODE,
            '.cxx': FileCategory.CODE,
            '.h': FileCategory.CODE,
            '.hpp': FileCategory.CODE,
            '.cs': FileCategory.CODE,
            '.php': FileCategory.CODE,
            '.rb': FileCategory.CODE,
            '.go': FileCategory.CODE,
            '.rs': FileCategory.CODE,
            '.swift': FileCategory.CODE,
            '.kt': FileCategory.CODE,
            '.scala': FileCategory.CODE,
            '.pl': FileCategory.CODE,
            '.sh': FileCategory.CODE,
            '.bat': FileCategory.CODE,
            '.ps1': FileCategory.CODE,
            '.r': FileCategory.CODE,
            '.m': FileCategory.CODE,
            '.lua': FileCategory.CODE,
            '.vim': FileCategory.CODE,
            
            # System
            '.iso': FileCategory.SYSTEM,
            '.img': FileCategory.SYSTEM,
            '.exe': FileCategory.SYSTEM,
            '.msi': FileCategory.SYSTEM,
            '.app': FileCategory.SYSTEM,
            '.deb': FileCategory.SYSTEM,
            '.rpm': FileCategory.SYSTEM,
            '.snap': FileCategory.SYSTEM,
            '.appimage': FileCategory.SYSTEM,
            '.flatpak': FileCategory.SYSTEM,
            '.dll': FileCategory.SYSTEM,
            '.so': FileCategory.SYSTEM,
            '.dylib': FileCategory.SYSTEM,
            
            # Mobile
            '.apk': FileCategory.MOBILE,
            '.ipa': FileCategory.MOBILE,
            '.aab': FileCategory.MOBILE,
            '.xap': FileCategory.MOBILE,
            
            # Web
            '.html': FileCategory.WEB,
            '.htm': FileCategory.WEB,
            '.css': FileCategory.WEB,
            '.scss': FileCategory.WEB,
            '.sass': FileCategory.WEB,
            '.less': FileCategory.WEB,
            '.xml': FileCategory.WEB,
            '.xsl': FileCategory.WEB,
            '.xslt': FileCategory.WEB,
            '.rss': FileCategory.WEB,
            '.atom': FileCategory.WEB,
            
            # Data
            '.json': FileCategory.DATA,
            '.yaml': FileCategory.DATA,
            '.yml': FileCategory.DATA,
            '.toml': FileCategory.DATA,
            '.ini': FileCategory.DATA,
            '.cfg': FileCategory.DATA,
            '.conf': FileCategory.DATA,
            '.sql': FileCategory.DATA,
            '.db': FileCategory.DATA,
            '.sqlite': FileCategory.DATA,
            '.sqlite3': FileCategory.DATA,
            '.mdb': FileCategory.DATA,
            '.accdb': FileCategory.DATA,
            
            # Fonts
            '.ttf': FileCategory.FONTS,
            '.otf': FileCategory.FONTS,
            '.woff': FileCategory.FONTS,
            '.woff2': FileCategory.FONTS,
            '.eot': FileCategory.FONTS,
            '.fon': FileCategory.FONTS,
            
            # 3D Models
            '.obj': FileCategory.MODELS_3D,
            '.fbx': FileCategory.MODELS_3D,
            '.dae': FileCategory.MODELS_3D,
            '.3ds': FileCategory.MODELS_3D,
            '.blend': FileCategory.MODELS_3D,
            '.stl': FileCategory.MODELS_3D,
            '.ply': FileCategory.MODELS_3D,
            '.x3d': FileCategory.MODELS_3D,
            
            # Ebooks
            '.epub': FileCategory.EBOOKS,
            '.mobi': FileCategory.EBOOKS,
            '.azw': FileCategory.EBOOKS,
            '.azw3': FileCategory.EBOOKS,
            '.fb2': FileCategory.EBOOKS,
            '.lit': FileCategory.EBOOKS,
            '.pdb': FileCategory.EBOOKS,
        }
        
        # Create reverse mapping for category lookups
        self.category_extensions: Dict[FileCategory, Set[str]] = {}
        for ext, category in self.extension_map.items():
            if category not in self.category_extensions:
                self.category_extensions[category] = set()
            self.category_extensions[category].add(ext)
    
    def detect_file_category(self, file_path: Path) -> FileCategory:
        """
        Detect the category of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileCategory enum value
        """
        extension = file_path.suffix.lower()
        
        # Handle compound extensions like .tar.gz
        if file_path.name.lower().endswith('.tar.gz'):
            extension = '.tar.gz'
        elif file_path.name.lower().endswith('.tar.bz2'):
            extension = '.tar.bz2'
        elif file_path.name.lower().endswith('.tar.xz'):
            extension = '.tar.xz'
        
        return self.extension_map.get(extension, FileCategory.MISCELLANEOUS)
    
    def get_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """
        Get comprehensive information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object or None if file doesn't exist
        """
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            stat = file_path.stat()
            category = self.detect_file_category(file_path)
            
            return FileInfo(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size=stat.st_size,
                category=category
            )
        except (OSError, PermissionError):
            return None
    
    def get_category_extensions(self, category: FileCategory) -> Set[str]:
        """
        Get all extensions for a given category.
        
        Args:
            category: FileCategory to get extensions for
            
        Returns:
            Set of extensions (including the dot)
        """
        return self.category_extensions.get(category, set())
    
    def get_all_categories(self) -> List[FileCategory]:
        """Get all available file categories."""
        return list(FileCategory)
    
    def is_hidden_file(self, file_path: Path) -> bool:
        """
        Check if a file is hidden (starts with dot on Unix or has hidden attribute on Windows).
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is hidden
        """
        if file_path.name.startswith('.'):
            return True
        
        # On Windows, check the hidden attribute
        if os.name == 'nt':
            try:
                import stat
                return bool(file_path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                pass
        
        return False