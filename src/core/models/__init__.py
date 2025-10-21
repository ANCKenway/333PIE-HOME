"""
🏠 333HOME - Core Models

Models partagés pour toute l'application
"""

from .unified_device import (
    UnifiedDevice,
    IPChange,
    HostnameChange,
    OnlinePeriod,
    DeviceCapabilities,
    DeviceStatus,
    InterfaceType,
)

__all__ = [
    'UnifiedDevice',
    'IPChange',
    'HostnameChange',
    'OnlinePeriod',
    'DeviceCapabilities',
    'DeviceStatus',
    'InterfaceType',
]
