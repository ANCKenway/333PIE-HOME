"""
📊 333HOME - Device Monitor
Monitoring du statut des appareils (ping, online/offline)

Phase 6 Étape 2: Utilise NetworkRegistry comme source unique de vérité.
Au lieu de ping individuel (lent), récupère le statut depuis le registry
(enrichi par les scans réseau réguliers).
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
        self._registry_cache: Dict[str, Dict] = {}  # Cache du registry
        self._cache_timestamp = None
        logger.info("📊 DeviceMonitor initialisé (avec NetworkRegistry)")
    
    def _load_registry_cache(self):
        """
        Charger le cache depuis le NetworkRegistry
        
        Phase 6: Source unique de vérité pour statuts online/offline.
        Évite les pings redondants avec les scans réseau.
        """
        try:
            from src.features.network.registry import get_network_registry
            registry = get_network_registry()
            
            # Construire cache {MAC: {is_online, last_seen, current_ip}}
            self._registry_cache = {}
            for device in registry.get_all_devices():
                mac = device['mac'].upper()
                self._registry_cache[mac] = {
                    'is_online': device.get('is_online', False),
                    'last_seen': device.get('last_seen'),
                    'current_ip': device.get('current_ip')
                }
            
            logger.debug(f"📊 Registry cache loaded: {len(self._registry_cache)} devices")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load registry cache: {e}")
            self._registry_cache = {}
    
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
        
        Phase 6: Priorité au NetworkRegistry (scan enrichi automatique).
        Fallback sur ping si device pas dans registry (cas rare).
        
        Args:
            device: Dictionnaire avec les infos de l'appareil
            
        Returns:
            Device avec statut mis à jour
        """
        mac = device.get('mac', '').upper()
        ip = device.get('ip')
        
        # 1. Essayer d'abord depuis le registry cache (source unique de vérité)
        if mac and mac in self._registry_cache:
            registry_status = self._registry_cache[mac]
            online = registry_status['is_online']
            
            logger.debug(f"✅ Status from registry: {mac[:17]} = {online}")
            
            return {
                **device,
                'status': 'online' if online else 'offline',
                'online': online,
                'last_seen': registry_status.get('last_seen')
            }
        
        # 2. Fallback: ping direct si pas dans registry (device géré mais pas encore scanné)
        if not ip:
            return {**device, 'status': 'unknown', 'online': False}
        
        logger.debug(f"⚠️ Device {mac[:17]} not in registry, fallback to ping")
        online = await self.ping(ip)
        
        return {
            **device,
            'status': 'online' if online else 'offline',
            'online': online
        }
    
    async def check_multiple_devices(self, devices: List[Dict]) -> List[Dict]:
        """
        Vérifier le statut de plusieurs appareils en parallèle
        
        Phase 6: Charge le registry cache une fois, puis check tous devices.
        Évite N pings redondants (source unique = registry).
        
        Args:
            devices: Liste d'appareils
            
        Returns:
            Liste d'appareils avec statuts mis à jour
        """
        # Charger le registry cache AVANT de vérifier les devices
        self._load_registry_cache()
        
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
