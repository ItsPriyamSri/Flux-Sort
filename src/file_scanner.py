"""File scanner module for discovering and analyzing files in directories."""

import os
from pathlib import Path
from typing import List, Dict, Generator, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import time

from .file_detector import FileTypeDetector, FileInfo, FileCategory


@dataclass
class ScanResult:
    """Results from scanning a directory."""
    scanned_path: Path
    total_files: int
    total_size: int
    files_by_category: Dict[FileCategory, List[FileInfo]]
    scan_duration: float
    hidden_files_count: int
    errors: List[str]
    
    @property
    def total_size_mb(self) -> float:
        """Total size in megabytes."""
        return round(self.total_size / (1024 * 1024), 2)
    
    @property
    def category_summary(self) -> Dict[FileCategory, int]:
        """Summary of file counts by category."""
        return {category: len(files) for category, files in self.files_by_category.items()}


class FileScanner:
    """Scans directories and categorizes files for organization."""
    
    def __init__(self, file_detector: Optional[FileTypeDetector] = None):
        """
        Initialize the file scanner.
        
        Args:
            file_detector: FileTypeDetector instance, creates new one if None
        """
        self.file_detector = file_detector or FileTypeDetector()
        self.include_hidden = False
        self.max_depth = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set a callback function for progress updates.
        
        Args:
            callback: Function that takes (current, total) parameters
        """
        self.progress_callback = callback
    
    def scan_directory(
        self,
        directory: Path,
        include_hidden: bool = False,
        max_depth: Optional[int] = None,
        file_patterns: Optional[List[str]] = None
    ) -> ScanResult:
        """
        Scan a directory and categorize all files.
        
        Args:
            directory: Directory to scan
            include_hidden: Whether to include hidden files
            max_depth: Maximum depth to scan (None for unlimited)
            file_patterns: Optional list of file patterns to include
            
        Returns:
            ScanResult with categorized files
        """
        start_time = time.time()
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        self.include_hidden = include_hidden
        self.max_depth = max_depth
        
        files_by_category: Dict[FileCategory, List[FileInfo]] = {
            category: [] for category in FileCategory
        }
        
        errors = []
        total_files = 0
        total_size = 0
        hidden_files_count = 0
        
        # First pass: count total files for progress tracking
        total_file_count = self._count_files(directory)
        processed_count = 0
        
        try:
            for file_path in self._walk_directory(directory, 0):
                try:
                    if self.file_detector.is_hidden_file(file_path):
                        hidden_files_count += 1
                        if not include_hidden:
                            continue
                    
                    # Apply file patterns if specified
                    if file_patterns and not self._matches_patterns(file_path, file_patterns):
                        continue
                    
                    file_info = self.file_detector.get_file_info(file_path)
                    if file_info:
                        files_by_category[file_info.category].append(file_info)
                        total_files += 1
                        total_size += file_info.size
                    
                    processed_count += 1
                    
                    # Update progress if callback is set
                    if self.progress_callback and total_file_count > 0:
                        self.progress_callback(processed_count, total_file_count)
                        
                except PermissionError as e:
                    errors.append(f"Permission denied: {file_path} - {str(e)}")
                except OSError as e:
                    errors.append(f"OS error reading {file_path}: {str(e)}")
                except Exception as e:
                    errors.append(f"Unexpected error with {file_path}: {str(e)}")
        
        except KeyboardInterrupt:
            errors.append("Scan interrupted by user")
        
        # Remove empty categories
        files_by_category = {
            category: files for category, files in files_by_category.items() if files
        }
        
        scan_duration = time.time() - start_time
        
        return ScanResult(
            scanned_path=directory,
            total_files=total_files,
            total_size=total_size,
            files_by_category=files_by_category,
            scan_duration=scan_duration,
            hidden_files_count=hidden_files_count,
            errors=errors
        )
    
    def _count_files(self, directory: Path) -> int:
        """Count total files for progress tracking."""
        count = 0
        try:
            for _ in self._walk_directory(directory, 0):
                count += 1
        except:
            # If we can't count, return 0 to disable progress tracking
            return 0
        return count
    
    def _walk_directory(self, directory: Path, current_depth: int) -> Generator[Path, None, None]:
        """
        Walk directory recursively, yielding file paths.
        
        Args:
            directory: Directory to walk
            current_depth: Current recursion depth
            
        Yields:
            Path objects for each file found
        """
        try:
            for item in directory.iterdir():
                if item.is_file():
                    yield item
                elif item.is_dir():
                    # Only recurse into subdirectories if max_depth allows it
                    if self.max_depth is None or current_depth < self.max_depth:
                        # Skip hidden directories unless explicitly included
                        if not self.include_hidden and self.file_detector.is_hidden_file(item):
                            continue
                        
                        # Recursively scan subdirectories
                        yield from self._walk_directory(item, current_depth + 1)
        
        except PermissionError:
            # Skip directories we can't access
            pass
        except OSError:
            # Skip directories with OS errors
            pass
    
    def _matches_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """
        Check if file matches any of the given patterns.
        
        Args:
            file_path: File to check
            patterns: List of patterns (glob-style)
            
        Returns:
            True if file matches any pattern
        """
        import fnmatch
        
        filename = file_path.name.lower()
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern.lower()):
                return True
        return False
    
    def get_downloads_directory(self) -> Optional[Path]:
        """
        Get the default Downloads directory for the current user.
        
        Returns:
            Path to Downloads directory or None if not found
        """
        home = Path.home()
        
        # Common Downloads directory locations
        downloads_paths = [
            home / "Downloads",
            home / "Download",
            home / "downloads",
        ]
        
        # On Windows, check for localized Downloads folder
        if os.name == 'nt':
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    downloads_path = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
                    downloads_paths.insert(0, Path(downloads_path))
            except (WindowsError, FileNotFoundError):
                pass
        
        # Return the first existing Downloads directory
        for path in downloads_paths:
            if path.exists() and path.is_dir():
                return path
        
        return None
    
    def quick_scan(self, directory: Path, max_files: int = 100) -> Dict[FileCategory, int]:
        """
        Perform a quick scan to get category counts without full file info.
        
        Args:
            directory: Directory to scan
            max_files: Maximum number of files to scan
            
        Returns:
            Dictionary with category counts
        """
        category_counts: Dict[FileCategory, int] = {category: 0 for category in FileCategory}
        
        file_count = 0
        try:
            for file_path in self._walk_directory(directory, 0):
                if file_count >= max_files:
                    break
                
                if not self.include_hidden and self.file_detector.is_hidden_file(file_path):
                    continue
                
                category = self.file_detector.detect_file_category(file_path)
                category_counts[category] += 1
                file_count += 1
        
        except Exception:
            # Return partial results on error
            pass
        
        # Remove zero counts
        return {category: count for category, count in category_counts.items() if count > 0}