#!/usr/bin/env python3
"""
Quick test runner shortcut
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Chạy test runner chính"""
    if len(sys.argv) > 1:
        # Chạy pytest trực tiếp với tham số
        cmd = [sys.executable, "-m", "pytest"] + sys.argv[1:]
        subprocess.run(cmd)
    else:
        # Chạy test runner với menu
        test_runner_path = Path(__file__).parent / "test_runner.py"
        subprocess.run([sys.executable, str(test_runner_path)])


if __name__ == "__main__":
    main()
