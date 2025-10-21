"""
🌐 333HOME - Network Routers
Routers modulaires pour l'API Network
"""

from .scan_router import router as scan_router
from .device_router import router as device_router
from .latency_router import router as latency_router
from .bandwidth_router import router as bandwidth_router
from .registry_router import router as registry_router  # Phase 6 Étape 2

__all__ = [
    "scan_router",
    "device_router",
    "latency_router",
    "bandwidth_router",
    "registry_router",
]
