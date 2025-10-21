"""
🏠 333HOME - Module Core
Cœur de l'application avec configuration, logging et lifecycle
"""

from .config import settings, get_settings, Settings
from .logging_config import setup_logging, get_logger
from .lifespan import lifespan, app_lifespan, on_startup, on_shutdown

__all__ = [
    "settings",
    "get_settings",
    "Settings",
    "setup_logging",
    "get_logger",
    "lifespan",
    "app_lifespan",
    "on_startup",
    "on_shutdown"
]
