"""
333HOME Agents - Plugins Common
================================

Plugins cross-platform (Windows + Linux).
"""

from .system_info import SystemInfoPlugin
from .self_update import SelfUpdatePlugin

__all__ = ["SystemInfoPlugin", "SelfUpdatePlugin"]
