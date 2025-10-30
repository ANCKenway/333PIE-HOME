"""
🌐 Plugin System Info - Cross-Platform
=======================================

Plugin de test pour collecte informations système.
Fonctionne sur Windows, Linux et macOS.
"""

from typing import Optional
from pydantic import BaseModel, Field
import platform
import psutil
import asyncio
import logging

from ..base import BasePlugin, PluginParams, PluginResult


logger = logging.getLogger(__name__)


class SystemInfoParams(PluginParams):
    """Paramètres pour collecte système."""
    
    include_cpu: bool = Field(default=True, description="Inclure info CPU")
    include_memory: bool = Field(default=True, description="Inclure info RAM")
    include_disk: bool = Field(default=True, description="Inclure info disques")
    include_network: bool = Field(default=True, description="Inclure info réseau")
    include_processes: bool = Field(default=False, description="Inclure top processus")


class SystemInfoPlugin(BasePlugin):
    """
    Plugin de collecte informations système.
    
    Cross-platform (Windows, Linux, macOS).
    Utilisé pour test et monitoring basique.
    """
    
    name = "system_info"
    description = "Collecte informations système cross-platform"
    version = "1.0.0"
    os_platform = "all"
    
    async def setup(self) -> bool:
        """Setup du plugin."""
        try:
            # Vérifier psutil disponible
            import psutil
            self.logger.info("System info plugin ready")
            return True
        except ImportError:
            self.logger.error("psutil not installed. Install: pip install psutil")
            return False
    
    async def execute(self, params: SystemInfoParams) -> PluginResult:
        """
        Collecte les informations système.
        
        Args:
            params: Options de collecte
        
        Returns:
            Résultat avec données système
        """
        try:
            data = {}
            
            # Info système de base
            data["system"] = {
                "hostname": platform.node(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor()
            }
            
            # CPU
            if params.include_cpu:
                data["cpu"] = {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
            
            # Memory
            if params.include_memory:
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                data["memory"] = {
                    "total": mem.total,
                    "available": mem.available,
                    "used": mem.used,
                    "percent": mem.percent,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_percent": swap.percent
                }
            
            # Disk
            if params.include_disk:
                partitions = psutil.disk_partitions()
                data["disk"] = []
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        data["disk"].append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        })
                    except PermissionError:
                        continue
            
            # Network
            if params.include_network:
                net_io = psutil.net_io_counters()
                data["network"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            
            # Top processes
            if params.include_processes:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort by CPU
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                data["top_processes"] = processes[:10]
            
            return PluginResult(
                status="success",
                message="System info collected successfully",
                data=data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system info: {e}", exc_info=True)
            return PluginResult(
                status="error",
                message="Failed to collect system info",
                error=str(e)
            )
    
    def validate_params(self, params: dict) -> bool:
        """Valide les paramètres."""
        try:
            SystemInfoParams(**params)
            return True
        except Exception as e:
            self.logger.error(f"Invalid params: {e}")
            return False
    
    def get_schema(self) -> dict:
        """Retourne le schéma des paramètres."""
        return SystemInfoParams.schema()
