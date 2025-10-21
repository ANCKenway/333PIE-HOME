"""
📋 333HOME - Device Storage Schema
Schéma de stockage moderne pour les appareils

Format JSON optimisé pour performance et évolutivité
"""

from typing import TypedDict, Optional, List
from datetime import datetime


# === FORMAT DE STOCKAGE MODERNE ===

class DeviceStorage(TypedDict, total=False):
    """
    Format de stockage d'un appareil (version 3.0)
    
    Champs obligatoires:
    - id: Identifiant unique (généré automatiquement)
    - name: Nom de l'appareil
    - ip: Adresse IP principale
    
    Champs optionnels:
    - mac: Adresse MAC
    - hostname: Nom d'hôte
    - type: Type d'appareil (pc, serveur, iot, etc.)
    - description: Description libre
    - tags: Tags pour catégorisation
    - metadata: Métadonnées additionnelles
    - created_at: Date de création (ISO 8601)
    - updated_at: Date de dernière modification (ISO 8601)
    """
    # === IDENTIFIANTS ===
    id: str
    name: str
    
    # === RÉSEAU ===
    ip: str
    mac: Optional[str]
    hostname: Optional[str]
    
    # === CLASSIFICATION ===
    type: str  # pc, serveur, iot, mobile, imprimante, etc.
    description: Optional[str]
    tags: List[str]  # ["bureau", "linux", "production", etc.]
    
    # === MÉTADONNÉES ===
    metadata: dict  # Données extensibles (OS, vendor, etc.)
    
    # === HORODATAGE ===
    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601


# === EXEMPLE DE FICHIER devices.json (v3.0) ===
EXAMPLE_DEVICES_JSON = {
    "version": "3.0",
    "updated_at": "2025-10-19T17:00:00Z",
    "devices": [
        {
            "id": "dev_rpi_d83add123456",
            "name": "Raspberry Pi 5",
            "ip": "192.168.1.150",
            "mac": "d8:3a:dd:12:34:56",
            "hostname": "raspberrypi.local",
            "type": "serveur",
            "description": "Serveur domotique principal",
            "tags": ["production", "linux", "arm64"],
            "metadata": {
                "os": "Raspberry Pi OS",
                "vendor": "Raspberry Pi Foundation",
                "model": "Raspberry Pi 5",
                "wol_enabled": False
            },
            "created_at": "2025-10-19T10:00:00Z",
            "updated_at": "2025-10-19T17:00:00Z"
        },
        {
            "id": "dev_pc_asus_107c61787",
            "name": "PC Bureau ASUS",
            "ip": "192.168.1.24",
            "mac": "10:7c:61:78:72:8b",
            "hostname": "CLACLA",
            "type": "pc",
            "description": "PC Windows principal",
            "tags": ["bureau", "windows", "gaming"],
            "metadata": {
                "os": "Windows 11",
                "vendor": "ASUSTek COMPUTER INC.",
                "wol_enabled": True
            },
            "created_at": "2025-10-19T10:00:00Z",
            "updated_at": "2025-10-19T17:00:00Z"
        }
    ]
}


# === MIGRATION DE L'ANCIEN FORMAT ===

def migrate_old_device_format(old_device: dict) -> DeviceStorage:
    """
    Migrer un appareil de l'ancien format vers le nouveau
    
    Ancien format: Structure plate avec champs variés
    Nouveau format: Structure organisée avec metadata
    """
    now = datetime.now().isoformat()
    
    # Générer ID si absent
    device_id = old_device.get('id')
    if not device_id:
        mac = old_device.get('mac', '')
        ip = old_device.get('ip', '')
        device_id = f"dev_{mac.replace(':', '').lower()[:12] if mac else ip.replace('.', '_')}"
    
    # Extraire les champs de base
    new_device: DeviceStorage = {
        'id': device_id,
        'name': old_device.get('name', 'Appareil inconnu'),
        'ip': old_device.get('ip', '0.0.0.0'),
        'mac': old_device.get('mac'),
        'hostname': old_device.get('hostname'),
        'type': old_device.get('type', 'other'),
        'description': old_device.get('description', ''),
        'tags': [],
        'metadata': {},
        'created_at': old_device.get('created_at', now),
        'updated_at': now
    }
    
    # Migrer les métadonnées
    metadata = {}
    
    # Champs à migrer vers metadata
    metadata_fields = [
        'vendor', 'os_detected', 'device_type', 'wake_on_lan',
        'is_vpn', 'vpn_ip', 'ip_secondary', 'status', 'online',
        'last_seen', 'scan_timestamp', 'added_from_scan'
    ]
    
    for field in metadata_fields:
        if field in old_device:
            metadata[field] = old_device[field]
    
    # Migrer les infos VPN
    if 'vpn' in old_device:
        metadata['vpn'] = old_device['vpn']
    
    new_device['metadata'] = metadata
    
    # Générer des tags intelligents
    tags = []
    if metadata.get('os_detected'):
        os_name = metadata['os_detected'].lower()
        if 'windows' in os_name:
            tags.append('windows')
        elif 'linux' in os_name:
            tags.append('linux')
        elif 'mac' in os_name:
            tags.append('macos')
    
    if metadata.get('is_vpn'):
        tags.append('vpn')
    
    if old_device.get('type'):
        tags.append(old_device['type'].lower())
    
    new_device['tags'] = list(set(tags))  # Dédupliquer
    
    return new_device
