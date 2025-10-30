"""
333HOME Agent - Configuration
==============================

Configuration pour agents de contrôle à distance.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
import platform
import os


class AgentConfig(BaseModel):
    """Configuration principale de l'agent."""
    
    # Identification
    agent_id: str = Field(..., description="ID unique de l'agent (ex: TITO, 333srv)")
    hostname: str = Field(default_factory=platform.node, description="Hostname du système")
    os_platform: Literal["windows", "linux", "darwin"] = Field(
        default_factory=lambda: platform.system().lower(),
        description="Système d'exploitation"
    )
    
    # Connexion Hub
    hub_url: str = Field(
        default="wss://333pie.local:8000/ws/agents",
        description="URL WebSocket du Hub"
    )
    hub_fallback_url: Optional[str] = Field(
        default=None,
        description="URL de secours (via VPN Tailscale)"
    )
    
    # Authentification
    jwt_token: Optional[str] = Field(default=None, description="Token JWT pour authentification")
    api_key: Optional[str] = Field(default=None, description="API key statique (fallback)")
    
    # Réseau
    tailscale_ip: Optional[str] = Field(default=None, description="IP Tailscale VPN")
    local_ip: Optional[str] = Field(default=None, description="IP LAN")
    prefer_vpn: bool = Field(default=True, description="Préférer VPN si disponible")
    
    # Comportement
    heartbeat_interval: int = Field(default=30, ge=10, le=300, description="Intervalle heartbeat (secondes)")
    reconnect_delay: int = Field(default=5, ge=1, le=60, description="Délai reconnexion (secondes)")
    max_reconnect_attempts: int = Field(default=10, ge=1, description="Tentatives reconnexion max")
    
    # Plugins
    plugins_enabled: list[str] = Field(
        default_factory=list,
        description="Liste plugins activés (vide = tous)"
    )
    plugins_disabled: list[str] = Field(
        default_factory=list,
        description="Liste plugins désactivés"
    )
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    log_file: Optional[str] = Field(default=None, description="Chemin fichier log")
    
    @validator("os_platform", pre=True)
    def normalize_platform(cls, v):
        """Normalise le nom de la plateforme."""
        if v.lower() in ["windows", "win32"]:
            return "windows"
        elif v.lower() in ["linux", "linux2"]:
            return "linux"
        elif v.lower() in ["darwin", "macos"]:
            return "darwin"
        return v.lower()
    
    @validator("hub_url")
    def validate_hub_url(cls, v):
        """Valide l'URL du Hub."""
        if not v.startswith(("ws://", "wss://")):
            raise ValueError("hub_url doit commencer par ws:// ou wss://")
        return v
    
    class Config:
        """Config Pydantic."""
        use_enum_values = True


class LogMeInRescueConfig(BaseModel):
    """Configuration plugin LogMeIn Rescue (Windows)."""
    
    # Browser
    browser: Literal["chrome", "firefox", "edge"] = Field(default="chrome")
    browser_binary: Optional[str] = Field(default=None, description="Chemin custom browser")
    headless: bool = Field(default=False, description="Mode headless (pas recommandé)")
    
    # Téléchargement
    download_dir: str = Field(
        default_factory=lambda: os.path.join(os.getenv("TEMP", "C:\\Temp"), "logmein"),
        description="Dossier téléchargements"
    )
    download_timeout: int = Field(default=60, ge=10, description="Timeout téléchargement (s)")
    
    # Exécution
    run_as_admin: bool = Field(default=True, description="Lancer en admin (UAC bypass)")
    auto_accept: bool = Field(default=True, description="Accepter droits automatiquement")
    auto_install: bool = Field(default=True, description="Installer logiciel si nécessaire")
    
    # Timeouts
    page_load_timeout: int = Field(default=30, ge=5, description="Timeout chargement page (s)")
    element_wait_timeout: int = Field(default=10, ge=1, description="Timeout attente élément (s)")


class SSHConsoleConfig(BaseModel):
    """Configuration plugin SSH Console (Linux)."""
    
    # Connexion SSH
    ssh_host: str = Field(..., description="Hostname ou IP cible")
    ssh_port: int = Field(default=22, ge=1, le=65535)
    ssh_username: str = Field(..., description="Username SSH")
    
    # Authentification
    ssh_key_path: Optional[str] = Field(default=None, description="Chemin clé privée SSH")
    ssh_password: Optional[str] = Field(default=None, description="Password SSH (non recommandé)")
    
    # Terminal
    terminal_cols: int = Field(default=80, ge=20, description="Colonnes terminal")
    terminal_rows: int = Field(default=24, ge=10, description="Lignes terminal")
    terminal_encoding: str = Field(default="utf-8")
    
    # Sécurité
    allow_exec: bool = Field(default=True, description="Autoriser exec commandes")
    allow_shell: bool = Field(default=True, description="Autoriser shell interactif")
    allowed_commands: list[str] = Field(
        default_factory=list,
        description="Commandes autorisées (vide = toutes)"
    )
    forbidden_commands: list[str] = Field(
        default_factory=lambda: ["rm -rf /", "dd if=/dev/zero", ":(){ :|:& };:"],
        description="Commandes interdites"
    )


# Configurations par défaut selon OS
DEFAULT_CONFIGS = {
    "windows": {
        "agent_id": "TITO",
        "tailscale_ip": "100.93.236.71",
        "local_ip": "192.168.1.174",
        "plugins_enabled": ["logmein_rescue", "system_info"]
    },
    "linux": {
        "agent_id": "333srv",
        "tailscale_ip": "100.80.31.55",
        "local_ip": "192.168.1.175",
        "plugins_enabled": ["ssh_console", "docker", "systemd", "system_info"]
    }
}


def get_default_config(os_platform: Optional[str] = None) -> AgentConfig:
    """
    Retourne la config par défaut selon l'OS.
    
    Args:
        os_platform: OS cible (auto-détecté si None)
    
    Returns:
        Configuration agent par défaut
    """
    if os_platform is None:
        os_platform = platform.system().lower()
    
    os_platform = "windows" if os_platform in ["windows", "win32"] else os_platform
    os_platform = "linux" if os_platform in ["linux", "linux2"] else os_platform
    
    base_config = DEFAULT_CONFIGS.get(os_platform, {})
    return AgentConfig(**base_config)
