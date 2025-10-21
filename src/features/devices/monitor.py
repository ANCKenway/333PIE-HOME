"""
📊 333HOME - Device Monitor
Monitoring du statut des appareils (ping, online/offline)
"""

import asyncio
import subprocess
from typing import Dict, List, Optional

from src.core import get_logger
from src.shared import NetworkError


logger = get_logger(__name__)


class DeviceMonitor:
    """Moniteur de statut des appareils"""
    
    def __init__(self):
        self.ping_timeout = 2  # secondes
        logger.info("📊 DeviceMonitor initialisé")
    
    async def ping(self, ip: str, timeout: int = None) -> bool:
        """
        Ping une adresse IP
        
        Args:
            ip: Adresse IP à pinger
            timeout: Timeout en secondes
            
        Returns:
            True si l'appareil répond, False sinon
        """
        timeout = timeout or self.ping_timeout
        
        try:
            # Utiliser ping système
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(timeout), ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            returncode = await process.wait()
            return returncode == 0
            
        except Exception as e:
            logger.debug(f"Ping failed for {ip}: {e}")
            return False
    
    async def check_device_status(self, device: Dict) -> Dict:
        """
        Vérifier le statut d'un appareil
        
        Args:
            device: Dictionnaire avec les infos de l'appareil
            
        Returns:
            Device avec statut mis à jour
        """
        ip = device.get('ip')
        if not ip:
            return {**device, 'status': 'unknown', 'online': False}
        
        online = await self.ping(ip)
        
        return {
            **device,
            'status': 'online' if online else 'offline',
            'online': online
        }
    
    async def check_multiple_devices(self, devices: List[Dict]) -> List[Dict]:
        """
        Vérifier le statut de plusieurs appareils en parallèle
        
        Args:
            devices: Liste d'appareils
            
        Returns:
            Liste d'appareils avec statuts mis à jour
        """
        tasks = [self.check_device_status(device) for device in devices]
        results = await asyncio.gather(*tasks)
        return list(results)
    
    def get_status_summary(self, devices: List[Dict]) -> Dict:
        """
        Obtenir un résumé du statut des appareils
        
        Args:
            devices: Liste d'appareils avec statuts
            
        Returns:
            Résumé des statuts
        """
        total = len(devices)
        online = sum(1 for d in devices if d.get('online', False))
        offline = sum(1 for d in devices if not d.get('online', False) and d.get('status') != 'unknown')
        unknown = sum(1 for d in devices if d.get('status') == 'unknown')
        
        return {
            'total': total,
            'online': online,
            'offline': offline,
            'unknown': unknown
        }
