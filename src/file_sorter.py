"""File sorting and organization module with safety features."""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

from .file_detector import FileInfo, FileCategory
from .file_scanner import ScanResult


@dataclass
class SortOperation:
    """Represents a single file sorting operation."""
    source_path: Path
    destination_path: Path
    category: FileCategory
    operation_id: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'source_path': str(self.source_path),
            'destination_path': str(self.destination_path),
            'category': self.category.value,
            'operation_id': self.operation_id,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SortOperation':
        """Create from dictionary."""
        return cls(
            source_path=Path(data['source_path']),
            destination_path=Path(data['destination_path']),
            category=FileCategory(data['category']),
            operation_id=data['operation_id'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class SortResult:
    """Results from a sorting operation."""
    operations: List[SortOperation]
    successful_moves: int
    failed_moves: int
    total_size_moved: int
    duration: float
    errors: List[str]
    dry_run: bool
    
    @property
    def total_size_moved_mb(self) -> float:
        """Total size moved in megabytes."""
        return round(self.total_size_moved / (1024 * 1024), 2)


class FileSorter:
    """Handles file sorting operations with safety features and undo capability."""
    
    def __init__(self, base_directory: Path):
        """
        Initialize the file sorter.
        
        Args:
            base_directory: Base directory where sorted files will be organized
        """
        self.base_directory = Path(base_directory)
        self.history_file = self.base_directory / ".fluxsort_history.json"
        self.conflicts_strategy = "rename"  # rename, skip, overwrite
        
    def sort_files(
        self,
        scan_result: ScanResult,
        dry_run: bool = True,
        create_category_folders: bool = True,
        custom_folder_names: Optional[Dict[FileCategory, str]] = None
    ) -> SortResult:
        """
        Sort files based on scan results.
        
        Args:
            scan_result: Results from file scanning
            dry_run: If True, only simulate the operation
            create_category_folders: Whether to create category folders
            custom_folder_names: Custom names for category folders
            
        Returns:
            SortResult with operation details
        """
        start_time = datetime.now()
        operations: List[SortOperation] = []
        errors: List[str] = []
        successful_moves = 0
        failed_moves = 0
        total_size_moved = 0
        
        # Generate unique operation ID
        operation_id = str(uuid.uuid4())
        
        # Create folder mapping
        folder_names = self._get_folder_names(custom_folder_names)
        
        # Create category folders if needed and not dry run
        if create_category_folders and not dry_run:
            self._create_category_folders(scan_result.files_by_category.keys(), folder_names)
        
        # Process each category
        for category, files in scan_result.files_by_category.items():
            category_folder = self.base_directory / folder_names[category]
            
            for file_info in files:
                try:
                    destination_path = self._get_destination_path(
                        file_info, category_folder, dry_run
                    )
                    
                    operation = SortOperation(
                        source_path=file_info.path,
                        destination_path=destination_path,
                        category=category,
                        operation_id=operation_id,
                        timestamp=datetime.now()
                    )
                    
                    if not dry_run:
                        success = self._move_file(file_info.path, destination_path)
                        if success:
                            successful_moves += 1
                            total_size_moved += file_info.size
                        else:
                            failed_moves += 1
                            errors.append(f"Failed to move {file_info.path}")
                    else:
                        successful_moves += 1
                        total_size_moved += file_info.size
                    
                    operations.append(operation)
                    
                except Exception as e:
                    failed_moves += 1
                    errors.append(f"Error processing {file_info.path}: {str(e)}")
        
        # Save operation history if not dry run
        if not dry_run and operations:
            self._save_operation_history(operations)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return SortResult(
            operations=operations,
            successful_moves=successful_moves,
            failed_moves=failed_moves,
            total_size_moved=total_size_moved,
            duration=duration,
            errors=errors,
            dry_run=dry_run
        )
    
    def _get_folder_names(self, custom_names: Optional[Dict[FileCategory, str]] = None) -> Dict[FileCategory, str]:
        """Get folder names for each category."""
        default_names = {
            FileCategory.IMAGES: "Images",
            FileCategory.VIDEOS: "Videos",
            FileCategory.DOCUMENTS: "Documents",
            FileCategory.AUDIO: "Audio",
            FileCategory.ARCHIVES: "Archives",
            FileCategory.CODE: "Code",
            FileCategory.SYSTEM: "System Files",
            FileCategory.MOBILE: "Mobile Apps",
            FileCategory.WEB: "Web Files",
            FileCategory.DATA: "Data Files",
            FileCategory.FONTS: "Fonts",
            FileCategory.MODELS_3D: "3D Models",
            FileCategory.EBOOKS: "Ebooks",
            FileCategory.MISCELLANEOUS: "Miscellaneous"
        }
        
        if custom_names:
            default_names.update(custom_names)
        
        return default_names
    
    def _create_category_folders(self, categories: Set[FileCategory], folder_names: Dict[FileCategory, str]) -> None:
        """Create folders for each category."""
        for category in categories:
            folder_path = self.base_directory / folder_names[category]
            folder_path.mkdir(exist_ok=True, parents=True)
    
    def _get_destination_path(self, file_info: FileInfo, category_folder: Path, dry_run: bool) -> Path:
        """
        Get the destination path for a file, handling conflicts.
        
        Args:
            file_info: Information about the file
            category_folder: Destination category folder
            dry_run: Whether this is a dry run
            
        Returns:
            Final destination path
        """
        base_destination = category_folder / file_info.name
        
        # If file doesn't exist at destination or it's a dry run, return as-is
        if dry_run or not base_destination.exists():
            return base_destination
        
        # Handle conflicts based on strategy
        if self.conflicts_strategy == "skip":
            return base_destination  # Caller will handle the skip
        elif self.conflicts_strategy == "overwrite":
            return base_destination
        elif self.conflicts_strategy == "rename":
            return self._get_unique_filename(base_destination)
        
        return base_destination
    
    def _get_unique_filename(self, file_path: Path) -> Path:
        """
        Generate a unique filename by adding a counter suffix.
        
        Args:
            file_path: Original file path
            
        Returns:
            Unique file path
        """
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent
        
        while True:
            new_name = f"{stem} ({counter}){suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _move_file(self, source: Path, destination: Path) -> bool:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle conflict strategies
            if destination.exists():
                if self.conflicts_strategy == "skip":
                    return False
                elif self.conflicts_strategy == "overwrite":
                    destination.unlink()
                # For rename, _get_destination_path should have handled it
            
            # Perform the move
            shutil.move(str(source), str(destination))
            return True
            
        except (OSError, PermissionError, shutil.Error):
            return False
    
    def _save_operation_history(self, operations: List[SortOperation]) -> None:
        """Save operation history for undo functionality."""
        history_data = []
        
        # Load existing history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                history_data = []
        
        # Add new operations
        for operation in operations:
            history_data.append(operation.to_dict())
        
        # Keep only last 1000 operations
        history_data = history_data[-1000:]
        
        # Save updated history
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)
        except OSError:
            pass  # Silently fail if we can't save history
    
    def get_operation_history(self, limit: Optional[int] = None) -> List[SortOperation]:
        """
        Get operation history for undo functionality.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of SortOperation objects
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            operations = [SortOperation.from_dict(data) for data in history_data]
            
            if limit:
                operations = operations[-limit:]
            
            return list(reversed(operations))  # Most recent first
            
        except (json.JSONDecodeError, OSError, KeyError):
            return []
    
    def undo_operation(self, operation_id: str) -> Tuple[int, int, List[str]]:
        """
        Undo a specific operation by moving files back.
        
        Args:
            operation_id: ID of the operation to undo
            
        Returns:
            Tuple of (successful_undos, failed_undos, errors)
        """
        operations = self.get_operation_history()
        target_operations = [op for op in operations if op.operation_id == operation_id]
        
        if not target_operations:
            return 0, 0, [f"Operation {operation_id} not found"]
        
        successful_undos = 0
        failed_undos = 0
        errors = []
        
        for operation in target_operations:
            try:
                # Only undo if the file is still at the destination
                if operation.destination_path.exists():
                    # Ensure source directory exists
                    operation.source_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file back
                    shutil.move(str(operation.destination_path), str(operation.source_path))
                    successful_undos += 1
                else:
                    failed_undos += 1
                    errors.append(f"File not found at destination: {operation.destination_path}")
                    
            except (OSError, PermissionError, shutil.Error) as e:
                failed_undos += 1
                errors.append(f"Failed to undo {operation.destination_path}: {str(e)}")
        
        return successful_undos, failed_undos, errors
    
    def set_conflicts_strategy(self, strategy: str) -> None:
        """
        Set the strategy for handling file conflicts.
        
        Args:
            strategy: One of 'rename', 'skip', 'overwrite'
        """
        if strategy not in ['rename', 'skip', 'overwrite']:
            raise ValueError(f"Invalid strategy: {strategy}")
        self.conflicts_strategy = strategy
    
    def preview_sort_operation(self, scan_result: ScanResult) -> Dict[FileCategory, List[Tuple[Path, Path]]]:
        """
        Preview what files would be moved where.
        
        Args:
            scan_result: Results from file scanning
            
        Returns:
            Dictionary mapping categories to list of (source, destination) tuples
        """
        folder_names = self._get_folder_names()
        preview: Dict[FileCategory, List[Tuple[Path, Path]]] = {}
        
        for category, files in scan_result.files_by_category.items():
            category_folder = self.base_directory / folder_names[category]
            moves = []
            
            for file_info in files:
                destination = self._get_destination_path(file_info, category_folder, dry_run=True)
                moves.append((file_info.path, destination))
            
            preview[category] = moves
        
        return preview