"""
🌐 333HOME - Network Registry
Système de suivi persistant des devices réseau

Le NetworkRegistry est le fichier UNIQUE qui stocke TOUS les devices
jamais détectés sur le réseau avec leur historique complet:
- Changements d'IP (DHCP)
- Changements de hostname
- Historique de présence/absence
- Première et dernière détection
- Vendor, OS, services

Chaque scan ENRICHIT ce registry au lieu de créer une liste temporaire.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


logger = logging.getLogger(__name__)


# Singleton global pour partager une seule instance du registry
_registry_instance: Optional['NetworkRegistry'] = None


def get_network_registry() -> 'NetworkRegistry':
    """
    Récupérer l'instance singleton du NetworkRegistry
    
    Garantit qu'une seule instance existe et persiste en mémoire.
    Évite de recharger le fichier JSON à chaque requête API.
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = NetworkRegistry()
    return _registry_instance


@dataclass
class IPHistoryEntry:
    """Entrée d'historique IP"""
    ip: str
    first_seen: str
    last_seen: str
    occurrences: int = 1


@dataclass
class HostnameHistoryEntry:
    """Entrée d'historique hostname"""
    hostname: str
    first_seen: str
    last_seen: str


@dataclass
class DeviceRegistryEntry:
    """
    Entrée du registry pour un device (identifié par MAC)
    
    Contient TOUT l'historique du device depuis sa première détection
    """
    # Identification
    mac: str
    current_ip: Optional[str] = None
    current_hostname: Optional[str] = None
    
    # Informations enrichies
    vendor: Optional[str] = None
    os_detected: Optional[str] = None
    device_type: Optional[str] = None
    
    # Statut temps réel
    is_online: bool = False
    is_vpn_connected: bool = False
    vpn_ip: Optional[str] = None
    
    # Historique
    ip_history: List[Dict[str, Any]] = field(default_factory=list)
    hostname_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    last_seen_online: Optional[str] = None
    
    # Métriques
    total_detections: int = 0
    
    # Metadata
    notes: Optional[str] = None
    is_managed: bool = False  # Device géré dans l'onglet "Appareils"
    
    def to_dict(self) -> dict:
        """Convertir en dict pour JSON"""
        return asdict(self)


class NetworkRegistry:
    """
    Gestionnaire du registry réseau persistant
    
    Le registry est un fichier JSON unique qui stocke TOUS les devices
    jamais vus avec leur historique complet.
    """
    
    def __init__(self, registry_file: str = "data/network_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.devices: Dict[str, DeviceRegistryEntry] = {}
        self._load()
    
    def _load(self):
        """Charger le registry depuis le fichier"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    
                    # Reconstruire les DeviceRegistryEntry
                    for mac, device_data in data.get('devices', {}).items():
                        self.devices[mac.upper()] = DeviceRegistryEntry(**device_data)
                    
                    logger.info(f"✅ Network Registry chargé: {len(self.devices)} devices")
            else:
                logger.info("📝 Création d'un nouveau Network Registry")
                self._save()
        except Exception as e:
            logger.error(f"❌ Erreur chargement registry: {e}")
            self.devices = {}
    
    def _save(self):
        """Sauvegarder le registry sur disque"""
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'total_devices': len(self.devices),
                'devices': {mac: device.to_dict() for mac, device in self.devices.items()}
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Registry sauvegardé: {len(self.devices)} devices")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde registry: {e}")
    
    def update_from_scan(self, scan_devices: List[dict]) -> dict:
        """
        Enrichir le registry avec les résultats d'un scan
        
        Args:
            scan_devices: Liste de devices du scan (format UnifiedDevice)
            
        Returns:
            Dict avec statistiques: {new: int, updated: int, changes: List}
        """
        now = datetime.now().isoformat()
        stats = {
            'new': 0,
            'updated': 0,
            'changes': []
        }
        
        for device_dict in scan_devices:
            mac = device_dict.get('mac', '').upper()
            if not mac:
                continue
            
            # Device existant ou nouveau
            if mac in self.devices:
                # Mise à jour
                changes = self._update_existing_device(mac, device_dict, now)
                if changes:
                    stats['updated'] += 1
                    stats['changes'].extend(changes)
            else:
                # Nouveau device
                self._create_new_device(mac, device_dict, now)
                stats['new'] += 1
                stats['changes'].append({
                    'type': 'new_device',
                    'mac': mac,
                    'ip': device_dict.get('current_ip'),
                    'hostname': device_dict.get('current_hostname'),
                    'timestamp': now
                })
        
        # Marquer devices offline (présents dans registry mais pas dans le scan)
        scanned_macs = {d.get('mac', '').upper() for d in scan_devices if d.get('mac')}
        for mac, device in self.devices.items():
            if mac not in scanned_macs and device.is_online:
                device.is_online = False
                device.last_seen = now
                stats['changes'].append({
                    'type': 'device_offline',
                    'mac': mac,
                    'last_ip': device.current_ip,
                    'timestamp': now
                })
        
        self._save()
        logger.info(f"📊 Registry enrichi: {stats['new']} nouveaux, {stats['updated']} mis à jour")
        
        return stats
    
    def _create_new_device(self, mac: str, device_dict: dict, timestamp: str):
        """Créer une nouvelle entrée dans le registry"""
        ip = device_dict.get('current_ip')
        hostname = device_dict.get('current_hostname')
        
        entry = DeviceRegistryEntry(
            mac=mac,
            current_ip=ip,
            current_hostname=hostname,
            vendor=device_dict.get('vendor'),
            os_detected=device_dict.get('os_detected'),
            device_type=device_dict.get('device_type'),
            is_online=device_dict.get('is_online', True),
            is_vpn_connected=device_dict.get('is_vpn_connected', False),
            vpn_ip=device_dict.get('vpn_ip'),
            first_seen=timestamp,
            last_seen=timestamp,
            last_seen_online=timestamp if device_dict.get('is_online') else None,
            total_detections=1,
            ip_history=[{'ip': ip, 'first_seen': timestamp, 'last_seen': timestamp, 'occurrences': 1}] if ip else [],
            hostname_history=[{'hostname': hostname, 'first_seen': timestamp, 'last_seen': timestamp}] if hostname else []
        )
        
        self.devices[mac] = entry
        logger.info(f"✨ Nouveau device: {mac} ({hostname or ip or 'Unknown'})")
    
    def _update_existing_device(self, mac: str, device_dict: dict, timestamp: str) -> List[dict]:
        """Mettre à jour un device existant et tracker les changements"""
        device = self.devices[mac]
        changes = []
        
        # Mettre à jour timestamps
        device.last_seen = timestamp
        device.total_detections += 1
        
        new_ip = device_dict.get('current_ip')
        new_hostname = device_dict.get('current_hostname')
        
        # Vérifier changement d'IP (DHCP)
        if new_ip and new_ip != device.current_ip:
            changes.append({
                'type': 'ip_changed',
                'mac': mac,
                'old_ip': device.current_ip,
                'new_ip': new_ip,
                'timestamp': timestamp
            })
            
            # Mettre à jour historique IP
            existing_ip = next((h for h in device.ip_history if h['ip'] == new_ip), None)
            if existing_ip:
                existing_ip['last_seen'] = timestamp
                existing_ip['occurrences'] += 1
            else:
                device.ip_history.append({
                    'ip': new_ip,
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'occurrences': 1
                })
            
            device.current_ip = new_ip
            logger.info(f"🔄 IP changée: {mac} {device.current_ip} → {new_ip}")
        
        # Vérifier changement de hostname
        if new_hostname and new_hostname != device.current_hostname:
            changes.append({
                'type': 'hostname_changed',
                'mac': mac,
                'old_hostname': device.current_hostname,
                'new_hostname': new_hostname,
                'timestamp': timestamp
            })
            
            # Mettre à jour historique hostname
            existing_hostname = next((h for h in device.hostname_history if h['hostname'] == new_hostname), None)
            if existing_hostname:
                existing_hostname['last_seen'] = timestamp
            else:
                device.hostname_history.append({
                    'hostname': new_hostname,
                    'first_seen': timestamp,
                    'last_seen': timestamp
                })
            
            device.current_hostname = new_hostname
            logger.info(f"🔄 Hostname changé: {mac} {device.current_hostname} → {new_hostname}")
        
        # Mettre à jour statut online
        if device_dict.get('is_online') and not device.is_online:
            changes.append({
                'type': 'device_online',
                'mac': mac,
                'ip': device.current_ip,
                'timestamp': timestamp
            })
            device.last_seen_online = timestamp
        
        device.is_online = device_dict.get('is_online', False)
        device.is_vpn_connected = device_dict.get('is_vpn_connected', False)
        device.vpn_ip = device_dict.get('vpn_ip')
        
        # Enrichir vendor/OS si non définis
        if not device.vendor and device_dict.get('vendor'):
            device.vendor = device_dict['vendor']
        if not device.os_detected and device_dict.get('os_detected'):
            device.os_detected = device_dict['os_detected']
        if not device.device_type and device_dict.get('device_type'):
            device.device_type = device_dict['device_type']
        
        return changes
    
    def get_all_devices(self) -> List[dict]:
        """Récupérer tous les devices du registry"""
        return [device.to_dict() for device in self.devices.values()]
    
    def get_device(self, mac: str) -> Optional[dict]:
        """Récupérer un device spécifique"""
        device = self.devices.get(mac.upper())
        return device.to_dict() if device else None
    
    def get_recent_changes(self, limit: int = 50) -> List[dict]:
        """
        Récupérer les changements récents (triés par date)
        
        TODO: Implémenter un vrai système de changelog
        Pour l'instant, trier par last_seen
        """
        devices = sorted(
            self.devices.values(),
            key=lambda d: d.last_seen or '',
            reverse=True
        )
        return [d.to_dict() for d in devices[:limit]]
    
    def get_statistics(self) -> dict:
        """Statistiques globales du registry"""
        online_count = sum(1 for d in self.devices.values() if d.is_online)
        vpn_count = sum(1 for d in self.devices.values() if d.is_vpn_connected)
        managed_count = sum(1 for d in self.devices.values() if d.is_managed)
        
        # Devices avec historique IP multiple (DHCP changeant)
        dhcp_dynamic = sum(1 for d in self.devices.values() if len(d.ip_history) > 1)
        
        return {
            'total_devices': len(self.devices),
            'online': online_count,
            'offline': len(self.devices) - online_count,
            'vpn_connected': vpn_count,
            'managed': managed_count,
            'dhcp_dynamic': dhcp_dynamic,
            'last_updated': max((d.last_seen for d in self.devices.values()), default=None)
        }
    
    def mark_as_managed(self, mac: str, managed: bool = True):
        """Marquer un device comme géré (dans l'onglet Appareils)"""
        device = self.devices.get(mac.upper())
        if device:
            device.is_managed = managed
            self._save()
            logger.info(f"{'✅' if managed else '❌'} Device {'géré' if managed else 'non géré'}: {mac}")
