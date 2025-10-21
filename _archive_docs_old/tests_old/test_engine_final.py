#!/usr/bin/env python3
"""
🧪 Test DeviceIntelligenceEngine - API réelle

Test des vraies méthodes de l'engine.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.core.device_intelligence import (
    DeviceIntelligenceEngine,
    DeviceData
)


def test_merge_device_data():
    """Test fusion multi-sources"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Fusion multi-sources")
    print("="*60)
    
    engine = DeviceIntelligenceEngine()
    
    # 3 sources pour le même device
    sources = [
        DeviceData(
            mac="3c:22:fb:aa:bb:cc",
            ip="192.168.1.10",
            hostname="TITO",
            vendor="Apple",
            source="nmap",
            is_online=True,
            response_time_ms=5.2,
            timestamp=datetime.now()
        ),
        DeviceData(
            mac="3c:22:fb:aa:bb:cc",
            ip="192.168.1.10",
            hostname="TITO.local",
            source="mdns",
            is_online=True,
            timestamp=datetime.now()
        ),
        DeviceData(
            mac="3c:22:fb:aa:bb:cc",
            ip="192.168.1.10",
            vendor="Apple Inc.",
            source="arp",
            is_online=True,
            timestamp=datetime.now()
        ),
    ]
    
    print(f"\n📥 {len(sources)} sources:")
    for s in sources:
        print(f"   • {s.source}: hostname={s.hostname}, vendor={s.vendor}")
    
    merged = engine.merge_device_data(sources)
    
    print(f"\n📤 Résultat fusionné:")
    print(f"   MAC: {merged['mac']}")
    print(f"   IP: {merged['ip']}")
    print(f"   Hostname: {merged['hostname']}")
    print(f"   Vendor: {merged['vendor']}")
    print(f"   Sources: {merged['sources']}")
    print(f"   Response time: {merged.get('response_time_ms', 'N/A')}")
    
    assert merged['mac'].upper() == "3C:22:FB:AA:BB:CC"
    assert len(merged['sources']) == 3
    assert "nmap" in merged['sources']
    print("   ✅ Fusion OK")


def test_detect_changes():
    """Test détection changements"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Détection de changements")
    print("="*60)
    
    engine = DeviceIntelligenceEngine()
    
    # État précédent
    previous = {
        'mac': '3c:22:fb:aa:bb:cc',
        'ip': '192.168.1.10',
        'hostname': 'TITO',
        'vendor': 'Apple',
        'is_online': True,
        'sources': ['nmap']
    }
    
    # État actuel (IP changée)
    current = {
        'mac': '3c:22:fb:aa:bb:cc',
        'ip': '192.168.1.15',  # ❗ IP changée
        'hostname': 'TITO',
        'vendor': 'Apple',
        'is_online': True,
        'sources': ['nmap']
    }
    
    print(f"\n📊 État précédent: IP={previous['ip']}")
    print(f"   État actuel:    IP={current['ip']}")
    
    changes = engine.detect_changes(previous, current)
    
    print(f"\n📢 Changements détectés: {len(changes)}")
    for change in changes:
        print(f"   • {change.change_type.value}")
        print(f"     {change.old_value} → {change.new_value}")
        print(f"     Confidence: {change.confidence:.2f}")
    
    assert len(changes) > 0, "Should detect IP change"
    assert changes[0].change_type.value == "ip_changed"
    print("   ✅ IP_CHANGED détecté")


def test_calculate_confidence():
    """Test calcul de confiance"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Calcul de confiance")
    print("="*60)
    
    engine = DeviceIntelligenceEngine()
    
    # Test 1: Source unique, old data
    sources1 = [
        DeviceData(
            mac="aa:bb:cc:dd:ee:ff",
            ip="192.168.1.100",
            source="arp",
            is_online=True,
            timestamp=datetime.now() - timedelta(hours=2)  # Vieilles données
        )
    ]
    device1 = {'mac': 'AA:BB:CC:DD:EE:FF', 'ip': '192.168.1.100'}
    
    conf1 = engine.calculate_confidence(device1, sources1)
    print(f"\n1️⃣  Source unique (arp) + données anciennes (2h)")
    print(f"   Confidence: {conf1:.2f}")
    assert conf1 < 0.7, f"Confidence trop haute: {conf1}"
    
    # Test 2: Multi-sources, fresh data
    sources2 = [
        DeviceData(
            mac="aa:bb:cc:dd:ee:ff",
            ip="192.168.1.100",
            hostname="test-device",
            vendor="Apple",
            source="nmap",
            is_online=True,
            response_time_ms=3.2,
            timestamp=datetime.now()
        ),
        DeviceData(
            mac="aa:bb:cc:dd:ee:ff",
            ip="192.168.1.100",
            hostname="test-device.local",
            source="mdns",
            is_online=True,
            timestamp=datetime.now()
        ),
        DeviceData(
            mac="aa:bb:cc:dd:ee:ff",
            ip="192.168.1.100",
            vendor="Apple Inc.",
            source="freebox",
            is_online=True,
            timestamp=datetime.now()
        )
    ]
    device2 = {'mac': 'AA:BB:CC:DD:EE:FF', 'ip': '192.168.1.100'}
    
    conf2 = engine.calculate_confidence(device2, sources2)
    print(f"\n2️⃣  Multi-sources (3: nmap+mdns+freebox) + données fraîches")
    print(f"   Confidence: {conf2:.2f}")
    assert conf2 > 0.7, f"Confidence trop basse: {conf2}"
    
    print("   ✅ Confiance calculée correctement")


def test_detect_conflicts():
    """Test détection de conflits IP"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Détection de conflits")
    print("="*60)
    
    engine = DeviceIntelligenceEngine()
    
    # 2 devices avec la même IP (conflit!)
    devices = [
        {
            'mac': '11:11:11:11:11:11',
            'ip': '192.168.1.100',
            'hostname': 'device1',
            'is_online': True
        },
        {
            'mac': '22:22:22:22:22:22',
            'ip': '192.168.1.100',  # ❗ Même IP
            'hostname': 'device2',
            'is_online': True
        }
    ]
    
    print(f"\n⚠️  2 devices avec IP=192.168.1.100")
    conflicts = engine.detect_conflicts(devices)
    
    print(f"\n📢 Conflits détectés: {len(conflicts)}")
    for conflict in conflicts:
        print(f"   • {conflict.conflict_type.value}")
        print(f"     Devices: {[m[:17] for m in conflict.affected_devices]}")
        print(f"     Sévérité: {conflict.severity}")
    
    assert len(conflicts) > 0, "Should detect IP conflict"
    print("   ✅ Conflit IP détecté")


def test_calculate_uptime():
    """Test calcul uptime"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Calcul d'uptime")
    print("="*60)
    
    engine = DeviceIntelligenceEngine()
    
    # Historique fictif: 3 scans sur 2h, 2 online, 1 offline
    history = [
        {
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'mac': '3c:22:fb:aa:bb:cc',
            'is_online': True,
            'response_time_ms': 5.2
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
            'mac': '3c:22:fb:aa:bb:cc',
            'is_online': True,
            'response_time_ms': 4.8
        },
        {
            'timestamp': datetime.now().isoformat(),
            'mac': '3c:22:fb:aa:bb:cc',
            'is_online': False  # Offline maintenant
        }
    ]
    
    stats = engine.calculate_uptime(history)
    
    print(f"\n📊 Statistiques uptime:")
    print(f"   Total scans: {stats.total_scans}")
    print(f"   Total detections: {stats.total_detections}")
    print(f"   Detection rate: {stats.detection_rate:.1%}")
    print(f"   Uptime: {stats.uptime_percentage:.1f}%")
    print(f"   Latence moyenne: {stats.average_latency_ms:.2f}ms")
    
    assert stats.total_scans == 3
    assert stats.total_detections == 2  # 2 online
    print("   ✅ Uptime calculé")


def main():
    """Run all tests"""
    print("\n🏠 333HOME - DeviceIntelligenceEngine Validation\n")
    
    try:
        test_merge_device_data()
        test_detect_changes()
        test_calculate_confidence()
        test_detect_conflicts()
        test_calculate_uptime()
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS RÉUSSIS")
        print("="*60)
        print("\n💡 DeviceIntelligenceEngine validé:")
        print("   • merge_device_data() ✅")
        print("   • detect_changes() ✅")
        print("   • calculate_confidence() ✅")
        print("   • detect_conflicts() ✅")
        print("   • calculate_uptime() ✅")
        print("\n📋 Phase 1 (Core Engine) COMPLÈTE")
        print("🚀 Prêt pour Phase 2: MultiSourceScanner + Freebox")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
