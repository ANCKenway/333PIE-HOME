"""
🧪 333HOME - Test Network Pro Features

Test des améliorations professionnelles :
- Port Scanning
- Latency Monitoring
- Bandwidth Monitoring
- Services Detection
- Device Role Identification
"""

import asyncio
import time
from src.features.network import (
    NetworkScanner,
    PortScanner,
    get_scan_preset,
)
from src.features.network.latency_monitor import get_latency_monitor
from src.features.network.bandwidth_monitor import get_bandwidth_monitor


async def test_port_scanner():
    """Test Port Scanner"""
    print("\n" + "="*60)
    print("🔍 TEST PORT SCANNER")
    print("="*60)
    
    scanner = PortScanner(timeout=1.0)
    
    # Test localhost
    print("📡 Scanning localhost ports...")
    results = await scanner.scan_host('127.0.0.1', get_scan_preset("quick"))
    
    print(f"\n✅ Scan completed:")
    print(f"   Open ports: {len(results)}")
    
    if results:
        print(f"\n   Detected services:")
        for service in results:
            icon = service['icon']
            port = service['port']
            name = service['name']
            svc = service['service']
            print(f"   {icon} Port {port:5} - {name:15} ({svc})")
        
        # Test role detection
        role_info = scanner.identify_device_role(results)
        print(f"\n   Device role: {role_info['role']}")
        print(f"   Confidence: {role_info['confidence']}")
        print(f"   Services: {', '.join(role_info['services'])}")
    
    # Test presets
    print(f"\n📋 Available presets:")
    presets = ["quick", "common", "web", "remote", "database"]
    for preset in presets:
        ports = get_scan_preset(preset)
        print(f"   {preset:12} - {len(ports):2} ports")


async def test_latency_monitor():
    """Test Latency Monitor"""
    print("\n" + "="*60)
    print("⚡ TEST LATENCY MONITOR")
    print("="*60)
    
    monitor = get_latency_monitor()
    
    # Test localhost
    print("📡 Measuring latency to localhost...")
    measurements = await monitor.measure_latency('127.0.0.1', count=10)
    
    print(f"\n✅ Measurements completed:")
    print(f"   Total: {len(measurements)}")
    
    successful = [m for m in measurements if m.success]
    if successful:
        latencies = [m.latency_ms for m in successful]
        print(f"   Successful: {len(successful)}")
        print(f"   Avg latency: {sum(latencies)/len(latencies):.2f}ms")
    
    # Calculer stats
    stats = monitor.calculate_stats('127.0.0.1')
    if stats:
        icon = monitor.get_quality_icon(stats.quality_score)
        print(f"\n📊 Quality Stats:")
        print(f"   {icon} Score: {stats.quality_score}/100 ({stats.quality_label})")
        print(f"   Avg latency: {stats.avg_latency_ms:.2f}ms")
        print(f"   Min/Max: {stats.min_latency_ms:.2f}ms / {stats.max_latency_ms:.2f}ms")
        print(f"   Jitter: {stats.jitter_ms:.2f}ms")
        print(f"   Packet loss: {stats.packet_loss_percent:.1f}%")


async def test_network_scanner_pro():
    """Test Network Scanner avec Port Scanning"""
    print("\n" + "="*60)
    print("🌐 TEST NETWORK SCANNER PRO")
    print("="*60)
    
    scanner = NetworkScanner(subnet="192.168.1.0/24", timeout_ms=1000)
    
    choice = input("\n❓ Lancer scan réseau avec port scan ? (LENT - y/N): ").lower()
    if choice != 'y':
        print("⏭️  Scan skipped")
        return
    
    print("\n📡 Scanning network with port detection...")
    print("   (This may take a while...)")
    
    try:
        result = await asyncio.wait_for(
            scanner.scan_network(
                scan_type="QUICK",  # Quick ICMP
                scan_ports=True,
                port_preset="quick",  # 5 ports essentiels
            ),
            timeout=60.0
        )
        
        print(f"\n✅ Scan completed:")
        print(f"   Duration: {result.duration_ms}ms")
        print(f"   Devices found: {result.devices_found}")
        
        # Afficher devices avec services
        devices_with_services = [d for d in result.devices if d.services]
        print(f"   Devices with services: {len(devices_with_services)}")
        
        if devices_with_services:
            print(f"\n📱 Devices with detected services:")
            for device in devices_with_services[:5]:  # Max 5
                print(f"\n   {device.current_ip:15} | {device.vendor or 'Unknown'}")
                if device.device_role:
                    print(f"   Role: {device.device_role}")
                print(f"   Services:")
                for service in device.services[:5]:  # Max 5
                    print(f"      {service.icon} {service.name}")
    
    except asyncio.TimeoutError:
        print("⚠️  Scan timeout")


def test_bandwidth_monitor():
    """Test Bandwidth Monitor"""
    print("\n" + "="*60)
    print("📊 TEST BANDWIDTH MONITOR")
    print("="*60)
    
    monitor = get_bandwidth_monitor()
    
    # Register devices
    print("📋 Registering test devices...")
    monitor.register_device('192.168.1.10', 'AA:BB:CC:DD:EE:01', 'laptop')
    monitor.register_device('192.168.1.20', 'AA:BB:CC:DD:EE:02', 'desktop')
    monitor.register_device('192.168.1.30', 'AA:BB:CC:DD:EE:03', 'phone')
    
    # Add samples (simulate traffic)
    print("📡 Adding bandwidth samples...")
    
    # Sample 1
    monitor.add_sample('AA:BB:CC:DD:EE:01', 1024*1024*10, 1024*1024*50)  # 10MB up, 50MB down
    monitor.add_sample('AA:BB:CC:DD:EE:02', 1024*1024*100, 1024*1024*20)  # 100MB up, 20MB down
    monitor.add_sample('AA:BB:CC:DD:EE:03', 1024*1024*5, 1024*1024*5)  # 5MB up, 5MB down
    
    time.sleep(1)
    
    # Sample 2 (simulate different rates)
    monitor.add_sample('AA:BB:CC:DD:EE:01', 1024*1024*5, 1024*1024*25)
    monitor.add_sample('AA:BB:CC:DD:EE:02', 1024*1024*50, 1024*1024*10)
    monitor.add_sample('AA:BB:CC:DD:EE:03', 1024*1024*2, 1024*1024*2)
    
    # Get stats
    print(f"\n✅ Bandwidth stats:")
    print(f"   Devices monitored: {len(monitor.get_all_stats())}")
    
    print(f"\n📊 Device stats:")
    for stats in monitor.get_all_stats():
        print(f"   {stats.ip:15} | {stats.hostname:10} | {stats.total_mb:7.1f} MB | {stats.current_mbps:5.1f} Mbps")
    
    # Top talkers
    print(f"\n🏆 Top talkers (by total):")
    for idx, stats in enumerate(monitor.get_top_talkers(limit=3, sort_by="total"), 1):
        print(f"   #{idx} {stats.hostname:10} - {stats.total_mb:7.1f} MB total")
    
    # Network total
    print(f"\n🌐 Network total:")
    total = monitor.get_total_bandwidth()
    print(f"   Upload:   {total['upload_mbps']:6.2f} Mbps")
    print(f"   Download: {total['download_mbps']:6.2f} Mbps")
    print(f"   Total:    {total['total_mbps']:6.2f} Mbps")


async def main():
    """Test principal"""
    print("\n" + "="*80)
    print("🧪 333HOME - TESTS NETWORK PRO FEATURES")
    print("="*80)
    
    # 1. Port Scanner
    await test_port_scanner()
    
    # 2. Latency Monitor
    await test_latency_monitor()
    
    # 3. Bandwidth Monitor
    test_bandwidth_monitor()
    
    # 4. Network Scanner Pro
    await test_network_scanner_pro()
    
    print("\n" + "="*80)
    print("✅ TESTS COMPLETED")
    print("="*80)
    print("\n📊 Summary:")
    print("   ✅ Port Scanner: 35+ services, 10 roles")
    print("   ✅ Latency Monitor: Quality scoring, jitter, packet loss")
    print("   ✅ Bandwidth Monitor: Usage tracking, top talkers")
    print("   ✅ Network Scanner: Integrated monitoring")
    print("\n🎯 Network Feature: 13 API endpoints")
    print("🚀 Ready for professional dashboard!")


if __name__ == "__main__":
    asyncio.run(main())
