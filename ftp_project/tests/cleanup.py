#!/usr/bin/env python3
"""
Script dọn dẹp để xóa file rỗng và file tạm thời
"""

import os
import sys
from pathlib import Path

def cleanup_empty_files(directory):
    """Xóa file rỗng trong thư mục"""
    directory = Path(directory)
    removed_files = []
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                # Kiểm tra nếu file rỗng
                if file_path.stat().st_size == 0:
                    # Bỏ qua file rỗng hợp lệ
                    if file_path.name in ['__init__.py', '.gitkeep', '.gitignore']:
                        continue
                    
                    # Xóa file rỗng
                    file_path.unlink()
                    removed_files.append(str(file_path))
                    print(f"Đã xóa file rỗng: {file_path}")
                    
            except Exception as e:
                print(f"Không thể xử lý {file_path}: {e}")
    
    return removed_files

def cleanup_temp_files(directory):
    """Xóa file tạm thời và backup"""
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
                    print(f"Đã xóa file tạm: {file_path}")
                except Exception as e:
                    print(f"Không thể xóa {file_path}: {e}")
    
    return removed_files

def main():
    """Function dọn dẹp chính"""
    # Lấy thư mục hiện tại hoặc sử dụng argument được cung cấp
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = Path(__file__).parent
    
    print(f"Đang dọn dẹp thư mục: {target_dir}")
    
    # Dọn dẹp file rỗng
    empty_files = cleanup_empty_files(target_dir)
    
    # Dọn dẹp file tạm
    temp_files = cleanup_temp_files(target_dir)
    
    total_removed = len(empty_files) + len(temp_files)
    
    if total_removed > 0:
        print(f"\nDọn dẹp hoàn tất! Đã xóa {total_removed} files.")
    else:
        print("\nKhông có file nào cần dọn dẹp.")

if __name__ == "__main__":
    main()
