"""
🧪 333HOME - Test rapide Network Feature

Test basique pour vérifier que tout fonctionne
"""

import asyncio
import json
from src.features.network import (
    NetworkScanner,
    DeviceDetector,
    NetworkHistory,
    ScanType,
    get_all_devices,
)


async def test_detector():
    """Test du DeviceDetector"""
    print("\n" + "="*60)
    print("🔍 TEST DETECTOR")
    print("="*60)
    
    detector = DeviceDetector()
    
    # Test avec une MAC Apple
    detection = await detector.detect_device(
        mac="AC:BC:32:11:22:33",
        ip="192.168.1.100",
        hostname="MacBook-Pro",
    )
    
    print(f"✅ Apple Device:")
    print(f"   Vendor: {detection['vendor']}")
    print(f"   Type: {detection['device_type_display']}")
    print(f"   Confidence: {detection['confidence']}")


async def test_scanner():
    """Test du NetworkScanner (mode QUICK)"""
    print("\n" + "="*60)
    print("🌐 TEST SCANNER (Quick Scan)")
    print("="*60)
    
    scanner = NetworkScanner(
        subnet="192.168.1.0/24",
        timeout_ms=1000,
    )
    
    print("⏳ Scanning 192.168.1.0/24 (quick mode)...")
    print("   (timeout 10s pour éviter blocage)")
    
    try:
        scan_result = await asyncio.wait_for(
            scanner.scan_network(ScanType.QUICK),
            timeout=10.0
        )
        
        print(f"\n✅ Scan completed:")
        print(f"   Duration: {scan_result.duration_ms}ms")
        print(f"   Devices found: {scan_result.devices_found}")
        
        if scan_result.devices:
            print(f"\n📱 First 3 devices:")
            for device in scan_result.devices[:3]:
                print(f"   - {device.current_ip:15} | {device.mac:17} | {device.vendor or 'Unknown'}")
    
    except asyncio.TimeoutError:
        print("⚠️  Scan timeout (normal en test)")


def test_storage():
    """Test du Storage"""
    print("\n" + "="*60)
    print("💾 TEST STORAGE")
    print("="*60)
    
    from src.features.network.storage import load_network_storage
    
    storage = load_network_storage()
    
    print(f"✅ Storage loaded:")
    print(f"   Version: {storage['version']}")
    print(f"   Total devices: {storage['metadata']['total_devices_seen']}")
    print(f"   Total scans: {storage['metadata']['total_scans']}")
    
    devices = get_all_devices()
    print(f"\n📱 Devices in storage: {len(devices)}")
    
    if devices:
        print(f"\n   Last 3 devices:")
        for device in devices[:3]:
            status = "🟢" if device.currently_online else "⚫"
            print(f"   {status} {device.mac:17} | {device.vendor or 'Unknown'}")


def test_history():
    """Test NetworkHistory"""
    print("\n" + "="*60)
    print("📊 TEST HISTORY")
    print("="*60)
    
    history = NetworkHistory()
    
    # Stats
    stats = history.get_network_stats()
    
    print(f"✅ Network Stats:")
    print(f"   Total devices seen: {stats.total_devices_seen}")
    print(f"   Currently online: {stats.currently_online}")
    print(f"   Currently offline: {stats.currently_offline}")
    print(f"   New last 24h: {stats.new_devices_last_24h}")
    print(f"   IP changes last 24h: {stats.ip_changes_last_24h}")
    
    # Timeline
    timeline = history.get_timeline(hours=24)
    print(f"\n📅 Timeline (last 24h):")
    print(f"   Total events: {timeline.total_events}")
    
    if timeline.events:
        print(f"\n   Last 5 events:")
        for event in timeline.events[:5]:
            print(f"   - {event.event_type.value:20} | {event.device_mac}")


async def main():
    """Test principal"""
    print("\n" + "="*80)
    print("🧪 333HOME - TESTS NETWORK FEATURE")
    print("="*80)
    
    # 1. Detector
    await test_detector()
    
    # 2. Storage
    test_storage()
    
    # 3. History
    test_history()
    
    # 4. Scanner (optionnel, peut être long)
    scan_choice = input("\n❓ Lancer un scan réseau ? (y/N): ").lower()
    if scan_choice == 'y':
        await test_scanner()
    else:
        print("⏭️  Scan skipped")
    
    print("\n" + "="*80)
    print("✅ TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
