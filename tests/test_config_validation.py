"""
Configuration Validation Test
Ensures Client config and Test config are synchronized
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

from test_config import TestConfig
try:
    from config import Config as ClientConfig
    CLIENT_CONFIG_AVAILABLE = True
except ImportError:
    CLIENT_CONFIG_AVAILABLE = False
    print("⚠️ Client config not available")

def test_config_sync():
    """Test that Client and Test configs are synchronized"""
    print("🔧 CONFIGURATION VALIDATION TEST")
    print("=" * 50)
    
    results = []
    
    if not CLIENT_CONFIG_AVAILABLE:
        results.append("❌ Client Config: Import failed")
        print("❌ Client Config: Import failed")
        return results
    
    # Test 1: FTP Host synchronization
    try:
        client_host = ClientConfig.FTP_HOST
        test_host = TestConfig.FTP_HOST
        
        if client_host == test_host:
            results.append(f"✅ FTP Host Sync: PASSED - Both use {client_host}")
            print(f"✅ FTP Host Sync: PASSED - Both use {client_host}")
        else:
            results.append(f"⚠️ FTP Host Sync: MISMATCH - Client: {client_host}, Test: {test_host}")
            print(f"⚠️ FTP Host Sync: MISMATCH - Client: {client_host}, Test: {test_host}")
    except Exception as e:
        results.append(f"❌ FTP Host Sync: ERROR - {e}")
        print(f"❌ FTP Host Sync: ERROR - {e}")
    
    # Test 2: FTP Port synchronization
    try:
        client_port = ClientConfig.FTP_PORT
        test_port = TestConfig.FTP_PORT
        
        if client_port == test_port:
            results.append(f"✅ FTP Port Sync: PASSED - Both use {client_port}")
            print(f"✅ FTP Port Sync: PASSED - Both use {client_port}")
        else:
            results.append(f"⚠️ FTP Port Sync: MISMATCH - Client: {client_port}, Test: {test_port}")
            print(f"⚠️ FTP Port Sync: MISMATCH - Client: {client_port}, Test: {test_port}")
    except Exception as e:
        results.append(f"❌ FTP Port Sync: ERROR - {e}")
        print(f"❌ FTP Port Sync: ERROR - {e}")
    
    # Test 3: ClamAV Host synchronization
    try:
        client_clamav_host = ClientConfig.CLAMAV_AGENT_HOST
        test_clamav_host = TestConfig.CLAMAV_HOST
        
        if client_clamav_host == test_clamav_host:
            results.append(f"✅ ClamAV Host Sync: PASSED - Both use {client_clamav_host}")
            print(f"✅ ClamAV Host Sync: PASSED - Both use {client_clamav_host}")
        else:
            results.append(f"⚠️ ClamAV Host Sync: MISMATCH - Client: {client_clamav_host}, Test: {test_clamav_host}")
            print(f"⚠️ ClamAV Host Sync: MISMATCH - Client: {client_clamav_host}, Test: {test_clamav_host}")
    except Exception as e:
        results.append(f"❌ ClamAV Host Sync: ERROR - {e}")
        print(f"❌ ClamAV Host Sync: ERROR - {e}")
    
    # Test 4: ClamAV Port synchronization
    try:
        client_clamav_port = ClientConfig.CLAMAV_AGENT_PORT
        test_clamav_port = TestConfig.CLAMAV_PORT
        
        if client_clamav_port == test_clamav_port:
            results.append(f"✅ ClamAV Port Sync: PASSED - Both use {client_clamav_port}")
            print(f"✅ ClamAV Port Sync: PASSED - Both use {client_clamav_port}")
        else:
            results.append(f"⚠️ ClamAV Port Sync: MISMATCH - Client: {client_clamav_port}, Test: {test_clamav_port}")
            print(f"⚠️ ClamAV Port Sync: MISMATCH - Client: {client_clamav_port}, Test: {test_clamav_port}")
    except Exception as e:
        results.append(f"❌ ClamAV Port Sync: ERROR - {e}")
        print(f"❌ ClamAV Port Sync: ERROR - {e}")
    
    # Test 5: Timeout availability in Client config
    try:
        if hasattr(ClientConfig, 'FTP_TIMEOUT'):
            client_ftp_timeout = ClientConfig.FTP_TIMEOUT
            results.append(f"✅ Client FTP Timeout: AVAILABLE - {client_ftp_timeout}s")
            print(f"✅ Client FTP Timeout: AVAILABLE - {client_ftp_timeout}s")
        else:
            results.append("⚠️ Client FTP Timeout: NOT AVAILABLE")
            print("⚠️ Client FTP Timeout: NOT AVAILABLE")
            
        if hasattr(ClientConfig, 'CLAMAV_TIMEOUT'):
            client_clamav_timeout = ClientConfig.CLAMAV_TIMEOUT
            results.append(f"✅ Client ClamAV Timeout: AVAILABLE - {client_clamav_timeout}s")
            print(f"✅ Client ClamAV Timeout: AVAILABLE - {client_clamav_timeout}s")
        else:
            results.append("⚠️ Client ClamAV Timeout: NOT AVAILABLE")
            print("⚠️ Client ClamAV Timeout: NOT AVAILABLE")
    except Exception as e:
        results.append(f"❌ Timeout Check: ERROR - {e}")
        print(f"❌ Timeout Check: ERROR - {e}")
    
    # Test 6: Helper methods availability
    try:
        if hasattr(ClientConfig, 'get_ftp_config'):
            host, port = ClientConfig.get_ftp_config()
            results.append(f"✅ Client Helper Methods: get_ftp_config() works - {host}:{port}")
            print(f"✅ Client Helper Methods: get_ftp_config() works - {host}:{port}")
        else:
            results.append("⚠️ Client Helper Methods: get_ftp_config() not available")
            print("⚠️ Client Helper Methods: get_ftp_config() not available")
    except Exception as e:
        results.append(f"❌ Helper Methods: ERROR - {e}")
        print(f"❌ Helper Methods: ERROR - {e}")
    
    return results

def main():
    """Main function"""
    print("🔧 Configuration Validation Test")
    print("This test ensures Client and Test configs are properly synchronized")
    print()
    
    results = test_config_sync()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONFIGURATION VALIDATION SUMMARY:")
    
    passed = len([r for r in results if "PASSED" in r])
    failed = len([r for r in results if "❌" in r])
    warnings = len([r for r in results if "⚠️" in r])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    if failed == 0 and warnings <= 1:
        print("\n🎉 Configuration synchronization is good!")
    elif warnings > 1:
        print("\n⚠️ Some configuration mismatches found - please review")
    else:
        print("\n❌ Configuration validation failed - please fix issues")
    
    print("\n📋 Validation Results:")
    for result in results:
        print(f"  {result}")
    
    print("\n💡 Configuration Best Practices:")
    print("  - Keep Client and Test configs synchronized")
    print("  - Use timeout settings to prevent hanging")
    print("  - Use helper methods for cleaner code")
    print("  - Keep credentials out of production config")

if __name__ == "__main__":
    main()
