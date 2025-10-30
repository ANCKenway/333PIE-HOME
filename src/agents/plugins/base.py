"""
333HOME Agents - Système de Plugins
====================================

Classes abstraites pour système de plugins extensible.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field, validator
import logging


logger = logging.getLogger(__name__)


class PluginParams(BaseModel):
    """Modèle de base pour paramètres de plugins."""
    pass


class PluginResult(BaseModel):
    """Résultat d'exécution d'un plugin."""
    
    status: Literal["success", "error", "timeout", "cancelled"] = Field(
        ...,
        description="Statut d'exécution"
    )
    message: str = Field(
        default="",
        description="Message descriptif"
    )
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Données résultat"
    )
    error: Optional[str] = Field(
        default=None,
        description="Message d'erreur si status=error"
    )
    duration_ms: Optional[float] = Field(
        default=None,
        description="Durée exécution en millisecondes"
    )


class BasePlugin(ABC):
    """
    Classe abstraite pour tous les plugins.
    
    Un plugin est une unité de fonctionnalité exécutable par un agent.
    Exemples: LogMeIn automation, SSH console, Docker control, etc.
    """
    
    # Métadonnées (à définir dans les sous-classes)
    name: str = "base_plugin"
    description: str = "Plugin de base"
    version: str = "1.0.0"
    os_platform: Literal["windows", "linux", "darwin", "all"] = "all"
    
    def __init__(self):
        """Initialise le plugin."""
        self.logger = logging.getLogger(f"plugin.{self.name}")
        self._enabled = True
    
    @abstractmethod
    async def execute(self, params: PluginParams) -> PluginResult:
        """
        Exécute la fonctionnalité principale du plugin.
        
        Args:
            params: Paramètres d'exécution (sous-classe de PluginParams)
        
        Returns:
            Résultat d'exécution
        
        Raises:
            PluginExecutionError: Si l'exécution échoue
        """
        pass
    
    @abstractmethod
    def validate_params(self, params: dict) -> bool:
        """
        Valide les paramètres avant exécution.
        
        Args:
            params: Paramètres bruts (dict)
        
        Returns:
            True si valide, False sinon
        """
        pass
    
    def get_schema(self) -> dict:
        """
        Retourne le schéma JSON des paramètres attendus.
        
        Returns:
            Schéma JSON Pydantic
        """
        return PluginParams.schema()
    
    async def setup(self) -> bool:
        """
        Setup initial du plugin (optionnel).
        Appelé une fois au chargement.
        
        Returns:
            True si setup réussi
        """
        self.logger.info(f"Plugin {self.name} setup completed")
        return True
    
    async def teardown(self) -> bool:
        """
        Nettoyage du plugin (optionnel).
        Appelé avant déchargement.
        
        Returns:
            True si teardown réussi
        """
        self.logger.info(f"Plugin {self.name} teardown completed")
        return True
    
    def is_compatible(self, os_platform: str) -> bool:
        """
        Vérifie si le plugin est compatible avec l'OS.
        
        Args:
            os_platform: Nom de l'OS ("windows", "linux", "darwin")
        
        Returns:
            True si compatible
        """
        if self.os_platform == "all":
            return True
        return self.os_platform.lower() == os_platform.lower()
    
    def enable(self):
        """Active le plugin."""
        self._enabled = True
        self.logger.info(f"Plugin {self.name} enabled")
    
    def disable(self):
        """Désactive le plugin."""
        self._enabled = False
        self.logger.info(f"Plugin {self.name} disabled")
    
    @property
    def enabled(self) -> bool:
        """Indique si le plugin est activé."""
        return self._enabled
    
    def __repr__(self) -> str:
        return (
            f"<Plugin {self.name} v{self.version} "
            f"[{self.os_platform}] {'✓' if self._enabled else '✗'}>"
        )


class WindowsPlugin(BasePlugin):
    """
    Plugin de base pour fonctionnalités Windows.
    
    Héritent de cette classe les plugins:
    - LogMeIn Rescue automation
    - Remote Desktop Protocol (RDP)
    - PowerShell execution
    - Windows services control
    """
    
    os_platform: Literal["windows"] = "windows"
    
    def __init__(self):
        super().__init__()
        self._check_windows_dependencies()
    
    def _check_windows_dependencies(self):
        """Vérifie les dépendances Windows spécifiques."""
        try:
            import ctypes
            self._is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            self._is_admin = False
    
    @property
    def is_admin(self) -> bool:
        """Indique si le processus a les droits administrateur."""
        return self._is_admin
    
    async def elevate_privileges(self) -> bool:
        """
        Élève les privilèges en admin si nécessaire (UAC bypass).
        
        Returns:
            True si élevé avec succès
        """
        if self.is_admin:
            self.logger.info("Already running as administrator")
            return True
        
        self.logger.warning("Not running as administrator")
        # Logique UAC bypass ici (via ctypes ShellExecuteW)
        return False


class LinuxPlugin(BasePlugin):
    """
    Plugin de base pour fonctionnalités Linux.
    
    Héritent de cette classe les plugins:
    - SSH console
    - Docker control
    - Systemd services
    - VNC/noVNC
    """
    
    os_platform: Literal["linux"] = "linux"
    
    def __init__(self):
        super().__init__()
        self._check_linux_dependencies()
    
    def _check_linux_dependencies(self):
        """Vérifie les dépendances Linux spécifiques."""
        import os
        self._is_root = os.geteuid() == 0
    
    @property
    def is_root(self) -> bool:
        """Indique si le processus tourne en root."""
        return self._is_root
    
    async def check_systemd(self) -> bool:
        """
        Vérifie si systemd est disponible.
        
        Returns:
            True si systemd actif
        """
        import subprocess
        try:
            result = subprocess.run(
                ["systemctl", "is-system-running"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to check systemd: {e}")
            return False


class PluginExecutionError(Exception):
    """Exception levée lors d'une erreur d'exécution plugin."""
    pass
