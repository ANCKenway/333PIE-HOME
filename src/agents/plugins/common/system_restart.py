"""
🔄 Plugin System Restart - Redémarrer agent ou machine
=======================================================

Plugin cross-platform pour restart agent ou machine hôte.

Use Cases:
- Restart agent après configuration change
- Restart machine pour appliquer updates système
- Recovery après erreur critique

Méthodes:
- Windows: Service sc restart / shutdown /r
- Linux: Systemd restart / reboot
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
import asyncio
import logging
import platform
import subprocess
import sys
import os

from ..base import BasePlugin, PluginParams, PluginResult


logger = logging.getLogger(__name__)


class SystemRestartParams(PluginParams):
    """Paramètres pour restart système."""
    
    target: str = Field(
        default="agent",
        description="Cible restart: 'agent' ou 'system'"
    )
    
    delay: int = Field(
        default=5,
        ge=0,
        le=300,
        description="Délai avant restart (secondes)"
    )
    
    @validator("target")
    def validate_target(cls, v):
        """Valide la cible."""
        if v not in ["agent", "system"]:
            raise ValueError("target must be 'agent' or 'system'")
        return v


class SystemRestartPlugin(BasePlugin):
    """
    Plugin restart agent ou système.
    
    Compatible Windows, Linux, macOS.
    """
    
    name = "system_restart"
    description = "Redémarrer agent ou machine"
    version = "1.0.0"
    os_platform = "all"
    
    async def setup(self) -> bool:
        """Setup du plugin."""
        self.logger.info("System restart plugin ready")
        return True
    
    async def execute(self, params: dict) -> PluginResult:
        """
        Exécute le restart.
        
        Args:
            params: Options restart (dict ou SystemRestartParams)
        
        Returns:
            Résultat avec confirmation restart schedulé
        """
        # Convertir dict en objet Pydantic si nécessaire
        if isinstance(params, dict):
            params = SystemRestartParams(**params)
        
        try:
            if params.target == "agent":
                return await self._restart_agent(params.delay)
            elif params.target == "system":
                return await self._restart_system(params.delay)
            else:
                return PluginResult(
                    status="error",
                    message=f"Invalid target: {params.target}"
                )
        
        except Exception as e:
            self.logger.error(f"Restart failed: {e}", exc_info=True)
            return PluginResult(
                status="error",
                message="Restart failed",
                error=str(e)
            )
    
    async def _restart_agent(self, delay: int) -> PluginResult:
        """
        Redémarre l'agent.
        
        Méthodes selon déploiement:
        - Windows: Service (sc restart) ou subprocess pythonw
        - Linux: Systemd (systemctl restart) ou subprocess
        """
        os_name = platform.system()
        
        if os_name == "Windows":
            # Windows: Priorité service > subprocess
            try:
                # Vérifier si service Windows existe
                result = subprocess.run(
                    ['sc', 'query', '333HOME Agent'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Service existe, utiliser sc restart
                    subprocess.Popen(
                        f'timeout {delay} && sc stop "333HOME Agent" && sc start "333HOME Agent"',
                        shell=True,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    
                    return PluginResult(
                        status="success",
                        message=f"Agent restart scheduled in {delay}s (service)",
                        data={"method": "windows_service", "delay": delay}
                    )
            
            except Exception as e:
                self.logger.debug(f"Service restart failed: {e}")
            
            # Fallback: Restart via subprocess (tray icon ou standalone)
            try:
                # Déterminer script à relancer
                agent_dir = os.path.dirname(os.path.abspath(__file__))
                agent_tray = os.path.join(agent_dir, "..", "..", "agent_tray.pyw")
                
                if os.path.exists(agent_tray):
                    # Tray icon disponible
                    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                    subprocess.Popen(
                        f'timeout {delay} && "{python_exe}" "{agent_tray}"',
                        shell=True,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    method = "tray_icon"
                else:
                    # Agent standalone
                    python_exe = sys.executable
                    agent_py = os.path.join(agent_dir, "..", "..", "agent.py")
                    subprocess.Popen(
                        [python_exe, agent_py] + sys.argv[1:],
                        cwd=os.path.dirname(agent_py),
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    method = "subprocess"
                
                # Exit après délai
                await asyncio.sleep(delay)
                os._exit(0)
                
            except Exception as e:
                self.logger.error(f"Subprocess restart failed: {e}")
                return PluginResult(
                    status="error",
                    message="Restart failed",
                    error=str(e)
                )
        
        else:
            # Linux/macOS: Priorité systemd > subprocess
            try:
                # Vérifier si systemd service existe
                result = subprocess.run(
                    ['systemctl', 'is-active', '333agent'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Service systemd actif
                    subprocess.Popen(
                        ['sh', '-c', f'sleep {delay} && systemctl restart 333agent'],
                        start_new_session=True
                    )
                    
                    return PluginResult(
                        status="success",
                        message=f"Agent restart scheduled in {delay}s (systemd)",
                        data={"method": "systemd", "delay": delay}
                    )
            
            except Exception as e:
                self.logger.debug(f"Systemd restart failed: {e}")
            
            # Fallback: Subprocess direct
            try:
                agent_dir = os.path.dirname(os.path.abspath(__file__))
                agent_py = os.path.join(agent_dir, "..", "..", "agent.py")
                
                subprocess.Popen(
                    ['sh', '-c', f'sleep {delay} && {sys.executable} {agent_py} {" ".join(sys.argv[1:])}'],
                    cwd=os.path.dirname(agent_py),
                    start_new_session=True
                )
                
                # Exit après délai
                await asyncio.sleep(delay)
                os._exit(0)
                
            except Exception as e:
                self.logger.error(f"Subprocess restart failed: {e}")
                return PluginResult(
                    status="error",
                    message="Restart failed",
                    error=str(e)
                )
        
        return PluginResult(
            status="error",
            message="No restart method available"
        )
    
    async def _restart_system(self, delay: int) -> PluginResult:
        """
        Redémarre la machine.
        
        Nécessite droits administrateur/sudo.
        """
        os_name = platform.system()
        
        try:
            if os_name == "Windows":
                # Windows: shutdown /r
                subprocess.Popen(
                    f"shutdown /r /t {delay} /c \"333HOME Agent scheduled restart\"",
                    shell=True
                )
                
                return PluginResult(
                    status="success",
                    message=f"System restart scheduled in {delay}s",
                    data={"os": "windows", "delay": delay}
                )
            
            else:
                # Linux/macOS: shutdown -r
                subprocess.Popen(
                    ['sh', '-c', f'sleep {delay} && shutdown -r now "333HOME Agent scheduled restart"'],
                    start_new_session=True
                )
                
                return PluginResult(
                    status="success",
                    message=f"System restart scheduled in {delay}s",
                    data={"os": os_name.lower(), "delay": delay}
                )
        
        except Exception as e:
            self.logger.error(f"System restart failed: {e}", exc_info=True)
            return PluginResult(
                status="error",
                message="System restart failed",
                error=str(e)
            )
    
    def validate_params(self, params: dict) -> bool:
        """Valide les paramètres."""
        try:
            SystemRestartParams(**params)
            return True
        except Exception as e:
            self.logger.error(f"Invalid params: {e}")
            return False
    
    def get_schema(self) -> dict:
        """Retourne le schéma des paramètres."""
        return SystemRestartParams.schema()
