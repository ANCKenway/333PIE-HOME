"""
🏠 333HOME - mDNS Scanner

Scanner mDNS pour discovery de hostnames .local (Apple, Linux).
Utilise avahi-browse.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from src.core.device_intelligence import DeviceData


logger = logging.getLogger(__name__)


class MDNSScanner:
    """
    Scanner mDNS: Service discovery pour hostnames .local
    
    Utilise avahi-browse pour détecter les devices Apple/Linux.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.logger = logger
    
    async def scan(self) -> List[DeviceData]:
        """
        Scan mDNS: Service discovery pour hostnames .local
        
        Uses avahi-browse if available
        """
        self.logger.info("📡 mDNS: Starting...")
        devices = []
        
        try:
            # Check if avahi-browse is available
            check = await asyncio.create_subprocess_shell(
                "which avahi-browse",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            
            if check.returncode != 0:
                self.logger.warning("mDNS: avahi-browse not found, skipping")
                return devices
            
            # Scan for all services
            proc = await asyncio.create_subprocess_shell(
                "avahi-browse -a -t -r -p",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            except asyncio.TimeoutError:
                proc.kill()
                self.logger.warning("mDNS: Timeout after 5s")
                return devices
            
            # Parse output
            seen_macs = set()
            for line in stdout.decode().split('\n'):
                if not line.startswith('='):
                    continue
                
                parts = line.split(';')
                if len(parts) < 8:
                    continue
                
                hostname = parts[6] if len(parts) > 6 else None
                ip = parts[7] if len(parts) > 7 else None
                
                if not hostname or not ip:
                    continue
                
                # Get MAC from ARP
                mac = await self._get_mac_for_ip(ip)
                if not mac or mac in seen_macs:
                    continue
                
                seen_macs.add(mac)
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    source='mdns',
                    is_online=True,
                    timestamp=datetime.now(),
                    scan_type='mdns_discovery'
                )
                devices.append(device)
            
            self.logger.info(f"📡 mDNS: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"mDNS scan error: {e}")
        
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
            
            import re
            output = stdout.decode()
            match = re.search(r'lladdr\s+([0-9a-fA-F:]+)', output)
            if match:
                return match.group(1)
        except:
            pass
        return None
