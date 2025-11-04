"""
333HOME Agents - Plugins Common
================================

Plugins cross-platform (Windows + Linux).
"""

from .system_info import SystemInfoPlugin
from .self_update import SelfUpdatePlugin
from .system_restart import SystemRestartPlugin

__all__ = ["SystemInfoPlugin", "SelfUpdatePlugin", "SystemRestartPlugin"]
