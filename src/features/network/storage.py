"""
🌐 333HOME - Network Storage
Gestion du stockage réseau avec format v3.0

Format v3.0:
- Versioning automatique
- Migration depuis anciens formats
- Backup automatique
- Structure normalisée
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import shutil

from .schemas import (
    NetworkDevice,
    ScanResult,
    IPHistoryEntry,
    NetworkEvent,
)
from .monitoring.dhcp_tracker import get_dhcp_tracker  # ✅ Déplacé dans monitoring/
from src.core.config import get_settings
from src.shared.exceptions import StorageError


logger = logging.getLogger(__name__)
settings = get_settings()


# === CONSTANTS ===

STORAGE_VERSION = "3.0"
NETWORK_STORAGE_FILE = settings.data_dir / "network_scan_history.json"
NETWORK_BACKUP_FILE = settings.data_dir / "network_scan_history.json.backup"


# === STORAGE V3.0 FORMAT ===

def _create_empty_storage() -> Dict[str, Any]:
    """Crée un storage vide au format v3.0"""
    return {
        "version": STORAGE_VERSION,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "metadata": {
            "total_scans": 0,
            "total_devices_seen": 0,
            "first_scan": None,
            "last_scan": None,
        },
        "devices": {},  # key: MAC address
        "scan_history": [],
    }


def _device_to_dict(device: NetworkDevice) -> Dict[str, Any]:
    """Convertit NetworkDevice en dict pour storage"""
    return {
        "id": device.id,
        "mac": device.mac,
        "current_ip": device.current_ip,
        "current_hostname": device.current_hostname,
        "vendor": device.vendor,
        "device_type": device.device_type,
        "os_detected": device.os_detected,
        "first_seen": device.first_seen.isoformat(),
        "last_seen": device.last_seen.isoformat(),
        "total_appearances": device.total_appearances,
        "currently_online": device.currently_online,
        "in_devices": device.in_devices,
        "tags": device.tags,
        "ip_history": [],  # Géré par NetworkHistory
    }


def _dict_to_device(data: Dict[str, Any]) -> NetworkDevice:
    """Convertit dict en NetworkDevice"""
    return NetworkDevice(
        id=data["id"],
        mac=data["mac"],
        current_ip=data["current_ip"],
        current_hostname=data.get("current_hostname"),
        vendor=data.get("vendor"),
        device_type=data.get("device_type"),
        os_detected=data.get("os_detected"),
        first_seen=datetime.fromisoformat(data["first_seen"]),
        last_seen=datetime.fromisoformat(data["last_seen"]),
        total_appearances=data.get("total_appearances", 1),
        currently_online=data.get("currently_online", False),
        in_devices=data.get("in_devices", False),
        tags=data.get("tags", []),
    )


def _scan_to_dict(scan: ScanResult) -> Dict[str, Any]:
    """Convertit ScanResult en dict pour storage"""
    return {
        "scan_id": scan.scan_id,
        "timestamp": scan.timestamp.isoformat(),
        "duration_ms": scan.duration_ms,
        "scan_type": scan.scan_type.value,
        "subnet": scan.subnet,
        "devices_found": scan.devices_found,
        "new_devices": scan.new_devices,
        "device_macs": [d.mac for d in scan.devices],
    }


# === MIGRATION ===

def _migrate_from_old_format(old_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migre depuis ancien format vers v3.0
    
    Formats supportés:
    - Format v2.x (modules/network)
    - Format legacy (data/network_history.json)
    """
    logger.info("🔄 Migrating network storage to v3.0...")
    
    new_storage = _create_empty_storage()
    migrated_count = 0
    
    # Détection format v2.x
    if "devices" in old_data and isinstance(old_data.get("devices"), list):
        logger.info("📦 Detected v2.x format")
        
        for old_device in old_data["devices"]:
            mac = old_device.get("mac_address") or old_device.get("mac")
            if not mac:
                continue
            
            # Crée device v3.0
            device_data = {
                "id": f"dev_network_{mac.replace(':', '')}",
                "mac": mac,
                "current_ip": old_device.get("ip_address") or old_device.get("ip", ""),
                "current_hostname": old_device.get("hostname"),
                "vendor": old_device.get("vendor") or old_device.get("vendor_info", {}).get("vendor"),
                "device_type": old_device.get("device_type"),
                "os_detected": old_device.get("os_detected"),
                "first_seen": old_device.get("first_seen", datetime.now().isoformat()),
                "last_seen": old_device.get("last_seen", datetime.now().isoformat()),
                "total_appearances": old_device.get("total_appearances", 1),
                "currently_online": old_device.get("status") == "online",
                "in_devices": False,
                "tags": old_device.get("tags", []),
                "ip_history": [],
            }
            
            new_storage["devices"][mac] = device_data
            migrated_count += 1
    
    # Format legacy
    elif "scan_history" in old_data:
        logger.info("📦 Detected legacy format")
        
        for scan in old_data.get("scan_history", []):
            for device in scan.get("devices", []):
                mac = device.get("mac_address") or device.get("mac")
                if not mac or mac in new_storage["devices"]:
                    continue
                
                device_data = {
                    "id": f"dev_network_{mac.replace(':', '')}",
                    "mac": mac,
                    "current_ip": device.get("ip", ""),
                    "current_hostname": device.get("hostname"),
                    "vendor": device.get("vendor"),
                    "device_type": None,
                    "os_detected": None,
                    "first_seen": scan.get("timestamp", datetime.now().isoformat()),
                    "last_seen": scan.get("timestamp", datetime.now().isoformat()),
                    "total_appearances": 1,
                    "currently_online": False,
                    "in_devices": False,
                    "tags": [],
                    "ip_history": [],
                }
                
                new_storage["devices"][mac] = device_data
                migrated_count += 1
    
    # Mise à jour metadata
    new_storage["metadata"]["total_devices_seen"] = migrated_count
    
    logger.info(f"✅ Migration complete: {migrated_count} devices migrated")
    return new_storage


# === LOAD / SAVE ===

def load_network_storage() -> Dict[str, Any]:
    """
    Charge le storage réseau
    
    Returns:
        Dict au format v3.0
    """
    if not NETWORK_STORAGE_FILE.exists():
        logger.info("📝 Creating new network storage v3.0")
        return _create_empty_storage()
    
    try:
        with open(NETWORK_STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérification version
        version = data.get("version")
        
        if version == STORAGE_VERSION:
            logger.debug("✅ Network storage v3.0 loaded")
            return data
        
        # Migration nécessaire
        logger.warning(f"⚠️  Old format detected (version: {version or 'unknown'})")
        
        # Backup avant migration
        if NETWORK_STORAGE_FILE.exists():
            shutil.copy2(NETWORK_STORAGE_FILE, NETWORK_BACKUP_FILE)
            logger.info(f"💾 Backup created: {NETWORK_BACKUP_FILE.name}")
        
        # Migration
        migrated_data = _migrate_from_old_format(data)
        
        # Sauvegarde
        save_network_storage(migrated_data)
        
        return migrated_data
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {NETWORK_STORAGE_FILE.name}: {e}")
        raise StorageError(f"Invalid network storage file: {e}")
    
    except Exception as e:
        logger.error(f"❌ Error loading network storage: {e}")
        raise StorageError(f"Failed to load network storage: {e}")


def save_network_storage(storage: Dict[str, Any]) -> None:
    """
    Sauvegarde le storage réseau
    
    Args:
        storage: Dict au format v3.0
    """
    try:
        # Mise à jour timestamp
        storage["last_updated"] = datetime.now().isoformat()
        
        # Écriture atomique
        temp_file = NETWORK_STORAGE_FILE.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(storage, f, indent=2, ensure_ascii=False)
        
        # Renommage atomique
        temp_file.replace(NETWORK_STORAGE_FILE)
        
        logger.debug(f"💾 Network storage saved: {len(storage['devices'])} devices")
    
    except Exception as e:
        logger.error(f"❌ Error saving network storage: {e}")
        raise StorageError(f"Failed to save network storage: {e}")


# === OPERATIONS ===

def save_scan_result(scan: ScanResult) -> None:
    """
    Sauvegarde un résultat de scan
    
    Args:
        scan: Résultat du scan
    """
    storage = load_network_storage()
    
    # Mise à jour/ajout des devices
    dhcp_tracker = get_dhcp_tracker()
    
    for device in scan.devices:
        mac = device.mac
        
        if mac in storage["devices"]:
            # Device existant - mise à jour
            existing = storage["devices"][mac]
            
            # Track IP change in DHCP tracker
            if existing["current_ip"] != device.current_ip:
                dhcp_tracker.track_ip_change(
                    mac=mac,
                    ip=device.current_ip,
                    hostname=device.current_hostname
                )
            
            existing["last_seen"] = device.last_seen.isoformat()
            existing["current_ip"] = device.current_ip
            existing["current_hostname"] = device.current_hostname
            existing["total_appearances"] += 1
            existing["currently_online"] = True
            
            # Mise à jour vendor/type si meilleur
            if device.vendor and device.vendor != "Unknown":
                existing["vendor"] = device.vendor
            if device.device_type:
                existing["device_type"] = device.device_type
            if device.os_detected:
                existing["os_detected"] = device.os_detected
        else:
            # Nouveau device
            storage["devices"][mac] = _device_to_dict(device)
            
            # Track new device in DHCP tracker
            dhcp_tracker.track_ip_change(
                mac=mac,
                ip=device.current_ip,
                hostname=device.current_hostname
            )
    
    # Marquer les devices offline
    scan_macs = {d.mac for d in scan.devices}
    for mac, device_data in storage["devices"].items():
        if mac not in scan_macs:
            device_data["currently_online"] = False
    
    # Ajouter à l'historique
    storage["scan_history"].append(_scan_to_dict(scan))
    
    # Limiter l'historique (garder 100 derniers scans)
    if len(storage["scan_history"]) > 100:
        storage["scan_history"] = storage["scan_history"][-100:]
    
    # Mise à jour metadata
    storage["metadata"]["total_scans"] = len(storage["scan_history"])
    storage["metadata"]["total_devices_seen"] = len(storage["devices"])
    storage["metadata"]["last_scan"] = scan.timestamp.isoformat()
    
    if not storage["metadata"]["first_scan"]:
        storage["metadata"]["first_scan"] = scan.timestamp.isoformat()
    
    # Sauvegarde
    save_network_storage(storage)
    
    logger.info(
        f"💾 Scan saved: {scan.devices_found} devices, "
        f"{scan.new_devices} new"
    )


def get_all_devices() -> List[NetworkDevice]:
    """Récupère tous les devices"""
    storage = load_network_storage()
    
    devices = []
    for device_data in storage["devices"].values():
        try:
            devices.append(_dict_to_device(device_data))
        except Exception as e:
            logger.warning(f"⚠️  Skipping invalid device: {e}")
    
    return devices


def get_device_by_mac(mac: str) -> Optional[NetworkDevice]:
    """Récupère un device par MAC"""
    storage = load_network_storage()
    
    device_data = storage["devices"].get(mac)
    if device_data:
        return _dict_to_device(device_data)
    
    return None


def update_device_in_devices_flag(mac: str, in_devices: bool) -> None:
    """Met à jour le flag in_devices"""
    storage = load_network_storage()
    
    if mac in storage["devices"]:
        storage["devices"][mac]["in_devices"] = in_devices
        save_network_storage(storage)
        logger.info(f"✅ Device {mac} marked as in_devices={in_devices}")
    else:
        logger.warning(f"⚠️  Device {mac} not found")


def get_scan_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Récupère l'historique des scans"""
    storage = load_network_storage()
    
    history = storage["scan_history"][-limit:]
    history.reverse()  # Plus récent en premier
    
    return history
