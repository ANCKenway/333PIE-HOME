"""
Service de monitoring du Raspberry Pi
Fonctionnalités : température, CPU, mémoire, services système
"""

import subprocess
import psutil
from typing import Dict, List

class PiMonitor:
    """Monitoring du Raspberry Pi"""
    
    def get_system_status(self) -> Dict:
        """Status système complet"""
        try:
            return {
                "cpu": self._get_cpu_info(),
                "memory": self._get_memory_info(),
                "temperature": self._get_temperature(),
                "services": self._get_services_status()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_cpu_info(self) -> Dict:
        """Informations CPU"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        with open('/proc/loadavg', 'r') as f:
            load = f.read().split()[:3]
        
        return {
            "usage_percent": round(cpu_percent, 1),
            "load_average": [float(x) for x in load]
        }
    
    def _get_memory_info(self) -> Dict:
        """Informations mémoire"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "usage_percent": round(memory.percent, 1)
        }
    
    def _get_temperature(self) -> float:
        """Température CPU"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
            return round(temp, 1)
        except:
            return 0.0
    
    def _get_services_status(self) -> List[Dict]:
        """Status des services système"""
        services = []
        system_services = [
            {"name": "SSH", "service": "ssh", "port": 22},
            {"name": "Docker", "service": "docker"},
            {"name": "Nginx", "service": "nginx", "port": 80},
        ]
        
        for service in system_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service["service"]], 
                    capture_output=True, 
                    text=True, 
                    timeout=2
                )
                status = "online" if result.stdout.strip() == "active" else "offline"
                
                service_info = {
                    "name": service["name"],
                    "status": status,
                    "type": "system"
                }
                
                if "port" in service:
                    service_info["port"] = service["port"]
                    
                services.append(service_info)
            except:
                services.append({
                    "name": service["name"],
                    "status": "offline",
                    "type": "system"
                })
        
        return services