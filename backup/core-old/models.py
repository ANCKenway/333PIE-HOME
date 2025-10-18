"""
🏠 333HOME - Modèles de Données
Classes de données pour la gestion de parc informatique
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

# ===== ÉNUMÉRATIONS =====

class DeviceStatus(Enum):
    """États des appareils"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    FAVORITE = "favorite"

class DeviceType(Enum):
    """Types d'appareils"""
    COMPUTER = "computer"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"
    ROUTER = "router"
    SWITCH = "switch"
    PRINTER = "printer"
    TV = "tv"
    CONSOLE = "console"
    IOT = "iot"
    SERVER = "server"
    NAS = "nas"
    UNKNOWN = "unknown"

class ActionType(Enum):
    """Types d'actions possibles"""
    WAKE_ON_LAN = "wake_on_lan"
    PING = "ping"
    SSH = "ssh"
    HTTP = "http"
    SHUTDOWN = "shutdown"

# ===== MODÈLES PRINCIPAUX =====

@dataclass
class Device:
    """Modèle d'appareil réseau"""
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    device_type: DeviceType = DeviceType.UNKNOWN
    status: DeviceStatus = DeviceStatus.UNKNOWN
    is_favorite: bool = False
    nickname: str = ""
    description: str = ""
    last_seen: Optional[str] = None
    first_seen: Optional[str] = None
    scan_count: int = 0
    
    def __post_init__(self):
        """Post-traitement après création"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not self.first_seen:
            self.first_seen = now
        if not self.last_seen:
            self.last_seen = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        data = asdict(self)
        data['device_type'] = self.device_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """Création depuis dictionnaire"""
        # Conversion des enums
        if 'device_type' in data:
            data['device_type'] = DeviceType(data['device_type'])
        if 'status' in data:
            data['status'] = DeviceStatus(data['status'])
        
        return cls(**data)
    
    def mark_as_favorite(self, nickname: str = "", description: str = ""):
        """Marquer comme favori"""
        self.is_favorite = True
        self.status = DeviceStatus.FAVORITE
        if nickname:
            self.nickname = nickname
        if description:
            self.description = description
    
    def update_seen(self):
        """Mettre à jour dernière vue"""
        self.last_seen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.scan_count += 1

@dataclass
class ScanResult:
    """Résultat d'un scan réseau"""
    scan_id: str
    timestamp: str
    network: str
    scan_type: str  # "quick" ou "full"
    devices: List[Device]
    duration_seconds: float
    total_found: int
    new_devices: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'scan_id': self.scan_id,
            'timestamp': self.timestamp,
            'network': self.network,
            'scan_type': self.scan_type,
            'devices': [device.to_dict() for device in self.devices],
            'duration_seconds': self.duration_seconds,
            'total_found': self.total_found,
            'new_devices': self.new_devices
        }

@dataclass
class SystemInfo:
    """Informations système"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    temperature: Optional[float]
    uptime_seconds: int
    load_average: List[float]
    network_bytes_sent: int
    network_bytes_recv: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return asdict(self)

@dataclass
class DeviceAction:
    """Action sur un appareil"""
    device_ip: str
    action_type: ActionType
    timestamp: str
    success: bool
    message: str = ""
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return data

@dataclass
class ApiResponse:
    """Réponse API standardisée"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        result = {
            'success': self.success,
            'timestamp': self.timestamp
        }
        
        if self.message:
            result['message'] = self.message
        if self.data is not None:
            result['data'] = self.data
        if self.error:
            result['error'] = self.error
            
        return result

# ===== FONCTIONS UTILITAIRES =====

def create_scan_id() -> str:
    """Génère un ID unique pour un scan"""
    return f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def get_device_display_name(device: Device) -> str:
    """Nom d'affichage d'un appareil"""
    if device.nickname:
        return device.nickname
    if device.hostname:
        return device.hostname
    return device.ip

print("✅ Modèles de données chargés")