#!/usr/bin/env python3
"""
Cleanup script to remove empty files and temporary files
"""

import os
import sys
from pathlib import Path

def cleanup_empty_files(directory):
    """Remove empty files in directory"""
    directory = Path(directory)
    removed_files = []
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                # Check if file is empty
                if file_path.stat().st_size == 0:
                    # Skip legitimate empty files
                    if file_path.name in ['__init__.py', '.gitkeep', '.gitignore']:
                        continue
                    
                    # Remove empty file
                    file_path.unlink()
                    removed_files.append(str(file_path))
                    print(f"Removed empty file: {file_path}")
                    
            except Exception as e:
                print(f"Could not process {file_path}: {e}")
    
    return removed_files

def cleanup_temp_files(directory):
    """Remove temporary and backup files"""
    directory = Path(directory)
    removed_files = []
    
    patterns = [
        "*.bak", "*.tmp", "*.temp", "*_backup", "*_backup.*",
        "fixed_*", "temp_*", "*.onedrive", "*-OneDrive"
    ]
    
    for pattern in patterns:
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    removed_files.append(str(file_path))
                    print(f"Removed temp file: {file_path}")
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")
    
    return removed_files

def main():
    """Main cleanup function"""
    # Get current directory or use provided argument
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = Path(__file__).parent
    
    print(f"Cleaning up directory: {target_dir}")
    
    # Cleanup empty files
    empty_files = cleanup_empty_files(target_dir)
    
    # Cleanup temp files
    temp_files = cleanup_temp_files(target_dir)
    
    total_removed = len(empty_files) + len(temp_files)
    
    if total_removed > 0:
        print(f"\nCleanup completed! Removed {total_removed} files.")
    else:
        print("\nNo files to clean up.")

if __name__ == "__main__":
    main()
