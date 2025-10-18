"""
🏠 Device Monitor - Monitoring intelligent d'appareils
Vérification par IP + Hostname + MAC (DHCP-friendly)
Architecture modulaire selon RULES.md
"""

import asyncio
import subprocess
import time
from typing import Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

class DeviceMonitor:
    def __init__(self):
        self.status_cache = {}
        self.arp_cache = {}
        self.cache_duration = 300  # 5 minutes
        self.ping_timeout = 1  # 1 seconde
        
    async def quick_ping(self, ip: str) -> bool:
        """Ping rapide d'un appareil (1 paquet, 1s timeout)"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(self.ping_timeout), ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            returncode = await result.wait()
            return returncode == 0
        except Exception as e:
            logger.debug(f"Ping error for {ip}: {e}")
            return False
    
    def get_arp_table(self) -> Dict[str, str]:
        """Récupérer la table ARP locale (très rapide, pas de réseau)"""
        if 'arp_table' in self.arp_cache:
            cached_data = self.arp_cache['arp_table']
            if time.time() - cached_data['timestamp'] < 60:  # Cache ARP 1 minute
                return cached_data['data']
        
        arp_table = {}
        try:
            # Lire la table ARP système
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=2)
            for line in result.stdout.split('\n'):
                # Parsing: hostname (ip) at mac [ether]
                if '(' in line and ')' in line and 'at' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        ip_part = parts[1].strip('()')
                        mac_part = parts[3]
                        if ':' in mac_part and len(mac_part) == 17:
                            arp_table[mac_part.upper()] = ip_part
            
            # Cache ARP
            self.arp_cache['arp_table'] = {
                'data': arp_table,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.debug(f"ARP table error: {e}")
        
        return arp_table
    
    def find_device_by_mac(self, target_mac: str) -> Optional[str]:
        """Trouver l'IP actuelle d'un appareil via sa MAC (gestion DHCP)"""
        if not target_mac:
            return None
            
        arp_table = self.get_arp_table()
        target_mac_clean = target_mac.upper().replace('-', ':')
        
        return arp_table.get(target_mac_clean)
    
    async def ping_by_hostname(self, hostname: str) -> Optional[str]:
        """Ping par hostname et récupérer l'IP résolue"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(self.ping_timeout), hostname,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                # Extraire l'IP de la sortie ping
                output = stdout.decode()
                import re
                ip_match = re.search(r'PING .* \(([0-9.]+)\)', output)
                if ip_match:
                    resolved_ip = ip_match.group(1)
                    logger.debug(f"Hostname {hostname} resolved to {resolved_ip}")
                    return resolved_ip
            return None
        except Exception as e:
            logger.debug(f"Hostname ping error for {hostname}: {e}")
            return None
    
    async def check_device_status(self, device: Dict) -> Dict:
        """
        Vérifier le statut d'un appareil avec gestion DHCP complète
        - Priorité 1: Ping IP configurée
        - Priorité 2: Ping par hostname (si configuré)
        - Priorité 3: Recherche par MAC dans ARP puis ping nouvelle IP
        """
        original_ip = device['ip']
        mac_address = device.get('mac', '')
        hostname = device.get('hostname', '')
        device_name = device.get('name', 'Unknown')
        
        # Vérifier le cache de statut
        cache_key = f"status_{original_ip}_{mac_address}_{hostname}"
        if cache_key in self.status_cache:
            cached_data = self.status_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                return cached_data
        
        status_result = {
            'status': 'offline',
            'current_ip': original_ip,
            'resolved_ip': None,
            'ip_changed': False,
            'method': 'unknown',
            'timestamp': time.time()
        }
        
        # Méthode 1: Ping IP originale
        if await self.quick_ping(original_ip):
            status_result.update({
                'status': 'online',
                'method': 'ping_original_ip'
            })
        
        # Méthode 2: Si offline et hostname disponible, ping par hostname
        elif hostname:
            resolved_ip = await self.ping_by_hostname(hostname)
            if resolved_ip:
                status_result.update({
                    'status': 'online',
                    'current_ip': resolved_ip,
                    'resolved_ip': resolved_ip,
                    'ip_changed': resolved_ip != original_ip,
                    'method': 'hostname_resolution'
                })
                if resolved_ip != original_ip:
                    logger.info(f"Device {device_name} found via hostname: {hostname} → {resolved_ip}")
            else:
                status_result['method'] = 'hostname_no_response'
        
        # Méthode 3: Si toujours offline et MAC disponible, chercher nouvelle IP
        if status_result['status'] == 'offline' and mac_address:
            current_ip = self.find_device_by_mac(mac_address)
            if current_ip and current_ip != original_ip:
                # Nouvelle IP trouvée via MAC, tester ping
                if await self.quick_ping(current_ip):
                    status_result.update({
                        'status': 'online',
                        'current_ip': current_ip,
                        'ip_changed': True,
                        'method': 'mac_lookup_ping'
                    })
                    logger.info(f"Device {device_name} moved: {original_ip} → {current_ip}")
                else:
                    status_result['method'] = 'mac_found_no_ping'
            else:
                if not hostname:  # Seulement si on n'a pas déjà testé le hostname
                    status_result['method'] = 'mac_not_in_arp'
        
        # Si aucune méthode n'a fonctionné et on n'a pas de MAC/hostname
        if status_result['status'] == 'offline' and status_result['method'] == 'unknown':
            status_result['method'] = 'no_fallback_method'
        
        # Mettre en cache
        self.status_cache[cache_key] = status_result
        
        return status_result
    
    async def get_devices_with_status(self, devices: List[Dict]) -> List[Dict]:
        """Enrichir la liste d'appareils avec leur statut actuel"""
        if not devices:
            return []
        
        # Lancer tous les checks en parallèle (rapide)
        tasks = [self.check_device_status(device) for device in devices]
        status_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Enrichir les appareils
        enriched_devices = []
        for i, device in enumerate(devices):
            device_copy = device.copy()
            
            if i < len(status_results) and not isinstance(status_results[i], Exception):
                result = status_results[i]
                device_copy['status'] = result['status']
                device_copy['current_ip'] = result['current_ip']
                device_copy['ip_changed'] = result['ip_changed']
                device_copy['detection_method'] = result['method']
                device_copy['last_checked'] = result['timestamp']
                
                # Mise à jour de l'IP si elle a changé
                if result['ip_changed']:
                    device_copy['previous_ip'] = device['ip']
                    device_copy['ip'] = result['current_ip']
            else:
                # Fallback en cas d'erreur
                device_copy['status'] = 'unknown'
                device_copy['detection_method'] = 'error'
                device_copy['last_checked'] = time.time()
            
            enriched_devices.append(device_copy)
        
        return enriched_devices
    
    def get_monitoring_stats(self) -> Dict:
        """Statistiques du monitoring"""
        return {
            'cached_statuses': len(self.status_cache),
            'arp_cache_age': time.time() - self.arp_cache.get('arp_table', {}).get('timestamp', 0),
            'arp_entries': len(self.arp_cache.get('arp_table', {}).get('data', {}))
        }
    
    def clear_cache(self):
        """Vider tous les caches"""
        self.status_cache.clear()
        self.arp_cache.clear()
        logger.info("Caches de monitoring vidés")

# Instance globale
device_monitor = DeviceMonitor()