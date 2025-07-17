#!/usr/bin/env python3
"""
FluxSort - Interactive file organization tool.
An intelligent file sorter that transforms cluttered directories into organized beauty.
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.file_detector import FileTypeDetector, FileCategory
from src.file_scanner import FileScanner, ScanResult
from src.file_sorter import FileSorter, SortResult


class InteractiveFluxSort:
    """Interactive FluxSort application with menu-driven interface."""
    
    def __init__(self):
        self.detector = FileTypeDetector()
        self.scanner = FileScanner(self.detector)
        self.current_path: Optional[Path] = None
        self.scan_result: Optional[ScanResult] = None
        self.sorter: Optional[FileSorter] = None
        
    def print_welcome(self):
        """Display welcome message and explanation."""
        banner = """
╔════════════════════════════════════════════════════════════════════╗
║  ███████╗██╗     ██╗   ██╗██╗  ██╗███████╗ ██████╗ ██████╗████████╗║
║  ██╔════╝██║     ██║   ██║╚██╗██╔╝██╔════╝██╔═══██╗██╔══██╚══██╔══╝║
║  █████╗  ██║     ██║   ██║ ╚███╔╝ ███████╗██║   ██║██████╔╝  ██║   ║
║  ██╔══╝  ██║     ██║   ██║ ██╔██╗ ╚════██║██║   ██║██╔══██╗  ██║   ║
║  ██║     ███████╗╚██████╔╝██╔╝ ██╗███████║╚██████╔╝██║  ██║  ██║   ║
║  ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝  ╚═╝   ║
║                                                                    ║
║            Transform chaos into organized beauty                   ║
╚════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print("  💫 Welcome to FluxSort - Your Intelligent File Organizer!")
        print()
        print("  🤖 What I do:")
        print("     • Scan directories for files")
        print("     • Intelligently categorize files by type") 
        print("     • Organize files into neat folders")
        print("     • Keep track of all operations for easy reversal")
        print()
        print("  🛡️  Safety first:")
        print("     • Always preview before moving files")
        print("     • Comprehensive undo functionality")
        print("     • Safe handling of file conflicts")
        print()
        print("  Let's get your files organized! ✨")
        print("=" * 65)
        print()
    
    def get_target_path(self) -> Optional[Path]:
        """Get target directory path from user with validation."""
        current_dir = Path.cwd()
        
        print("📂 PATH SELECTION")
        print("-" * 30)
        print(f"Current directory: {current_dir}")
        print()
        
        while True:
            response = input("Use current directory? (Y/yes or enter custom path): ").strip()
            
            # Use current directory
            if response.lower() in ['y', 'yes', '']:
                target_path = current_dir
                break
            
            # Custom path provided
            try:
                target_path = Path(response).resolve()
                
                # Validate path
                if not target_path.exists():
                    print(f"❌ Error: Path '{target_path}' does not exist.")
                    print("   Please enter a valid path or 'Y' to use current directory.")
                    print()
                    continue
                
                if not target_path.is_dir():
                    print(f"❌ Error: '{target_path}' is not a directory.")
                    print("   Please enter a valid directory path.")
                    print()
                    continue
                
                break
                
            except Exception as e:
                print(f"❌ Error: Invalid path format - {str(e)}")
                print("   Please enter a valid path or 'Y' to use current directory.")
                print()
                continue
        
        print(f"✅ Selected path: {target_path}")
        print()
        return target_path
    
    def display_directory_contents(self, path: Path) -> None:
        """Display files and folders in the target directory."""
        print("📁 DIRECTORY CONTENTS")
        print("-" * 30)
        
        try:
            items = list(path.iterdir())
            
            if not items:
                print("  📭 Directory is empty")
                print()
                return
            
            # Separate files and folders
            folders = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # Display statistics
            print(f"  📊 Found: {len(folders)} folders, {len(files)} files")
            print()
            
            # Display folders (first 10)
            if folders:
                print("  📁 Folders:")
                for folder in sorted(folders)[:10]:
                    if not self.detector.is_hidden_file(folder):
                        print(f"     📂 {folder.name}")
                if len(folders) > 10:
                    print(f"     ... and {len(folders) - 10} more folders")
                print()
            
            # Display files (first 15)
            if files:
                print("  📄 Files:")
                for file in sorted(files)[:15]:
                    if not self.detector.is_hidden_file(file):
                        size_mb = file.stat().st_size / (1024 * 1024)
                        if size_mb < 0.1:
                            size_str = f"{file.stat().st_size} bytes"
                        else:
                            size_str = f"{size_mb:.1f} MB"
                        print(f"     📄 {file.name} ({size_str})")
                if len(files) > 15:
                    print(f"     ... and {len(files) - 15} more files")
                print()
                
        except PermissionError:
            print("  ❌ Permission denied - cannot read directory contents")
            print()
        except Exception as e:
            print(f"  ❌ Error reading directory: {str(e)}")
            print()
    
    def scan_directory(self, path: Path) -> bool:
        """Scan the directory and store results."""
        print("🔍 SCANNING DIRECTORY")
        print("-" * 30)
        print(f"Scanning: {path}")
        
        try:
            # Set up progress callback
            self.scanner.set_progress_callback(self.progress_callback)
            
            # Perform scan - ONLY scan immediate directory, not subdirectories
            self.scan_result = self.scanner.scan_directory(path, include_hidden=False, max_depth=0)
            print()  # New line after progress bar
            
            # Display scan summary
            print(f"✅ Scan completed in {self.scan_result.scan_duration:.2f} seconds")
            print(f"📄 Total files found: {self.scan_result.total_files}")
            print(f"💾 Total size: {self.scan_result.total_size_mb} MB")
            
            if self.scan_result.hidden_files_count > 0:
                print(f"👻 Hidden files (excluded): {self.scan_result.hidden_files_count}")
            
            if self.scan_result.errors:
                print(f"⚠️  Errors encountered: {len(self.scan_result.errors)}")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Scan failed: {str(e)}")
            print()
            return False
    
    def progress_callback(self, current: int, total: int):
        """Progress callback for file scanning."""
        if total > 0:
            percent = (current / total) * 100
            bar_length = 40
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"\r  Progress: |{bar}| {percent:.1f}% ({current}/{total})", end='', flush=True)
    
    def display_main_menu(self) -> str:
        """Display main menu and get user choice."""
        print("🎛️  MAIN MENU")
        print("-" * 30)
        print("1. 👁️  Preview File Organization (See what would happen)")
        print("2. 🚀 Organize Files (Move files for real)")
        print("3. ↩️  View & Revert Previous Operations")
        print("4. 🔄 Change Directory")
        print("5. ❌ Exit")
        print()
        
        while True:
            choice = input("Select option (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    def show_preview(self, detailed: bool = True) -> bool:
        """Show file organization preview."""
        if not self.scan_result or not self.scan_result.files_by_category:
            print("❌ No files found to organize.")
            return False
        
        print("👁️  FILE ORGANIZATION PREVIEW")
        print("=" * 50)
        
        # Initialize sorter
        self.sorter = FileSorter(self.current_path)
        preview = self.sorter.preview_sort_operation(self.scan_result)
        
        total_operations = sum(len(moves) for moves in preview.values())
        print(f"📝 Total files to organize: {total_operations}")
        print()
        
        # Show preview by category
        for category, moves in preview.items():
            if moves:
                icon = self.get_category_icon(category)
                print(f"{icon} {category.value} ({len(moves)} files)")
                print(f"   📥 Destination: {self.current_path / self.sorter._get_folder_names()[category]}")
                
                if detailed:
                    # Show first few files
                    for source, dest in moves[:5]:
                        print(f"   📤 {source.name}")
                    if len(moves) > 5:
                        print(f"   ... and {len(moves) - 5} more files")
                else:
                    # Just show count
                    sample_files = [move[0].name for move in moves[:3]]
                    print(f"   📄 Examples: {', '.join(sample_files)}")
                    if len(moves) > 3:
                        print(f"   ... and {len(moves) - 3} more")
                print()
        
        return True
    
    def get_category_icon(self, category: FileCategory) -> str:
        """Get emoji icon for category."""
        icons = {
            FileCategory.IMAGES: "🖼️ ",
            FileCategory.VIDEOS: "🎬",
            FileCategory.DOCUMENTS: "📄",
            FileCategory.AUDIO: "🎵",
            FileCategory.ARCHIVES: "📦",
            FileCategory.CODE: "💻",
            FileCategory.SYSTEM: "⚙️ ",
            FileCategory.MOBILE: "📱",
            FileCategory.WEB: "🌐",
            FileCategory.DATA: "📊",
            FileCategory.FONTS: "🔤",
            FileCategory.MODELS_3D: "🎮",
            FileCategory.EBOOKS: "📚",
            FileCategory.MISCELLANEOUS: "❓"
        }
        return icons.get(category, "📁")
    
    def option_preview(self) -> None:
        """Handle Option 1: Preview mode."""
        print("\n" + "="*50)
        print("OPTION 1: PREVIEW MODE")
        print("="*50)
        
        if not self.show_preview(detailed=True):
            return
        
        print("💡 This is a preview only - no files will be moved.")
        print("   Use Option 2 to actually organize the files.")
        input("\nPress Enter to return to main menu...")
    
    def option_organize(self) -> None:
        """Handle Option 2: Real file organization."""
        print("\n" + "="*50)
        print("OPTION 2: ORGANIZE FILES")
        print("="*50)
        
        # Always show preview first
        if not self.show_preview(detailed=False):
            return
        
        # Confirmation step
        print("⚠️  CONFIRMATION REQUIRED")
        print("-" * 30)
        while True:
            confirm = input("Do you want to proceed with moving these files? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                break
            elif confirm in ['no', 'n']:
                print("❌ Operation cancelled.")
                input("Press Enter to return to main menu...")
                return
            else:
                print("Please enter 'yes' or 'no'")
        
        # Perform actual file organization
        print("\n🚀 ORGANIZING FILES...")
        print("-" * 30)
        
        try:
            # Perform the sort operation
            sort_result = self.sorter.sort_files(self.scan_result, dry_run=False)
            
            # Display results
            self.display_sort_results(sort_result)
            
            # Offer undo option
            if sort_result.successful_moves > 0:
                print("\n🔄 UNDO OPTION")
                print("-" * 30)
                while True:
                    undo_choice = input("Would you like to undo this operation? (yes/no): ").strip().lower()
                    if undo_choice in ['yes', 'y']:
                        self.undo_last_operation()
                        break
                    elif undo_choice in ['no', 'n']:
                        print("✅ Operation completed successfully!")
                        break
                    else:
                        print("Please enter 'yes' or 'no'")
            
        except Exception as e:
            print(f"❌ Organization failed: {str(e)}")
        
        input("\nPress Enter to return to main menu...")
    
    def display_sort_results(self, sort_result: SortResult) -> None:
        """Display results of sorting operation."""
        print("\n✨ ORGANIZATION RESULTS")
        print("=" * 30)
        print(f"✅ Successfully moved: {sort_result.successful_moves} files")
        print(f"❌ Failed to move: {sort_result.failed_moves} files")
        print(f"💾 Data organized: {sort_result.total_size_moved_mb} MB")
        print(f"⏱️  Duration: {sort_result.duration:.2f} seconds")
        
        if sort_result.errors:
            print(f"\n⚠️  ERRORS ({len(sort_result.errors)}):")
            for error in sort_result.errors[:5]:
                print(f"  • {error}")
            if len(sort_result.errors) > 5:
                print(f"  ... and {len(sort_result.errors) - 5} more errors")
    
    def option_revert(self) -> None:
        """Handle Option 3: View and revert operations."""
        print("\n" + "="*50)
        print("OPTION 3: PREVIOUS OPERATIONS")
        print("="*50)
        
        # Create a temporary sorter to access history
        temp_sorter = FileSorter(self.current_path or Path.cwd())
        history = temp_sorter.get_operation_history(limit=20)
        
        if not history:
            print("📭 No previous operations found.")
            input("Press Enter to return to main menu...")
            return
        
        print(f"📋 Found {len(history)} recent operations:")
        print()
        
        # Display operations
        for i, operation in enumerate(history[:10], 1):
            timestamp = operation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i:2d}. 📅 {timestamp}")
            print(f"    📁 From: {operation.source_path.parent}")
            print(f"    📂 To: {operation.destination_path.parent}")
            print(f"    🔗 Operation ID: {operation.operation_id[:8]}...")
            print()
        
        if len(history) > 10:
            print(f"... and {len(history) - 10} more operations")
            print()
        
        # Get user choice
        print("💡 Select an operation to revert (by number) or 0 to cancel:")
        while True:
            try:
                choice = input("Enter choice: ").strip()
                if choice == '0':
                    return
                
                choice_num = int(choice)
                if 1 <= choice_num <= min(10, len(history)):
                    selected_operation = history[choice_num - 1]
                    self.revert_specific_operation(selected_operation.operation_id, temp_sorter)
                    break
                else:
                    print(f"Please enter a number between 1 and {min(10, len(history))}, or 0 to cancel")
            except ValueError:
                print("Please enter a valid number")
        
        input("Press Enter to return to main menu...")
    
    def undo_last_operation(self) -> None:
        """Undo the most recent operation."""
        if not self.sorter:
            print("❌ No sorter available for undo operation")
            return
        
        history = self.sorter.get_operation_history(limit=1)
        if not history:
            print("❌ No operations to undo")
            return
        
        last_operation_id = history[0].operation_id
        self.revert_specific_operation(last_operation_id, self.sorter)
    
    def revert_specific_operation(self, operation_id: str, sorter: FileSorter) -> None:
        """Revert a specific operation."""
        print(f"\n🔄 REVERTING OPERATION")
        print("-" * 30)
        print(f"Operation ID: {operation_id[:8]}...")
        
        try:
            successful_undos, failed_undos, errors = sorter.undo_operation(operation_id)
            
            print(f"✅ Successfully reverted: {successful_undos} files")
            print(f"❌ Failed to revert: {failed_undos} files")
            
            if errors:
                print(f"\n⚠️  REVERT ERRORS:")
                for error in errors[:5]:
                    print(f"  • {error}")
                if len(errors) > 5:
                    print(f"  ... and {len(errors) - 5} more errors")
            
            if successful_undos > 0:
                print("✅ Operation successfully reverted!")
            else:
                print("❌ No files were reverted")
                
        except Exception as e:
            print(f"❌ Revert failed: {str(e)}")
    
    def run(self) -> None:
        """Main application loop."""
        try:
            # Welcome message
            self.print_welcome()
            
            # Get target path
            self.current_path = self.get_target_path()
            if not self.current_path:
                return
            
            # Display directory contents
            self.display_directory_contents(self.current_path)
            
            # Scan directory
            if not self.scan_directory(self.current_path):
                return
            
            # Main menu loop
            while True:
                choice = self.display_main_menu()
                
                if choice == '1':
                    self.option_preview()
                elif choice == '2':
                    self.option_organize()
                elif choice == '3':
                    self.option_revert()
                elif choice == '4':
                    # Change directory
                    new_path = self.get_target_path()
                    if new_path:
                        self.current_path = new_path
                        self.display_directory_contents(self.current_path)
                        if not self.scan_directory(self.current_path):
                            continue
                elif choice == '5':
                    print("\n👋 Thank you for using FluxSort!")
                    print("   Your files are now beautifully organized! ✨")
                    break
        
        except KeyboardInterrupt:
            print("\n\n❌ Operation interrupted by user.")
            print("👋 Thank you for using FluxSort!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("👋 Thank you for using FluxSort!")


def main():
    """Main entry point for interactive FluxSort."""
    app = InteractiveFluxSort()
    app.run()


if __name__ == '__main__':
    main()