"""
🏠 333HOME - ARP Scanner

Scanner ARP cache pour mapping MAC/IP rapide et fiable.
"""

import asyncio
import logging
from datetime import datetime
from typing import List
from src.core.device_intelligence import DeviceData


logger = logging.getLogger(__name__)


class ARPScanner:
    """
    Scanner ARP: Récupère les devices depuis l'ARP cache
    
    Rapide, fiable, ne génère pas de trafic réseau.
    Utilise 'ip neigh show' sur Linux.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.logger = logger
    
    async def scan(self) -> List[DeviceData]:
        """
        Scan ARP cache: MAC/IP mapping rapide et fiable
        
        Command: ip neigh show
        """
        self.logger.info("📡 ARP: Starting...")
        devices = []
        
        try:
            proc = await asyncio.create_subprocess_shell(
                "ip neigh show",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                self.logger.error(f"ARP scan failed: {stderr.decode()}")
                return devices
            
            # Parse output
            # Format: IP dev INTERFACE lladdr MAC REACHABLE/STALE/DELAY
            for line in stdout.decode().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) < 5:
                    continue
                
                ip = parts[0]
                
                # Skip IPv6 addresses (only keep IPv4)
                if ':' in ip and '.' not in ip:
                    continue
                
                # Find MAC (after lladdr)
                try:
                    lladdr_idx = parts.index('lladdr')
                    mac = parts[lladdr_idx + 1]
                except (ValueError, IndexError):
                    continue
                
                # Check if reachable
                is_online = 'REACHABLE' in line or 'DELAY' in line
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    source='arp',
                    is_online=is_online,
                    timestamp=datetime.now(),
                    scan_type='arp_cache'
                )
                devices.append(device)
            
            self.logger.info(f"📡 ARP: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"ARP scan error: {e}")
        
        return devices
