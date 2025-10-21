"""
🏠 333HOME - NetBIOS Scanner

Scanner NetBIOS pour résolution de noms Windows.
Utilise nbtscan pour détecter les hostnames Windows.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import List, Optional
from src.core.device_intelligence import DeviceData


logger = logging.getLogger(__name__)


class NetBIOSScanner:
    """
    Scanner NetBIOS: Windows name resolution
    
    Utilise nbtscan pour détecter les hostnames Windows sur le réseau.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.logger = logger
    
    async def scan(self) -> List[DeviceData]:
        """
        Scan NetBIOS: Windows name resolution
        
        Uses nbtscan if available
        """
        self.logger.info("📡 NetBIOS: Starting...")
        devices = []
        
        try:
            # Check if nbtscan is available
            check = await asyncio.create_subprocess_shell(
                "which nbtscan",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            
            if check.returncode != 0:
                self.logger.warning("NetBIOS: nbtscan not found, skipping")
                return devices
            
            # Scan subnet (⚠️ sudo requis pour bind socket)
            proc = await asyncio.create_subprocess_shell(
                f"sudo nbtscan -r {self.subnet}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # Parse output
            # Format: IP    NetBIOS_Name    Server    User    MAC
            for line in stdout.decode().split('\n'):
                if not line.strip() or line.startswith('Doing'):
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                ip = parts[0]
                hostname = parts[1]
                
                # Try to extract MAC from end of line
                mac_match = re.search(
                    r'([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})',
                    line
                )
                if not mac_match:
                    # Fallback: get MAC from ARP
                    mac = await self._get_mac_for_ip(ip)
                    if not mac:
                        continue
                else:
                    mac = mac_match.group(1)
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    source='netbios',
                    is_online=True,
                    timestamp=datetime.now(),
                    scan_type='netbios_scan'
                )
                devices.append(device)
            
            self.logger.info(f"📡 NetBIOS: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"NetBIOS scan error: {e}")
        
        return devices
    
    async def _get_mac_for_ip(self, ip: str) -> Optional[str]:
        """Helper: Get MAC from ARP cache"""
        try:
            proc = await asyncio.create_subprocess_shell(
                f"ip neigh show {ip}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            output = stdout.decode()
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', output)
            if match:
                return match.group(1)
        except:
            pass
        return None
