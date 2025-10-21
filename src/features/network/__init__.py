"""
🌐 333HOME - Network Feature
Hub de monitoring réseau complet

Fonctionnalités:
- Scanner réseau (ICMP + mDNS + ARP)
- Détection avancée (vendor API + OUI database)
- Port scanning (35+ services)
- Latency monitoring (quality scoring)
- Bandwidth monitoring (usage tracking)
- Historique complet des appareils
- Timeline des événements
- Promotion vers Devices
- Statistiques réseau
"""

from .schemas import (
    # Enums
    ScanType,
    NetworkEventType,
    DeviceStatus,
    
    # Network Device
    NetworkDevice,
    NetworkDeviceCreate,
    NetworkDeviceDetailed,
    ServiceInfo,
    
    # Scan
    ScanRequest,
    ScanResult,
    
    # History
    IPHistoryEntry,
    DeviceHistory,
    OnlinePeriod,
    
    # Events
    NetworkEvent,
    NetworkEventDetailed,
    NetworkTimeline,
    
    # Statistics
    NetworkStats,
    DeviceStatistics,
    
    # Promote
    PromoteToDevicesRequest,
    PromoteToDevicesResponse,
)

from .scanners.multi_source import MultiSourceScanner  # ✅ Déplacé dans scanners/
from .detector import DeviceDetector
# ❌ port_scanner.py supprimé (orphelin - scanner.py n'existe plus)
from .monitoring.latency_monitor import get_latency_monitor, LatencyStats  # ✅ Déplacé dans monitoring/
from .monitoring.bandwidth_monitor import (  # ✅ Déplacé dans monitoring/
    get_bandwidth_monitor,
    BandwidthMonitor,
    BandwidthStats,
    BandwidthSample,
)
from .storage import (
    save_scan_result,
    get_all_devices,
    get_device_by_mac,
    update_device_in_devices_flag,
)
from .history import NetworkHistory
from .router import router as network_router


__all__ = [
    # Enums
    "ScanType",
    "NetworkEventType",
    "DeviceStatus",
    
    # Network Device
    "NetworkDevice",
    "NetworkDeviceCreate",
    "NetworkDeviceDetailed",
    "ServiceInfo",
    
    # Scan
    "ScanRequest",
    "ScanResult",
    
    # History
    "IPHistoryEntry",
    "DeviceHistory",
    "OnlinePeriod",
    
    # Events
    "NetworkEvent",
    "NetworkEventDetailed",
    "NetworkTimeline",
    
    # Statistics
    "NetworkStats",
    "DeviceStatistics",
    
    # Promote
    "PromoteToDevicesRequest",
    "PromoteToDevicesResponse",
    
    # Core components
    "MultiSourceScanner",
    "DeviceDetector",
    "NetworkHistory",
    
    # Professional monitoring
    # ❌ PortScanner supprimé (orphelin)
    "get_latency_monitor",
    "LatencyStats",
    "get_bandwidth_monitor",
    "BandwidthMonitor",
    "BandwidthStats",
    "BandwidthSample",
    
    # Storage
    "save_scan_result",
    "get_all_devices",
    "get_device_by_mac",
    "update_device_in_devices_flag",
    
    # Router
    "network_router",
]
