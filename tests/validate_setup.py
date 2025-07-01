#!/usr/bin/env python3
"""
Test Validation Script
Verify test suite setup and configurations
"""

import os
import sys
from pathlib import Path

def validate_test_setup():
    """Validate test suite setup"""
    print("🔍 Validating Test Suite Setup")
    print("="*40)
    
    # Check test directory structure
    tests_dir = Path(__file__).parent
    required_files = [
        'test_runner.py',
        'test_session.py', 
        'test_file.py',
        'test_directory.py',
        'test_local.py',
        'conftest.py',
        'pytest.ini',
        'requirements.txt',
        'test_config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not (tests_dir / file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Check test_data directory
    test_data_dir = tests_dir / "test_data"
    if test_data_dir.exists():
        print(f"✅ test_data/ directory")
        data_files = list(test_data_dir.glob("*"))
        print(f"   Found {len(data_files)} data files")
    else:
        print("❌ test_data/ directory missing")
        return False
    
    # Check downloads directory
    downloads_dir = tests_dir / "downloads"
    if downloads_dir.exists():
        print(f"✅ downloads/ directory") 
    else:
        downloads_dir.mkdir()
        print(f"✅ Created downloads/ directory")
    
    # Test pytest availability
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__}")
    except ImportError:
        print("❌ pytest not available")
        return False
    
    # Test configuration
    try:
        from test_config import TestConfig
        print("✅ TestConfig imported successfully")
        print(f"   FTP Host: {TestConfig.FTP_HOST}:{TestConfig.FTP_PORT}")
        print(f"   ClamAV Host: {TestConfig.CLAMAV_HOST}:{TestConfig.CLAMAV_PORT}")
    except ImportError as e:
        print(f"❌ TestConfig import failed: {e}")
        return False
    
    print("\n✅ Test suite validation completed successfully!")
    return True

def main():
    if validate_test_setup():
        print("\n🚀 Ready to run tests!")
        print("Usage:")
        print("  python test_runner.py  # Interactive menu")
        print("  python test.py         # Quick shortcut")  
        print("  pytest                 # Direct pytest")
    else:
        print("\n❌ Test suite setup has issues. Please fix them before running tests.")
        sys.exit(1)

if __name__ == "__main__":
    main()
