"""
📱 333HOME - Devices Feature
Gestion complète des appareils (CRUD, monitoring, Wake-on-LAN)
"""

from .manager import DeviceManager
from .monitor import DeviceMonitor
from .wol import WakeOnLanService
from .router import router
from .schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    WakeOnLanRequest,
    DeviceStatusSummary
)


__all__ = [
    "DeviceManager",
    "DeviceMonitor",
    "WakeOnLanService",
    "router",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "WakeOnLanRequest",
    "DeviceStatusSummary"
]
