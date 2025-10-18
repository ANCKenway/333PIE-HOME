"""
Service de monitoring du Raspberry Pi
Fonctionnalités : température, CPU, mémoire, services système
"""

import subprocess
import psutil
from typing import Dict, List
from ..utils.system import get_cpu_usage, get_memory_usage, get_temperature, get_uptime, check_service_status

class PiMonitor:
    """Monitoring du Raspberry Pi"""
    
    def get_system_status(self) -> Dict:
        """Status système complet"""
        try:
            return {
                "cpu": self._get_cpu_info(),
                "memory": get_memory_usage(),
                "temperature": get_temperature(),
                "uptime": get_uptime(),
                "services": self._get_services_status()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_cpu_info(self) -> Dict:
        """Informations CPU"""
        cpu_percent = get_cpu_usage()
        try:
            with open('/proc/loadavg', 'r') as f:
                load = f.read().split()[:3]
            
            return {
                "usage_percent": round(cpu_percent, 1),
                "load_1m": float(load[0]),
                "load_5m": float(load[1]),
                "load_15m": float(load[2])
            }
        except:
            return {"usage_percent": round(cpu_percent, 1)}
    
    def _get_services_status(self) -> List[Dict]:
        """Status des services système"""
        services = []
        system_services = [
            {"name": "SSH", "service": "ssh", "port": 22},
            {"name": "Docker", "service": "docker"},
            {"name": "Nginx", "service": "nginx", "port": 80},
        ]
        
        for service_info in system_services:
            status = check_service_status(service_info["service"])
            services.append({
                "name": service_info["name"],
                "status": "active" if status else "inactive",
                "port": service_info.get("port")
            })
        
        return services