"""
🏠 333HOME - Unified Device Model

Modèle unifié pour représenter un device réseau avec toutes ses données.
Source unique de vérité fusionnant multiples sources (nmap, ARP, Freebox, mDNS).

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 1.3
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


# === ENUMS ===

class DeviceStatus(Enum):
    """Statut d'un device"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class InterfaceType(Enum):
    """Type d'interface réseau"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    VPN = "vpn"
    UNKNOWN = "unknown"


# === DATA CLASSES ===

@dataclass
class IPChange:
    """
    Historique d'un changement d'IP
    """
    old_ip: Optional[str]
    new_ip: str
    changed_at: datetime
    detected_by: str                # Source qui a détecté (nmap, freebox, etc.)
    reason: Optional[str] = None    # Raison si connue (dhcp_renew, manual, etc.)
    dhcp_lease_time: Optional[int] = None  # Durée du bail DHCP (secondes)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'old_ip': self.old_ip,
            'new_ip': self.new_ip,
            'changed_at': self.changed_at.isoformat(),
            'detected_by': self.detected_by,
            'reason': self.reason,
            'dhcp_lease_time': self.dhcp_lease_time,
        }


@dataclass
class HostnameChange:
    """
    Historique d'un changement de hostname
    """
    old_hostname: Optional[str]
    new_hostname: str
    changed_at: datetime
    detected_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'old_hostname': self.old_hostname,
            'new_hostname': self.new_hostname,
            'changed_at': self.changed_at.isoformat(),
            'detected_by': self.detected_by,
        }


@dataclass
class OnlinePeriod:
    """
    Période où le device était en ligne
    """
    online_from: datetime
    online_until: Optional[datetime] = None  # None = encore en ligne
    duration_seconds: int = 0
    detections_count: int = 0  # Nombre de scans détectés pendant cette période
    
    def __post_init__(self):
        if self.online_until and self.duration_seconds == 0:
            self.duration_seconds = int((self.online_until - self.online_from).total_seconds())
    
    @property
    def is_active(self) -> bool:
        """Le device est-il encore en ligne ?"""
        return self.online_until is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'online_from': self.online_from.isoformat(),
            'online_until': self.online_until.isoformat() if self.online_until else None,
            'duration_seconds': self.duration_seconds,
            'detections_count': self.detections_count,
            'is_active': self.is_active,
        }


@dataclass
class DeviceCapabilities:
    """
    Capacités détectées d'un device
    """
    open_ports: List[int] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    supports_wake_on_lan: bool = False
    supports_snmp: bool = False
    has_web_interface: bool = False
    detected_os: Optional[str] = None
    os_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'open_ports': self.open_ports,
            'services': self.services,
            'supports_wake_on_lan': self.supports_wake_on_lan,
            'supports_snmp': self.supports_snmp,
            'has_web_interface': self.has_web_interface,
            'detected_os': self.detected_os,
            'os_confidence': self.os_confidence,
        }


@dataclass
class UnifiedDevice:
    """
    Modèle unifié d'un device réseau
    
    Single source of truth fusionnant données de multiples sources.
    MAC address = clé primaire (unique, stable).
    """
    
    # === IDENTIFIANTS (MAC = clé primaire) ===
    mac: str                        # Adresse MAC (unique, stable)
    id: str                         # ID format: dev_{mac_clean}
    
    # === IDENTITÉ ===
    name: str = "Unknown"           # Nom custom ou hostname
    hostname: Optional[str] = None  # Hostname réseau
    vendor: Optional[str] = None    # Constructeur (OUI lookup)
    device_type: Optional[str] = None  # Type détecté
    
    # === RÉSEAU ACTUEL ===
    current_ip: Optional[str] = None
    subnet: str = "192.168.1.0/24"
    interface_type: InterfaceType = InterfaceType.UNKNOWN
    
    # === VPN (Tailscale) ===
    is_vpn_connected: bool = False
    vpn_ip: Optional[str] = None
    vpn_hostname: Optional[str] = None
    
    # === STATUT ===
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    
    # === HISTORIQUE ===
    ip_history: List[IPChange] = field(default_factory=list)
    hostname_history: List[HostnameChange] = field(default_factory=list)
    uptime_periods: List[OnlinePeriod] = field(default_factory=list)
    
    # === STATISTIQUES ===
    total_scans_detected: int = 0
    uptime_percentage: float = 0.0
    average_latency_ms: float = 0.0
    total_uptime_seconds: int = 0
    
    # === CAPACITÉS ===
    capabilities: DeviceCapabilities = field(default_factory=DeviceCapabilities)
    
    # === SOURCES DE DONNÉES ===
    sources: List[str] = field(default_factory=list)  # [nmap, arp, freebox, mdns]
    confidence_score: float = 0.0   # Score de fiabilité (0-1)
    data_quality: str = "low"       # high | medium | low
    last_updated: Optional[datetime] = None
    
    # === GESTION ===
    is_managed: bool = False        # Dans devices.json ?
    is_monitored: bool = False      # Monitoring actif ?
    is_whitelisted: bool = True     # Device autorisé ?
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    # === ALERTES ===
    has_active_alerts: bool = False
    alert_count: int = 0
    last_alert: Optional[datetime] = None
    
    # === FREEBOX SPECIFIC ===
    freebox_data: Optional[Dict[str, Any]] = None
    
    @property
    def is_online(self) -> bool:
        """Raccourci pour vérifier si le device est en ligne"""
        return self.status == DeviceStatus.ONLINE
    
    @property
    def last_seen_relative(self) -> str:
        """Affichage relatif de la dernière détection"""
        if not self.last_seen:
            return "Jamais vu"
        
        now = datetime.now()
        delta = now - self.last_seen
        
        if delta.total_seconds() < 60:
            return "À l'instant"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"Il y a {minutes} min"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"Il y a {hours}h"
        elif delta.days == 1:
            return "Hier"
        elif delta.days < 7:
            return f"Il y a {delta.days} jours"
        else:
            return f"Le {self.last_seen.strftime('%d/%m/%Y')}"
    
    @property
    def scan_status(self) -> str:
        """Status simple basé sur le dernier scan"""
        if self.is_online:
            return f"✅ Détecté - {self.last_seen_relative}"
        else:
            return f"⚠️ Absent - {self.last_seen_relative}"
    
    @property
    def mac_clean(self) -> str:
        """MAC address sans séparateurs (pour ID)"""
        return self.mac.replace(':', '').replace('-', '').lower()
    
    @property
    def display_name(self) -> str:
        """Nom à afficher (priorité: name > hostname > vendor > MAC)"""
        if self.name and self.name != "Unknown":
            return self.name
        if self.hostname:
            return self.hostname
        if self.vendor and self.vendor != "Unknown":
            return self.vendor
        return self.mac
    
    def add_ip_change(self, new_ip: str, detected_by: str, reason: Optional[str] = None):
        """Ajouter un changement d'IP à l'historique"""
        change = IPChange(
            old_ip=self.current_ip,
            new_ip=new_ip,
            changed_at=datetime.now(),
            detected_by=detected_by,
            reason=reason
        )
        self.ip_history.append(change)
        self.current_ip = new_ip
    
    def add_hostname_change(self, new_hostname: str, detected_by: str):
        """Ajouter un changement de hostname à l'historique"""
        change = HostnameChange(
            old_hostname=self.hostname,
            new_hostname=new_hostname,
            changed_at=datetime.now(),
            detected_by=detected_by
        )
        self.hostname_history.append(change)
        self.hostname = new_hostname
    
    def start_online_period(self):
        """Démarrer une nouvelle période en ligne"""
        # Terminer la période précédente si active
        if self.uptime_periods and self.uptime_periods[-1].is_active:
            self.uptime_periods[-1].online_until = datetime.now()
            self.uptime_periods[-1].duration_seconds = int(
                (self.uptime_periods[-1].online_until - self.uptime_periods[-1].online_from).total_seconds()
            )
        
        # Créer nouvelle période
        period = OnlinePeriod(
            online_from=datetime.now(),
            online_until=None,
            detections_count=1
        )
        self.uptime_periods.append(period)
        self.status = DeviceStatus.ONLINE
    
    def mark_offline(self):
        """Marquer le device comme hors ligne"""
        self.status = DeviceStatus.OFFLINE
        
        # Terminer la période en ligne actuelle
        if self.uptime_periods and self.uptime_periods[-1].is_active:
            self.uptime_periods[-1].online_until = datetime.now()
            self.uptime_periods[-1].duration_seconds = int(
                (self.uptime_periods[-1].online_until - self.uptime_periods[-1].online_from).total_seconds()
            )
    
    def increment_detection(self):
        """Incrémenter le compteur de détections (lors d'un scan)"""
        self.total_scans_detected += 1
        self.last_seen = datetime.now()
        
        # Incrémenter la période en ligne actuelle
        if self.uptime_periods and self.uptime_periods[-1].is_active:
            self.uptime_periods[-1].detections_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour API/Storage"""
        return {
            # Identifiants
            'id': self.id,
            'mac': self.mac,
            
            # Identité
            'name': self.name,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'device_type': self.device_type,
            
            # Réseau
            'current_ip': self.current_ip,
            'ip': self.current_ip,  # Alias pour compatibilité
            'subnet': self.subnet,
            'interface_type': self.interface_type.value,
            
            # Statut
            'status': self.status.value,
            'online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen_relative': self.last_seen_relative,
            'scan_status': self.scan_status,
            
            # Historique
            'ip_history': [change.to_dict() for change in self.ip_history],
            'hostname_history': [change.to_dict() for change in self.hostname_history],
            'uptime_periods': [period.to_dict() for period in self.uptime_periods],
            
            # Statistiques
            'total_scans_detected': self.total_scans_detected,
            'uptime_percentage': self.uptime_percentage,
            'average_latency_ms': self.average_latency_ms,
            'total_uptime_seconds': self.total_uptime_seconds,
            
            # Capacités
            'capabilities': self.capabilities.to_dict(),
            'open_ports': self.capabilities.open_ports,  # Alias
            'services': self.capabilities.services,      # Alias
            
            # Sources
            'sources': self.sources,
            'confidence_score': self.confidence_score,
            'data_quality': self.data_quality,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            
            # Gestion
            'is_managed': self.is_managed,
            'in_devices': self.is_managed,  # Alias pour compatibilité
            'is_monitored': self.is_monitored,
            'is_whitelisted': self.is_whitelisted,
            'tags': self.tags,
            'notes': self.notes,
            
            # Alertes
            'has_active_alerts': self.has_active_alerts,
            'alert_count': self.alert_count,
            'last_alert': self.last_alert.isoformat() if self.last_alert else None,
            
            # Freebox
            'freebox_data': self.freebox_data,
            
            # Helpers
            'display_name': self.display_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedDevice':
        """Créer depuis un dictionnaire"""
        # Parse dates
        last_seen = None
        if data.get('last_seen'):
            try:
                last_seen = datetime.fromisoformat(data['last_seen'])
            except:
                pass
        
        first_seen = None
        if data.get('first_seen'):
            try:
                first_seen = datetime.fromisoformat(data['first_seen'])
            except:
                pass
        
        last_updated = None
        if data.get('last_updated'):
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
            except:
                pass
        
        # Parse status
        status = DeviceStatus.UNKNOWN
        if data.get('status'):
            try:
                status = DeviceStatus(data['status'])
            except:
                pass
        
        # Parse interface type
        interface_type = InterfaceType.UNKNOWN
        if data.get('interface_type'):
            try:
                interface_type = InterfaceType(data['interface_type'])
            except:
                pass
        
        # Parse capabilities
        capabilities = DeviceCapabilities(
            open_ports=data.get('open_ports', []),
            services=data.get('services', []),
            supports_wake_on_lan=data.get('capabilities', {}).get('supports_wake_on_lan', False),
            detected_os=data.get('capabilities', {}).get('detected_os'),
            os_confidence=data.get('capabilities', {}).get('os_confidence', 0.0),
        )
        
        # Parse historique
        ip_history = []
        for change_data in data.get('ip_history', []):
            try:
                ip_history.append(IPChange(
                    old_ip=change_data.get('old_ip'),
                    new_ip=change_data['new_ip'],
                    changed_at=datetime.fromisoformat(change_data['changed_at']),
                    detected_by=change_data['detected_by'],
                    reason=change_data.get('reason'),
                ))
            except:
                pass
        
        return cls(
            mac=data['mac'],
            id=data.get('id', f"dev_{data['mac'].replace(':', '').lower()}"),
            name=data.get('name', 'Unknown'),
            hostname=data.get('hostname'),
            vendor=data.get('vendor'),
            device_type=data.get('device_type'),
            current_ip=data.get('current_ip') or data.get('ip'),
            subnet=data.get('subnet', '192.168.1.0/24'),
            interface_type=interface_type,
            status=status,
            last_seen=last_seen,
            first_seen=first_seen,
            ip_history=ip_history,
            total_scans_detected=data.get('total_scans_detected', 0),
            uptime_percentage=data.get('uptime_percentage', 0.0),
            average_latency_ms=data.get('average_latency_ms', 0.0),
            capabilities=capabilities,
            sources=data.get('sources', []),
            confidence_score=data.get('confidence_score', 0.0),
            data_quality=data.get('data_quality', 'low'),
            last_updated=last_updated,
            is_managed=data.get('is_managed', False) or data.get('in_devices', False),
            is_monitored=data.get('is_monitored', False),
            tags=data.get('tags', []),
            notes=data.get('notes', ''),
            freebox_data=data.get('freebox_data'),
        )
