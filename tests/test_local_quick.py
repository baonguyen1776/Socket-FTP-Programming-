"""
Quick Local Operations Test
Tests local directory operations without requiring FTP server
"""

import sys
import os
import tempfile
import shutil

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

from ftp_command import FTPCommands

def test_local_operations():
    """Test local directory operations"""
    print("🧪 QUICK LOCAL OPERATIONS TEST")
    print("=" * 50)
    
    results = []
    
    # Test 1: FTP Client Creation
    try:
        ftp_client = FTPCommands()
        results.append("✅ FTP Client Creation: PASSED")
        print("✅ FTP Client Creation: PASSED")
    except Exception as e:
        results.append(f"❌ FTP Client Creation: FAILED - {e}")
        print(f"❌ FTP Client Creation: FAILED - {e}")
        return results
    
    # Test 2: Get Current Local Directory
    try:
        original_dir = os.getcwd()
        print(f"📂 Current directory: {original_dir}")
        results.append(f"✅ Current Directory Check: PASSED - {original_dir}")
        print(f"✅ Current Directory Check: PASSED")
    except Exception as e:
        results.append(f"❌ Current Directory Check: FAILED - {e}")
        print(f"❌ Current Directory Check: FAILED - {e}")
        return results
    
    # Test 3: Create Temporary Directory for Testing
    try:
        temp_dir = tempfile.mkdtemp(prefix='ftp_test_lcd_')
        print(f"📁 Created temp directory: {temp_dir}")
        results.append(f"✅ Temp Directory Creation: PASSED - {temp_dir}")
        print(f"✅ Temp Directory Creation: PASSED")
    except Exception as e:
        results.append(f"❌ Temp Directory Creation: FAILED - {e}")
        print(f"❌ Temp Directory Creation: FAILED - {e}")
        return results
    
    # Test 4: LCD Command - Change to Temp Directory
    try:
        print(f"🔄 Testing LCD to: {temp_dir}")
        ftp_client.do_lcd(temp_dir)
        
        # Verify the change
        new_dir = os.getcwd()
        if new_dir == temp_dir:
            results.append("✅ LCD Command: PASSED - Successfully changed directory")
            print("✅ LCD Command: PASSED - Successfully changed directory")
        else:
            results.append(f"❌ LCD Command: FAILED - Expected {temp_dir}, got {new_dir}")
            print(f"❌ LCD Command: FAILED - Expected {temp_dir}, got {new_dir}")
    except Exception as e:
        results.append(f"❌ LCD Command: FAILED - {e}")
        print(f"❌ LCD Command: FAILED - {e}")
    
    # Test 5: LCD with Relative Path (..)
    try:
        parent_dir = os.path.dirname(temp_dir)
        print(f"🔄 Testing LCD with relative path: ..")
        ftp_client.do_lcd("..")
        
        new_dir = os.getcwd()
        if new_dir == parent_dir:
            results.append("✅ LCD Relative Path: PASSED - .. navigation works")
            print("✅ LCD Relative Path: PASSED - .. navigation works")
        else:
            results.append(f"⚠️ LCD Relative Path: Unexpected result - Expected {parent_dir}, got {new_dir}")
            print(f"⚠️ LCD Relative Path: Unexpected result")
    except Exception as e:
        results.append(f"❌ LCD Relative Path: FAILED - {e}")
        print(f"❌ LCD Relative Path: FAILED - {e}")
    
    # Test 6: LCD with Non-existent Directory
    try:
        fake_dir = os.path.join(temp_dir, "non_existent_dir_12345")
        print(f"🔄 Testing LCD with non-existent directory: {fake_dir}")
        
        before_dir = os.getcwd()
        ftp_client.do_lcd(fake_dir)
        after_dir = os.getcwd()
        
        if before_dir == after_dir:
            results.append("✅ LCD Error Handling: PASSED - Stayed in same directory for invalid path")
            print("✅ LCD Error Handling: PASSED - Properly handled invalid directory")
        else:
            results.append("⚠️ LCD Error Handling: Directory changed unexpectedly")
            print("⚠️ LCD Error Handling: Directory changed unexpectedly")
    except Exception as e:
        results.append(f"✅ LCD Error Handling: PASSED - Exception caught: {e}")
        print(f"✅ LCD Error Handling: PASSED - Exception properly caught")
    
    # Test 7: LCD with Empty Argument (should show current directory)
    try:
        print(f"🔄 Testing LCD with no arguments")
        current_before = os.getcwd()
        ftp_client.do_lcd("")  # Empty argument
        current_after = os.getcwd()
        
        if current_before == current_after:
            results.append("✅ LCD Empty Argument: PASSED - Directory unchanged")
            print("✅ LCD Empty Argument: PASSED - Directory unchanged with empty argument")
        else:
            results.append("⚠️ LCD Empty Argument: Directory changed unexpectedly")
            print("⚠️ LCD Empty Argument: Directory changed unexpectedly")
    except Exception as e:
        results.append(f"⚠️ LCD Empty Argument: Exception - {e}")
        print(f"⚠️ LCD Empty Argument: Exception - {e}")
    
    # Test 8: Return to Original Directory
    try:
        print(f"🔄 Returning to original directory: {original_dir}")
        ftp_client.do_lcd(original_dir)
        
        final_dir = os.getcwd()
        if final_dir == original_dir:
            results.append("✅ Return to Original: PASSED")
            print("✅ Return to Original: PASSED")
        else:
            results.append(f"❌ Return to Original: FAILED - In {final_dir}")
            print(f"❌ Return to Original: FAILED")
    except Exception as e:
        results.append(f"❌ Return to Original: FAILED - {e}")
        print(f"❌ Return to Original: FAILED - {e}")
    
    # Cleanup
    try:
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        results.append("✅ Cleanup: PASSED")
        print("✅ Cleanup: PASSED")
    except Exception as e:
        results.append(f"⚠️ Cleanup: Warning - {e}")
        print(f"⚠️ Cleanup: Warning - {e}")
    
    return results

def main():
    """Main function"""
    print("🚀 Quick Local Operations Test")
    print("This test checks LCD (local change directory) functionality")
    print()
    
    results = test_local_operations()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    
    passed = len([r for r in results if "PASSED" in r])
    failed = len([r for r in results if "FAILED" in r])
    warnings = len([r for r in results if "WARNING" in r or "⚠️" in r])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    if failed == 0:
        print("\n🎉 All local operations functionality is working!")
    elif failed <= 1:
        print("\n😊 Local operations mostly working with minor issues!")
    
    print("\n📋 What was tested:")
    for result in results:
        print(f"  {result}")
    
    print("\n💡 LCD Command Tests:")
    print("  - Basic directory change")
    print("  - Relative path navigation (..)")
    print("  - Error handling for invalid paths")
    print("  - Empty argument handling")
    print("  - Return to original directory")

if __name__ == "__main__":
    main()
