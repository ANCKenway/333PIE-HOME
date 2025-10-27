"""
🌐 333HOME - Network Schemas
Modèles Pydantic pour la feature Network

Format moderne pour monitoring réseau complet
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# Import depuis source unique (RÈGLE #1)
from src.shared.constants import DeviceStatus


# === ENUMS ===

class ScanType(str, Enum):
    """
    Type de scan réseau
    
    Phase 6: Simplifié à FULL uniquement (RULES.MD: pas de versions multiples)
    Quick/MDNS/ARP = subsets redondants → Supprimés
    """
    FULL = "full"  # Multi-source complet: nmap + ARP + mDNS + NetBIOS + Tailscale


class NetworkEventType(str, Enum):
    """Types d'événements réseau"""
    DEVICE_APPEARED = "device_appeared"
    DEVICE_DISAPPEARED = "device_disappeared"
    IP_CHANGED = "ip_changed"
    MAC_CHANGED = "mac_changed"
    HOSTNAME_CHANGED = "hostname_changed"
    DEVICE_PROMOTED = "device_promoted"


# === NETWORK DEVICE ===

class ServiceInfo(BaseModel):
    """Information sur un service réseau"""
    port: int = Field(..., description="Numéro de port")
    service: str = Field(..., description="Nom du service")
    name: str = Field(..., description="Description")
    icon: str = Field("❓", description="Icône du service")
    banner: Optional[str] = Field(None, description="Banner du service")
    
    class Config:
        from_attributes = True


class NetworkDeviceBase(BaseModel):
    """Modèle de base pour un appareil réseau"""
    mac: str = Field(..., description="Adresse MAC (identifiant unique)")
    current_ip: str = Field(..., description="Adresse IP actuelle")
    current_hostname: Optional[str] = Field(None, description="Hostname actuel")
    vendor: Optional[str] = Field(None, description="Fabricant (via MAC OUI)")
    device_type: Optional[str] = Field(None, description="Type d'appareil")
    os_detected: Optional[str] = Field(None, description="OS détecté")
    device_role: Optional[str] = Field(None, description="Rôle (web_server, router, etc.)")
    
    # VPN (Tailscale)
    is_vpn_connected: bool = Field(False, description="Connecté au VPN Tailscale")
    vpn_ip: Optional[str] = Field(None, description="Adresse IP VPN (100.x.x.x)")
    vpn_hostname: Optional[str] = Field(None, description="Hostname VPN complet")


class NetworkDeviceCreate(NetworkDeviceBase):
    """Modèle pour créer un appareil réseau"""
    pass


class NetworkDevice(NetworkDeviceBase):
    """Modèle complet d'un appareil réseau"""
    id: str = Field(..., description="ID unique (dev_network_xxx)")
    first_seen: datetime = Field(..., description="Première fois vu")
    last_seen: datetime = Field(..., description="Dernière fois vu")
    total_appearances: int = Field(0, description="Nombre d'apparitions")
    currently_online: bool = Field(False, description="Actuellement en ligne")
    in_devices: bool = Field(False, description="Dans la liste Devices favoris")
    tags: List[str] = Field(default_factory=list, description="Tags")
    services: List[ServiceInfo] = Field(default_factory=list, description="Services détectés")
    
    # Status simple (basé sur scans ON-DEMAND)
    last_seen_relative: Optional[str] = Field(None, description="Dernière détection relative (Il y a X)")
    scan_status: Optional[str] = Field(None, description="Status du dernier scan")
    
    class Config:
        from_attributes = True


class NetworkDeviceDetailed(NetworkDevice):
    """Appareil réseau avec historique IP"""
    ip_history: List['IPHistoryEntry'] = Field(default_factory=list)


# === IP HISTORY ===

class IPHistoryEntry(BaseModel):
    """Entrée d'historique IP"""
    ip: str = Field(..., description="Adresse IP")
    first_seen: datetime = Field(..., description="Première fois avec cette IP")
    last_seen: datetime = Field(..., description="Dernière fois avec cette IP")
    duration_days: int = Field(0, description="Durée en jours")
    
    class Config:
        from_attributes = True


# === SCAN RESULT ===

class ScanRequest(BaseModel):
    """Requête de scan réseau"""
    scan_type: ScanType = Field(ScanType.FULL, description="Type de scan")
    subnet: str = Field("192.168.1.0/24", description="Sous-réseau à scanner")
    timeout_ms: int = Field(2000, ge=500, le=10000, description="Timeout en ms")
    scan_ports: bool = Field(True, description="Scanner les ports")
    port_preset: str = Field("quick", description="Preset de ports (quick, common, web, etc.)")


class ScanResult(BaseModel):
    """Résultat d'un scan réseau"""
    scan_id: str = Field(..., description="ID unique du scan")
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: int = Field(..., description="Durée du scan en ms")
    scan_type: ScanType = Field(..., description="Type de scan effectué")
    subnet: str = Field(..., description="Sous-réseau scanné")
    devices_found: int = Field(..., description="Nombre d'appareils trouvés")
    new_devices: int = Field(0, description="Nouveaux appareils")
    devices: List[NetworkDevice] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# === NETWORK EVENT ===

class NetworkEvent(BaseModel):
    """Événement réseau"""
    event_id: str = Field(..., description="ID unique de l'événement")
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: NetworkEventType = Field(..., description="Type d'événement")
    device_mac: str = Field(..., description="MAC de l'appareil concerné")
    device_name: Optional[str] = Field(None, description="Nom de l'appareil")
    details: Dict[str, Any] = Field(default_factory=dict, description="Détails de l'événement")
    
    class Config:
        from_attributes = True


class NetworkEventDetailed(NetworkEvent):
    """Événement réseau avec infos appareil"""
    device: Optional[NetworkDevice] = None


# === TIMELINE ===

class NetworkTimeline(BaseModel):
    """Timeline des événements réseau"""
    total_events: int = Field(..., description="Nombre total d'événements")
    events: List[NetworkEvent] = Field(..., description="Liste des événements")
    period_start: Optional[datetime] = Field(None, description="Début de période")
    period_end: Optional[datetime] = Field(None, description="Fin de période")


# === STATISTICS ===

class DeviceStatistics(BaseModel):
    """Statistiques d'un appareil"""
    mac: str
    name: Optional[str]
    total_appearances: int
    uptime_percentage: float
    average_connection_duration_hours: float
    last_ip: str
    last_seen: datetime


class NetworkStats(BaseModel):
    """Statistiques réseau globales"""
    total_devices_seen: int = Field(..., description="Total appareils vus")
    currently_online: int = Field(..., description="Actuellement en ligne")
    currently_offline: int = Field(..., description="Actuellement hors ligne")
    average_devices_online: float = Field(..., description="Moyenne appareils online")
    new_devices_last_24h: int = Field(0, description="Nouveaux dernières 24h")
    ip_changes_last_24h: int = Field(0, description="Changements IP dernières 24h")
    most_stable_device: Optional[DeviceStatistics] = None
    most_active_device: Optional[DeviceStatistics] = None
    last_scan: Optional[datetime] = None


# === DEVICE HISTORY ===

class OnlinePeriod(BaseModel):
    """Période de connexion"""
    start: datetime
    end: Optional[datetime] = None
    duration_hours: Optional[float] = None


class DeviceHistory(BaseModel):
    """Historique complet d'un appareil"""
    mac: str
    device_name: Optional[str]
    first_seen: datetime
    last_seen: datetime
    total_appearances: int
    ip_history: List[IPHistoryEntry]
    events: List[NetworkEvent]
    online_periods: List[OnlinePeriod]
    statistics: DeviceStatistics


# === PROMOTE TO DEVICES ===

class PromoteToDevicesRequest(BaseModel):
    """Requête pour promouvoir un appareil vers Devices"""
    name: Optional[str] = Field(None, description="Nom personnalisé")
    description: Optional[str] = Field(None, description="Description")
    tags: List[str] = Field(default_factory=list, description="Tags")
    type: Optional[str] = Field(None, description="Type d'appareil")


class PromoteToDevicesResponse(BaseModel):
    """Réponse après promotion"""
    success: bool
    message: str
    device_id: Optional[str] = None
    network_device_id: str
    device_name: str


# === REGISTRY RESPONSES (Phase 6 - Étape 2) ===

class DeviceRegistryResponse(BaseModel):
    """Réponse du registry avec tous les devices"""
    total: int = Field(..., description="Nombre total de devices")
    devices: List[Dict[str, Any]] = Field(..., description="Liste des devices du registry")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Filtres appliqués")


class RegistryStatistics(BaseModel):
    """Statistiques du registry"""
    total_devices: int = Field(..., description="Total devices dans le registry")
    online: int = Field(..., description="Devices online")
    offline: int = Field(..., description="Devices offline")
    vpn_connected: int = Field(0, description="Devices VPN connectés")
    managed: int = Field(0, description="Devices gérés (in Appareils)")
    dhcp_dynamic: int = Field(0, description="Devices avec IP history multiple (DHCP)")
    last_updated: Optional[str] = Field(None, description="Dernière mise à jour du registry")


# Update forward refs
NetworkDeviceDetailed.model_rebuild()
