"""
Test Data Validation Script
Checks that all test data files are present and properly formatted
"""

import os
import sys

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(current_dir, 'test_data')

def validate_test_data():
    """Validate all test data files"""
    print("🔍 TEST DATA VALIDATION")
    print("=" * 50)
    
    results = []
    
    # Expected files
    expected_files = {
        'small_test.txt': {
            'description': 'Small text file for basic testing',
            'min_size': 50,
            'max_size': 500,
            'expected_content': ['small test file', 'simple text']
        },
        'large_test.txt': {
            'description': 'Large text file for performance testing',
            'min_size': 1000,
            'max_size': 10000,
            'expected_content': ['large test file']
        },
        'eicar_test.txt': {
            'description': 'EICAR virus test file for antivirus testing',
            'min_size': 68,
            'max_size': 70,
            'expected_content': ['EICAR-STANDARD-ANTIVIRUS-TEST-FILE']
        }
    }
    
    # Check if test_data directory exists
    if not os.path.exists(test_data_dir):
        results.append("❌ Test Data Directory: NOT FOUND")
        print("❌ Test Data Directory: NOT FOUND")
        return results
    else:
        results.append(f"✅ Test Data Directory: FOUND - {test_data_dir}")
        print(f"✅ Test Data Directory: FOUND - {test_data_dir}")
    
    # Check each expected file
    for filename, specs in expected_files.items():
        filepath = os.path.join(test_data_dir, filename)
        
        print(f"\n🔎 Checking {filename}...")
        
        # Check file existence
        if not os.path.exists(filepath):
            results.append(f"❌ {filename}: FILE NOT FOUND")
            print(f"❌ {filename}: FILE NOT FOUND")
            continue
        
        # Check file size
        try:
            file_size = os.path.getsize(filepath)
            if file_size < specs['min_size']:
                results.append(f"⚠️ {filename}: TOO SMALL ({file_size} bytes, min: {specs['min_size']})")
                print(f"⚠️ {filename}: TOO SMALL ({file_size} bytes)")
            elif file_size > specs['max_size']:
                results.append(f"⚠️ {filename}: TOO LARGE ({file_size} bytes, max: {specs['max_size']})")
                print(f"⚠️ {filename}: TOO LARGE ({file_size} bytes)")
            else:
                results.append(f"✅ {filename}: SIZE OK ({file_size} bytes)")
                print(f"✅ {filename}: SIZE OK ({file_size} bytes)")
        except Exception as e:
            results.append(f"❌ {filename}: SIZE CHECK FAILED - {e}")
            print(f"❌ {filename}: SIZE CHECK FAILED - {e}")
            continue
        
        # Check file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
            content_ok = True
            for expected in specs['expected_content']:
                if expected.lower() not in content:
                    content_ok = False
                    break
            
            if content_ok:
                results.append(f"✅ {filename}: CONTENT OK")
                print(f"✅ {filename}: CONTENT OK")
            else:
                results.append(f"⚠️ {filename}: UNEXPECTED CONTENT")
                print(f"⚠️ {filename}: UNEXPECTED CONTENT")
                
        except Exception as e:
            results.append(f"❌ {filename}: CONTENT CHECK FAILED - {e}")
            print(f"❌ {filename}: CONTENT CHECK FAILED - {e}")
    
    # Check for unexpected files
    print(f"\n🔎 Checking for unexpected files...")
    try:
        actual_files = set(os.listdir(test_data_dir))
        expected_files_set = set(expected_files.keys())
        unexpected_files = actual_files - expected_files_set
        
        if unexpected_files:
            results.append(f"⚠️ Unexpected files found: {list(unexpected_files)}")
            print(f"⚠️ Unexpected files found: {list(unexpected_files)}")
        else:
            results.append("✅ No unexpected files")
            print("✅ No unexpected files")
            
    except Exception as e:
        results.append(f"❌ Directory listing failed: {e}")
        print(f"❌ Directory listing failed: {e}")
    
    return results

def main():
    """Main function"""
    print("🧪 Test Data Validation")
    print("This script validates all test data files are present and correct")
    print()
    
    results = validate_test_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")
    
    passed = len([r for r in results if "✅" in r])
    failed = len([r for r in results if "❌" in r])
    warnings = len([r for r in results if "⚠️" in r])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    if failed == 0:
        print("\n🎉 All test data files are valid!")
    elif failed <= 1:
        print("\n😊 Test data mostly valid with minor issues!")
    else:
        print("\n❌ Test data validation failed - please fix issues!")
    
    print("\n📋 Validation Results:")
    for result in results:
        print(f"  {result}")
    
    print("\n💡 Test Data Files Purpose:")
    print("  - small_test.txt: Basic file transfer testing")
    print("  - large_test.txt: Performance and large file testing")
    print("  - eicar_test.txt: Antivirus/virus scanning testing")
    
    print("\n🔧 If files are missing or corrupted:")
    print("  1. Check if files were accidentally deleted")
    print("  2. Regenerate files using appropriate tools")
    print("  3. Ensure EICAR test virus is properly formatted")
    print("  4. Verify file permissions allow reading")

if __name__ == "__main__":
    main()
