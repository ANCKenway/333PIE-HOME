"""
🔧 333HOME - Configuration centralisée
Gestion moderne de la configuration avec Pydantic Settings
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # Application
    app_name: str = "333HOME"
    app_version: str = "3.0.0"
    app_description: str = "🏠 Système de domotique et gestion de parc informatique"
    debug: bool = False
    
    # Serveur
    host: str = Field(default="0.0.0.0", description="Adresse d'écoute du serveur")
    port: int = Field(default=8000, description="Port d'écoute du serveur API")
    reload: bool = Field(default=False, description="Auto-reload en développement")
    
    # Chemins
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Optional[Path] = Field(default=None)
    config_dir: Optional[Path] = Field(default=None)
    web_dir: Optional[Path] = Field(default=None)
    static_dir: Optional[Path] = Field(default=None)
    
    # Logging
    log_level: str = Field(default="INFO", description="Niveau de logging")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # CORS
    cors_origins: list = Field(default=["*"], description="Origines CORS autorisées")
    
    # Network Scanner
    scan_timeout: int = Field(default=30, description="Timeout scan réseau (secondes)")
    max_concurrent_scans: int = Field(default=50, description="Scans simultanés max")
    
    # Tailscale
    tailscale_api_base: str = "https://api.tailscale.com/api/v2"
    tailscale_cache_ttl: int = Field(default=300, description="TTL cache Tailscale (secondes)")
    
    # Devices
    device_check_interval: int = Field(default=60, description="Intervalle vérification appareils (secondes)")
    device_history_retention: int = Field(default=30, description="Rétention historique appareils (jours)")
    
    # Performance
    worker_threads: int = Field(default=4, description="Nombre de workers threads")
    max_request_size: int = Field(default=10 * 1024 * 1024, description="Taille max requête (bytes)")
    
    # Intégration 333srv
    srv_333_host: str = Field(default="192.168.1.175", description="Adresse serveur 333srv")
    srv_333_port: int = Field(default=8000, description="Port serveur 333srv")
    srv_333_enabled: bool = Field(default=False, description="Intégration 333srv activée")
    
    class Config:
        env_prefix = "HOME333_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_paths()
    
    def _init_paths(self):
        """Initialiser les chemins par défaut"""
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.config_dir is None:
            self.config_dir = self.base_dir / "config"
        if self.web_dir is None:
            self.web_dir = self.base_dir / "web"
        if self.static_dir is None:
            self.static_dir = self.web_dir / "static"
        
        # Créer les répertoires s'ils n'existent pas
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"📁 Chemins configurés:")
        logger.info(f"   Base: {self.base_dir}")
        logger.info(f"   Data: {self.data_dir}")
        logger.info(f"   Config: {self.config_dir}")
        logger.info(f"   Web: {self.web_dir}")
    
    def get_summary(self) -> dict:
        """Obtenir un résumé de la configuration"""
        return {
            "app": {
                "name": self.app_name,
                "version": self.app_version,
                "debug": self.debug
            },
            "server": {
                "host": self.host,
                "port": self.port,
                "reload": self.reload
            },
            "paths": {
                "base": str(self.base_dir),
                "data": str(self.data_dir),
                "config": str(self.config_dir),
                "web": str(self.web_dir)
            },
            "integration": {
                "333srv_enabled": self.srv_333_enabled,
                "333srv_host": self.srv_333_host if self.srv_333_enabled else None
            }
        }


# Instance globale de configuration
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection pour obtenir les settings"""
    return settings
