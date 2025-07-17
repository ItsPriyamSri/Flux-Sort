"""Configuration management for FluxSort."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os

from .file_detector import FileCategory


@dataclass
class FluxSortConfig:
    """FluxSort configuration settings."""
    
    # File handling settings
    include_hidden_files: bool = False
    max_scan_depth: Optional[int] = None
    conflicts_strategy: str = "rename"  # rename, skip, overwrite
    
    # Category folder names
    category_folders: Dict[str, str] = None
    
    # File patterns to include/exclude
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    
    # Custom file type mappings
    custom_extensions: Dict[str, str] = None
    
    # Safety settings
    require_confirmation: bool = True
    auto_backup: bool = False
    max_file_size_mb: Optional[int] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.category_folders is None:
            self.category_folders = {
                FileCategory.IMAGES.value: "Images",
                FileCategory.VIDEOS.value: "Videos", 
                FileCategory.DOCUMENTS.value: "Documents",
                FileCategory.AUDIO.value: "Audio",
                FileCategory.ARCHIVES.value: "Archives",
                FileCategory.CODE.value: "Code",
                FileCategory.SYSTEM.value: "System Files",
                FileCategory.MOBILE.value: "Mobile Apps",
                FileCategory.WEB.value: "Web Files",
                FileCategory.DATA.value: "Data Files",
                FileCategory.FONTS.value: "Fonts",
                FileCategory.MODELS_3D.value: "3D Models",
                FileCategory.EBOOKS.value: "Ebooks",
                FileCategory.MISCELLANEOUS.value: "Miscellaneous"
            }
        
        if self.include_patterns is None:
            self.include_patterns = []
        
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        
        if self.custom_extensions is None:
            self.custom_extensions = {}


class ConfigManager:
    """Manages FluxSort configuration files."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store config files (default: user config dir)
        """
        if config_dir is None:
            config_dir = self._get_default_config_dir()
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "fluxsort.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config: Optional[FluxSortConfig] = None
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory for the current OS."""
        if os.name == 'nt':  # Windows
            base = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif os.name == 'posix':  # macOS and Linux
            if 'darwin' in os.uname().sysname.lower():  # macOS
                base = Path.home() / 'Library' / 'Application Support'
            else:  # Linux
                base = Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config'))
        else:
            base = Path.home() / '.fluxsort'
        
        return base / 'fluxsort'
    
    def load_config(self) -> FluxSortConfig:
        """
        Load configuration from file or create default.
        
        Returns:
            FluxSortConfig object
        """
        if self._config is not None:
            return self._config
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self._config = FluxSortConfig(**config_data)
                return self._config
            
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration.")
        
        # Create default config
        self._config = FluxSortConfig()
        self.save_config(self._config)
        return self._config
    
    def save_config(self, config: FluxSortConfig) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            
        Returns:
            True if saved successfully
        """
        try:
            config_data = asdict(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._config = config
            return True
            
        except (OSError, json.JSONEncodeError) as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_config(self) -> FluxSortConfig:
        """Get current configuration (loads if not already loaded)."""
        return self.load_config()
    
    def update_config(self, **kwargs) -> bool:
        """
        Update specific configuration values.
        
        Args:
            **kwargs: Configuration values to update
            
        Returns:
            True if updated successfully
        """
        config = self.get_config()
        
        # Update values
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print(f"Warning: Unknown configuration key: {key}")
        
        return self.save_config(config)
    
    def reset_config(self) -> bool:
        """
        Reset configuration to defaults.
        
        Returns:
            True if reset successfully
        """
        default_config = FluxSortConfig()
        return self.save_config(default_config)
    
    def get_category_folder_name(self, category: FileCategory) -> str:
        """
        Get the folder name for a specific category.
        
        Args:
            category: FileCategory to get name for
            
        Returns:
            Folder name for the category
        """
        config = self.get_config()
        return config.category_folders.get(category.value, category.value)
    
    def set_category_folder_name(self, category: FileCategory, folder_name: str) -> bool:
        """
        Set the folder name for a specific category.
        
        Args:
            category: FileCategory to set name for
            folder_name: New folder name
            
        Returns:
            True if set successfully
        """
        config = self.get_config()
        config.category_folders[category.value] = folder_name
        return self.save_config(config)
    
    def add_custom_extension(self, extension: str, category: FileCategory) -> bool:
        """
        Add a custom file extension mapping.
        
        Args:
            extension: File extension (with or without dot)
            category: Category to map to
            
        Returns:
            True if added successfully
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        config = self.get_config()
        config.custom_extensions[extension.lower()] = category.value
        return self.save_config(config)
    
    def remove_custom_extension(self, extension: str) -> bool:
        """
        Remove a custom file extension mapping.
        
        Args:
            extension: File extension to remove
            
        Returns:
            True if removed successfully
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        config = self.get_config()
        if extension.lower() in config.custom_extensions:
            del config.custom_extensions[extension.lower()]
            return self.save_config(config)
        
        return False
    
    def add_include_pattern(self, pattern: str) -> bool:
        """
        Add a file pattern to include in scanning.
        
        Args:
            pattern: Glob pattern to include
            
        Returns:
            True if added successfully
        """
        config = self.get_config()
        if pattern not in config.include_patterns:
            config.include_patterns.append(pattern)
            return self.save_config(config)
        return True
    
    def add_exclude_pattern(self, pattern: str) -> bool:
        """
        Add a file pattern to exclude from scanning.
        
        Args:
            pattern: Glob pattern to exclude
            
        Returns:
            True if added successfully
        """
        config = self.get_config()
        if pattern not in config.exclude_patterns:
            config.exclude_patterns.append(pattern)
            return self.save_config(config)
        return True
    
    def list_settings(self) -> Dict[str, Any]:
        """
        Get all current settings as a dictionary.
        
        Returns:
            Dictionary of all configuration settings
        """
        config = self.get_config()
        return asdict(config)
    
    def export_config(self, export_path: Path) -> bool:
        """
        Export configuration to a specific file.
        
        Args:
            export_path: Path to export configuration to
            
        Returns:
            True if exported successfully
        """
        try:
            config = self.get_config()
            config_data = asdict(config)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (OSError, json.JSONEncodeError):
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """
        Import configuration from a specific file.
        
        Args:
            import_path: Path to import configuration from
            
        Returns:
            True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = FluxSortConfig(**config_data)
            return self.save_config(config)
            
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return False