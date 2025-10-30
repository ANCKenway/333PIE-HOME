"""
333HOME Agents - Plugin Manager
================================

Gestionnaire de plugins avec auto-découverte.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import BasePlugin


logger = logging.getLogger(__name__)


class PluginManager:
    """
    Gestionnaire de plugins avec auto-découverte.
    
    Charge automatiquement tous les plugins compatibles avec l'OS.
    """
    
    def __init__(self, os_platform: str):
        """
        Initialise le gestionnaire.
        
        Args:
            os_platform: OS de l'agent ("windows", "linux", "darwin")
        """
        self.os_platform = os_platform.lower()
        self.plugins: Dict[str, BasePlugin] = {}
        self._loaded = False
    
    async def load_plugins(self) -> int:
        """
        Charge tous les plugins compatibles.
        
        Returns:
            Nombre de plugins chargés
        """
        if self._loaded:
            logger.warning("Plugins already loaded")
            return len(self.plugins)
        
        logger.info(f"Loading plugins for {self.os_platform}...")
        
        # Charger plugins common (cross-platform)
        await self._load_from_module(".common")
        
        # Charger plugins OS-specific
        if self.os_platform == "windows":
            await self._load_from_module(".windows")
        elif self.os_platform == "linux":
            await self._load_from_module(".linux")
        
        self._loaded = True
        logger.info(f"[OK] Loaded {len(self.plugins)} plugins: {list(self.plugins.keys())}")
        return len(self.plugins)
    
    async def _load_from_module(self, module_name: str):
        """Charge les plugins depuis un module."""
        try:
            # Support imports relatifs
            if module_name.startswith("."):
                module = importlib.import_module(module_name, package=__package__)
            else:
                module = importlib.import_module(module_name)
            
            # Parcourir les attributs du module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Vérifier si c'est une classe plugin
                if (inspect.isclass(attr) and 
                    issubclass(attr, BasePlugin) and 
                    attr is not BasePlugin):
                    
                    # Instancier le plugin
                    plugin = attr()
                    
                    # Vérifier compatibilité OS
                    if plugin.is_compatible(self.os_platform):
                        # Setup plugin
                        if await plugin.setup():
                            self.plugins[plugin.name] = plugin
                            logger.info(f"  [OK] Loaded plugin: {plugin.name} v{plugin.version}")
                        else:
                            logger.warning(f"  [X] Failed to setup plugin: {plugin.name}")
                    else:
                        logger.debug(f"  [Skip] Skipped incompatible plugin: {plugin.name} ({plugin.os_platform})")
                        
        except ImportError as e:
            logger.warning(f"Could not import module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading plugins from {module_name}: {e}", exc_info=True)
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Récupère un plugin par son nom.
        
        Args:
            name: Nom du plugin
        
        Returns:
            Instance du plugin ou None
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[dict]:
        """
        Liste tous les plugins chargés.
        
        Returns:
            Liste des métadonnées plugins
        """
        return [
            {
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "os_platform": plugin.os_platform,
                "enabled": plugin.enabled,
                "schema": plugin.get_schema()
            }
            for plugin in self.plugins.values()
        ]
    
    def enable_plugin(self, name: str) -> bool:
        """Active un plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Désactive un plugin."""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.disable()
            return True
        return False
    
    async def unload_plugins(self):
        """Décharge tous les plugins."""
        logger.info("Unloading all plugins...")
        
        for plugin in self.plugins.values():
            try:
                await plugin.teardown()
            except Exception as e:
                logger.error(f"Error tearing down plugin {plugin.name}: {e}")
        
        self.plugins.clear()
        self._loaded = False
        logger.info("[OK] All plugins unloaded")
