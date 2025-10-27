"""
📌 333HOME - Constantes de l'application
Valeurs constantes utilisées à travers l'application
"""

from enum import Enum


# Statuts d'appareils (SOURCE UNIQUE - RÈGLE #1)
class DeviceStatus(str, Enum):
    """
    Statut d'un appareil - SOURCE UNIQUE pour toute l'app
    
    ⚠️ NE PAS dupliquer cette enum ailleurs (RÈGLE #1)
    Import: from src.shared.constants import DeviceStatus
    """
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    PENDING = "pending"  # Appareil en cours de détection
    ERROR = "error"      # Erreur lors de la détection


# Types d'appareils
class DeviceType(str, Enum):
    COMPUTER = "computer"
    SERVER = "server"
    PHONE = "phone"
    TABLET = "tablet"
    IOT = "iot"
    NETWORK = "network"
    PRINTER = "printer"
    TV = "tv"
    CONSOLE = "console"
    OTHER = "other"


# Types d'événements réseau
class NetworkEventType(str, Enum):
    NEW_DEVICE = "new_device"
    RECONNECTION = "reconnection"
    DISCONNECTION = "disconnection"
    IP_CHANGE = "ip_change"
    MAC_CHANGE = "mac_change"
    HOSTNAME_CHANGE = "hostname_change"


# Types de scans réseau
class ScanType(str, Enum):
    QUICK = "quick"
    FULL = "full"
    DEEP = "deep"
    CUSTOM = "custom"


# Niveaux de log personnalisés
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}


# Timeouts par défaut (secondes)
DEFAULT_TIMEOUTS = {
    "scan": 30,
    "ping": 5,
    "http": 10,
    "api": 30
}

# Network scanning
DEFAULT_SCAN_TIMEOUT = 2000  # millisecondes
DEFAULT_SUBNET = "192.168.1.0/24"


# Limites
MAX_DEVICES = 1000
MAX_SCAN_HISTORY = 100
MAX_EVENTS = 500
MAX_LOG_ENTRIES = 1000


# Intervalles (secondes)
INTERVALS = {
    "device_check": 60,
    "network_scan": 300,
    "status_update": 30,
    "cache_cleanup": 3600
}


# Chemins API
API_PATHS = {
    "devices": "/api/devices",
    "network": "/api/network",
    "tailscale": "/api/tailscale",
    "monitoring": "/api/monitoring",
    "system": "/api/system"
}


# Messages d'erreur standards
ERROR_MESSAGES = {
    "device_not_found": "Appareil non trouvé",
    "invalid_ip": "Adresse IP invalide",
    "invalid_mac": "Adresse MAC invalide",
    "scan_in_progress": "Un scan est déjà en cours",
    "scan_failed": "Échec du scan réseau",
    "service_unavailable": "Service temporairement indisponible",
    "unauthorized": "Accès non autorisé",
    "rate_limit": "Trop de requêtes, veuillez réessayer plus tard"
}


# Emojis pour les logs (parce que c'est plus sympa 😊)
EMOJIS = {
    "start": "🚀",
    "stop": "🔴",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "device": "📱",
    "network": "🌐",
    "scan": "🔍",
    "config": "⚙️",
    "file": "📁",
    "api": "🔗",
    "time": "⏱️",
    "user": "👤",
    "server": "🖥️"
}


# Configuration par défaut des features
DEFAULT_FEATURE_FLAGS = {
    "network_scan": True,
    "wake_on_lan": True,
    "tailscale": True,
    "monitoring": True,
    "system_control": False,  # Désactivé par défaut pour sécurité
    "333srv_integration": False  # À activer manuellement
}


# Patterns de détection d'appareils
DEVICE_PATTERNS = {
    "raspberry": [r"raspberry", r"raspbian", r"rpi"],
    "windows": [r"windows", r"microsoft", r"msft"],
    "linux": [r"linux", r"ubuntu", r"debian"],
    "mac": [r"apple", r"macos", r"mac os"],
    "android": [r"android", r"samsung"],
    "ios": [r"iphone", r"ipad", r"ios"],
    "router": [r"router", r"gateway", r"ubiquiti"],
    "switch": [r"switch", r"netgear"],
    "printer": [r"printer", r"hp", r"canon", r"epson"]
}


# Ports communs pour la détection
COMMON_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
    9090: "Web-Admin"
}
