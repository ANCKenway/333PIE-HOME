"""
🏠 333HOME - Network Service Unifié

Service principal combinant MultiSourceScanner + DeviceIntelligenceEngine.
Remplace progressivement l'ancien système network/storage.py.

Architecture:
1. MultiSourceScanner: Scan multi-sources (nmap+ARP+mDNS+NetBIOS)
2. DeviceIntelligenceEngine: Fusion intelligente + détection changements
3. UnifiedDevice: Modèle de données complet
4. Persistance JSON: devices_unified.json

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 2-3
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.network.multi_source_scanner import MultiSourceScanner
from src.core.models.unified_device import UnifiedDevice
from src.core.config import get_settings

settings = get_settings()


class NetworkServiceUnified:
    """
    Service unifié de gestion réseau
    
    Centralise:
    - Scan multi-sources
    - Fusion intelligente des données
    - Détection changements
    - Persistance
    - Statistiques
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.scanner = MultiSourceScanner(subnet)
        self.storage_file = settings.data_dir / "devices_unified.json"
        self.devices: Dict[str, UnifiedDevice] = {}
        
        # Charger devices existants
        self._load_devices()
    
    def _load_devices(self):
        """Charge les devices depuis le fichier JSON"""
        if not self.storage_file.exists():
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            for mac, device_dict in data.get('devices', {}).items():
                try:
                    device = UnifiedDevice.from_dict(device_dict)
                    self.devices[mac] = device
                except Exception as e:
                    print(f"Error loading device {mac}: {e}")
        
        except Exception as e:
            print(f"Error loading devices: {e}")
    
    def _save_devices(self):
        """Sauvegarde les devices dans le fichier JSON"""
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'devices': {
                    mac: device.to_dict()
                    for mac, device in self.devices.items()
                }
            }
            
            # Backup si le fichier existe
            if self.storage_file.exists():
                backup_file = self.storage_file.with_suffix('.json.backup')
                self.storage_file.rename(backup_file)
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        except Exception as e:
            print(f"Error saving devices: {e}")
    
    async def scan_network(self) -> List[UnifiedDevice]:
        """
        Lance un scan complet du réseau
        
        Returns:
            Liste des devices trouvés
        """
        # Scanner via MultiSourceScanner
        devices = await self.scanner.scan_all()
        
        # Mettre à jour notre cache
        for device in devices:
            self.devices[device.mac] = device
        
        # Sauvegarder
        self._save_devices()
        
        return devices
    
    def get_all_devices(self) -> List[UnifiedDevice]:
        """Retourne tous les devices connus"""
        return list(self.devices.values())
    
    def get_device(self, mac: str) -> Optional[UnifiedDevice]:
        """Retourne un device par MAC"""
        return self.devices.get(mac.upper())
    
    def get_online_devices(self) -> List[UnifiedDevice]:
        """Retourne seulement les devices online"""
        return [d for d in self.devices.values() if d.is_online]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques réseau"""
        devices = list(self.devices.values())
        
        if not devices:
            return {
                'total_devices': 0,
                'online_devices': 0,
                'offline_devices': 0,
                'avg_confidence': 0.0,
                'avg_uptime': 0.0
            }
        
        online = sum(1 for d in devices if d.is_online)
        avg_conf = sum(d.confidence_score for d in devices) / len(devices)
        avg_uptime = sum(d.uptime_percentage for d in devices) / len(devices)
        
        return {
            'total_devices': len(devices),
            'online_devices': online,
            'offline_devices': len(devices) - online,
            'avg_confidence': round(avg_conf, 2),
            'avg_uptime': round(avg_uptime, 1),
            'last_scan': max((d.last_seen for d in devices if d.last_seen), default=None)
        }
    
    def get_device_history(self, mac: str) -> Optional[Dict[str, Any]]:
        """Historique d'un device"""
        device = self.get_device(mac)
        if not device:
            return None
        
        return {
            'mac': device.mac,
            'current_state': device.to_dict(),
            'ip_history': [change.to_dict() for change in device.ip_history],
            'hostname_history': [change.to_dict() for change in device.hostname_history],
            'uptime_periods': [period.to_dict() for period in device.uptime_periods],
            'statistics': {
                'total_scans': device.total_scans_detected,
                'uptime_percentage': device.uptime_percentage,
                'average_latency_ms': device.average_latency_ms,
                'first_seen': device.first_seen.isoformat() if device.first_seen else None,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None
            }
        }


# === SINGLETON ===

_service_instance: Optional[NetworkServiceUnified] = None


def get_network_service(subnet: str = "192.168.1.0/24") -> NetworkServiceUnified:
    """Retourne l'instance singleton du service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = NetworkServiceUnified(subnet)
    return _service_instance


# === CLI pour tests ===

async def main():
    """Test CLI"""
    print("\n🏠 333HOME - Network Service Unified Test\n")
    
    service = get_network_service()
    
    print("📡 Scanning network...")
    devices = await service.scan_network()
    
    print(f"\n✅ Found {len(devices)} devices\n")
    
    stats = service.get_statistics()
    print("📊 Statistics:")
    print(f"   Total: {stats['total_devices']}")
    print(f"   Online: {stats['online_devices']}")
    print(f"   Avg confidence: {stats['avg_confidence']}")
    print(f"   Avg uptime: {stats['avg_uptime']}%")
    
    print("\n📋 Devices:")
    for device in service.get_online_devices()[:10]:
        print(f"   {device.mac:<20} {device.current_ip:<15} {device.display_name:<30} [{'⬆' * len(device.sources)}]")


if __name__ == "__main__":
    asyncio.run(main())
