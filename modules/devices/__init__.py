"""
🏠 Module Devices - Gestion et monitoring des appareils
Architecture modulaire selon RULES.md
"""

from .manager import DeviceManager
from .monitor import DeviceMonitor

__all__ = ['DeviceManager', 'DeviceMonitor']