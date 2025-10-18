"""
Utilitaires système partagés
Fonctions communes pour le monitoring système
"""

import subprocess
import psutil
import os
from typing import Dict, Optional

def get_cpu_usage() -> float:
    """Utilisation CPU moyenne"""
    return psutil.cpu_percent(interval=0.1)

def get_memory_usage() -> Dict[str, float]:
    """Informations mémoire"""
    memory = psutil.virtual_memory()
    return {
        "total_gb": round(memory.total / (1024**3), 2),
        "used_gb": round(memory.used / (1024**3), 2),
        "free_gb": round(memory.available / (1024**3), 2),
        "usage_percent": round(memory.percent, 1)
    }

def get_temperature() -> float:
    """Température CPU du Raspberry Pi"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000
        return round(temp, 1)
    except:
        return 0.0

def get_uptime() -> str:
    """Uptime système formaté"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"

def check_service_status(service_name: str) -> bool:
    """Vérifie si un service systemd est actif"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def run_command_safe(command: list, timeout: int = 5) -> Optional[str]:
    """Exécution sécurisée d'une commande"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None