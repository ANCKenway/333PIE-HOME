"""
🏠 333HOME - Unified Device Service

Service unifié qui agrège les données de toutes les sources :
- devices.json (managed devices)
- network_scan_history.json (auto-discovered)
- tailscale (VPN) - TODO

Fournit une vue unifiée avec enrichissement automatique.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from src.features.devices.manager import DeviceManager
from src.features.network.storage import get_all_devices as get_network_devices, get_device_by_mac
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Singleton DeviceManager
device_manager = DeviceManager()


class UnifiedDevice:
    """Device unifié avec données de toutes les sources"""
    
    def __init__(self, data: Dict[str, Any]):
        # IDs
        self.id = data.get('id')
        self.mac = data.get('mac', '').upper()
        
        # Infos de base
        self.name = data.get('name', 'Unknown')
        self.ip = data.get('ip')
        self.hostname = data.get('hostname')
        
        # Source tracking
        self.in_devices = data.get('in_devices', False)
        self.in_network = data.get('in_network', False)
        self.source = self._determine_source()
        
        # Device info
        self.type = data.get('type', 'unknown')
        self.description = data.get('description')
        self.vendor = data.get('vendor')
        self.device_type = data.get('device_type')
        self.os_detected = data.get('os_detected')
        
        # Status
        self.online = data.get('online', False)
        self.last_seen = data.get('last_seen')
        self.first_seen = data.get('first_seen')
        
        # Capabilities
        self.wake_on_lan = data.get('wake_on_lan', False)
        self.can_ping = True  # Tous les devices peuvent être pingés
        
        # VPN
        self.vpn_ip = data.get('vpn_ip')
        
        # Metadata
        self.tags = data.get('tags', [])
        self.metadata = data.get('metadata', {})
        
        # Stats
        self.total_scans = data.get('total_scans', 0)
        
    def _determine_source(self) -> str:
        """Détermine la source du device"""
        if self.in_devices and self.in_network:
            return 'both'
        elif self.in_devices:
            return 'devices'
        elif self.in_network:
            return 'network'
        return 'unknown'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dict pour API"""
        return {
            'id': self.id,
            'mac': self.mac,
            'name': self.name,
            'ip': self.ip,
            'hostname': self.hostname,
            
            'source': self.source,
            'in_devices': self.in_devices,
            'in_network': self.in_network,
            
            'type': self.type,
            'description': self.description,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'os_detected': self.os_detected,
            
            'online': self.online,
            'last_seen': self.last_seen,
            'first_seen': self.first_seen,
            
            'capabilities': {
                'wake_on_lan': self.wake_on_lan,
                'ping': self.can_ping,
            },
            
            'vpn_ip': self.vpn_ip,
            'tags': self.tags,
            'metadata': self.metadata,
            'total_scans': self.total_scans,
        }


def get_unified_devices() -> List[UnifiedDevice]:
    """
    Récupère tous les devices en unifiant les sources
    
    Returns:
        Liste de UnifiedDevice
    """
    unified = {}
    
    # 1. Charger devices managés (source principale)
    try:
        devices_list = device_manager.get_all_devices()
        for device in devices_list:
            mac = device.get('mac', '').upper()
            if not mac:
                continue
            
            # Extraire VPN IP depuis metadata
            metadata = device.get('metadata', {})
            vpn_info = metadata.get('vpn', {})
            vpn_ip = (
                vpn_info.get('tailscale_ip') or  # metadata.vpn.tailscale_ip
                metadata.get('ip_secondary') or   # metadata.ip_secondary
                metadata.get('vpn_ip')            # metadata.vpn_ip (fallback)
            )
            
            unified[mac] = {
                'id': device.get('id'),
                'mac': mac,
                'name': device.get('name', 'Unknown'),
                'ip': device.get('ip'),
                'hostname': device.get('hostname'),
                'type': device.get('type', 'unknown'),
                'description': device.get('description'),
                'tags': device.get('tags', []),
                'metadata': metadata,
                'in_devices': True,
                'in_network': False,
                'online': False,  # Sera mis à jour par network si disponible
                'wake_on_lan': metadata.get('wake_on_lan', False),
                'vpn_ip': vpn_ip,
                'first_seen': device.get('created_at'),
                'last_seen': device.get('updated_at'),
                'total_scans': 0,
            }
    except Exception as e:
        logger.error(f"❌ Error loading devices: {e}")
    
    # 2. Enrichir avec données network
    try:
        network_devices = get_network_devices()
        for net_device in network_devices:
            mac = net_device.mac.upper()
            
            if mac in unified:
                # Enrichir device existant
                device = unified[mac]
                device['in_network'] = True
                device['vendor'] = net_device.vendor or device.get('vendor')
                device['device_type'] = net_device.device_type or device.get('device_type')
                device['os_detected'] = net_device.os_detected or device.get('os_detected')
                device['online'] = net_device.currently_online
                device['last_seen'] = net_device.last_seen.isoformat() if net_device.last_seen else device.get('last_seen')
                device['total_scans'] = net_device.total_appearances
                
                # Mettre à jour IP/hostname si plus récent
                if net_device.currently_online:
                    device['ip'] = net_device.current_ip or device.get('ip')
                    device['hostname'] = net_device.current_hostname or device.get('hostname')
            else:
                # Nouveau device depuis network
                unified[mac] = {
                    'id': net_device.id,
                    'mac': mac,
                    'name': net_device.current_hostname or net_device.vendor or 'Unknown',
                    'ip': net_device.current_ip,
                    'hostname': net_device.current_hostname,
                    'type': 'unknown',
                    'description': None,
                    'vendor': net_device.vendor,
                    'device_type': net_device.device_type,
                    'os_detected': net_device.os_detected,
                    'tags': net_device.tags,
                    'metadata': {},
                    'in_devices': False,
                    'in_network': True,
                    'online': net_device.currently_online,
                    'wake_on_lan': False,
                    'vpn_ip': None,
                    'first_seen': net_device.first_seen.isoformat() if net_device.first_seen else None,
                    'last_seen': net_device.last_seen.isoformat() if net_device.last_seen else None,
                    'total_scans': net_device.total_appearances,
                }
    except Exception as e:
        logger.error(f"❌ Error loading network devices: {e}")
    
    # 3. Vérifier le statut online des devices managés sans données réseau
    # via ping rapide (pour sync temps réel)
    try:
        import subprocess
        for mac, data in unified.items():
            if data['in_devices'] and not data['in_network'] and data.get('ip'):
                # Ping rapide (timeout 1s) pour vérifier si online
                try:
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', data['ip']],
                        capture_output=True,
                        timeout=2
                    )
                    is_online = result.returncode == 0
                    data['online'] = is_online
                    if is_online:
                        data['last_seen'] = datetime.now().isoformat()
                        logger.debug(f"✅ Ping OK: {data['name']} ({data['ip']})")
                except Exception as e:
                    logger.debug(f"⚠️ Ping failed for {data['name']}: {e}")
                    data['online'] = False
    except Exception as e:
        logger.warning(f"⚠️ Live ping check failed: {e}")
    
    # 4. Convertir en UnifiedDevice
    result = [UnifiedDevice(data) for data in unified.values()]
    
    # 5. Trier par last_seen (plus récent en premier)
    result.sort(
        key=lambda d: d.last_seen or '1970-01-01',
        reverse=True
    )
    
    logger.info(f"📊 Unified devices: {len(result)} total (online: {sum(1 for d in result if d.online)})")
    return result


def get_unified_device_by_mac(mac: str) -> Optional[UnifiedDevice]:
    """Récupère un device unifié par MAC"""
    devices = get_unified_devices()
    mac_upper = mac.upper()
    
    for device in devices:
        if device.mac == mac_upper:
            return device
    
    return None


def get_unified_device_by_id(device_id: str) -> Optional[UnifiedDevice]:
    """Récupère un device unifié par ID"""
    devices = get_unified_devices()
    
    for device in devices:
        if device.id == device_id:
            return device
    
    return None


def get_devices_stats() -> Dict[str, Any]:
    """Stats globales des devices"""
    devices = get_unified_devices()
    
    return {
        'total': len(devices),
        'online': sum(1 for d in devices if d.online),
        'offline': sum(1 for d in devices if not d.online),
        'managed': sum(1 for d in devices if d.in_devices),
        'discovered': sum(1 for d in devices if d.in_network and not d.in_devices),
        'both': sum(1 for d in devices if d.in_devices and d.in_network),
    }
