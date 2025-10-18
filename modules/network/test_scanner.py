"""
Test du module de scan réseau avancé
Script pour tester les fonctionnalités du scanner
"""

import sys
import os
import json
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire parent au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.network import NetworkScanner, DeviceIdentifier, MacVendorAPI, network_api

def test_network_interfaces():
    """Tester la récupération des interfaces réseau"""
    print("=== Test des interfaces réseau ===")
    
    scanner = NetworkScanner()
    interfaces = scanner.get_network_interfaces()
    
    print(f"Interfaces trouvées: {len(interfaces)}")
    for interface in interfaces:
        print(f"  {interface['interface']}: {interface['ip']} ({interface['cidr']})")
    
    default_network = scanner.get_default_network()
    print(f"Réseau par défaut: {default_network}")
    print()

def test_mac_vendor_api():
    """Tester l'API des fabricants MAC"""
    print("=== Test de l'API MAC Vendor ===")
    
    mac_api = MacVendorAPI()
    
    # Tester quelques MACs connus
    test_macs = [
        "00:1B:63:84:45:E6",  # Apple
        "08:00:27:12:34:56",  # Oracle VirtualBox
        "52:54:00:12:34:56",  # QEMU/KVM
        "B8:27:EB:12:34:56"   # Raspberry Pi
    ]
    
    for mac in test_macs:
        print(f"MAC: {mac}")
        vendor_info = mac_api.get_vendor_info(mac)
        print(f"  Vendor: {vendor_info.get('vendor', 'Unknown')}")
        print(f"  Source: {vendor_info.get('source', 'N/A')}")
        print(f"  Confidence: {vendor_info.get('confidence', 'N/A')}")
        print()

def test_device_identifier():
    """Tester l'identification des appareils"""
    print("=== Test de l'identification des appareils ===")
    
    identifier = DeviceIdentifier()
    
    # Simuler des appareils de test
    test_devices = [
        {
            'ip': '192.168.1.10',
            'hostname': 'iPhone-de-John',
            'mac_address': '00:1B:63:84:45:E6',
            'services': ['5353']
        },
        {
            'ip': '192.168.1.20',
            'hostname': 'DESKTOP-ABC123',
            'mac_address': '08:00:27:12:34:56',
            'services': ['135', '139', '445']
        },
        {
            'ip': '192.168.1.1',
            'hostname': 'livebox',
            'mac_address': 'AA:BB:CC:DD:EE:FF',
            'services': ['80', '443', '23']
        }
    ]
    
    for device in test_devices:
        print(f"Appareil: {device['ip']} ({device['hostname']})")
        identification = identifier.identify_device_type(device)
        print(f"  Type: {identification['device_type']}")
        print(f"  Confidence: {identification['confidence']}")
        print(f"  Score: {identification['score']:.2f}")
        print()

def test_quick_scan():
    """Tester un scan rapide"""
    print("=== Test de scan rapide ===")
    
    # Utiliser l'API unifiée
    result = network_api.quick_scan()
    
    if result['success']:
        devices = result['data'].get('devices', [])
        print(f"Scan terminé: {len(devices)} appareils trouvés")
        
        for device in devices[:3]:  # Afficher seulement les 3 premiers
            basic = device['basic_info']
            identification = device['identification']
            print(f"  {basic['ip']} - {basic['hostname']} - {identification['device_type']}")
    else:
        print(f"Erreur: {result['message']}")
    print()

def test_network_api():
    """Tester l'API réseau complète"""
    print("=== Test de l'API réseau ===")
    
    # Test des interfaces
    interfaces_result = network_api.get_network_interfaces()
    if interfaces_result['success']:
        interfaces = interfaces_result['data']['interfaces']
        print(f"Interfaces: {len(interfaces)} trouvées")
    
    # Test du cache
    cache_stats = network_api.get_cache_stats()
    if cache_stats['success']:
        stats = cache_stats['data']
        print(f"Cache: {stats['cache_size']} entrées")
    
    print()

def main():
    """Fonction principale de test"""
    print("Démarrage des tests du module de scan réseau avancé\n")
    
    try:
        test_network_interfaces()
        test_mac_vendor_api()
        test_device_identifier()
        test_network_api()
        test_quick_scan()
        
        print("=== Tests terminés ===")
        
    except Exception as e:
        print(f"Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()