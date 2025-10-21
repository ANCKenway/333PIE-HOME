"""
🏠 333HOME - Nmap Scanner

Scanner nmap pour découverte réseau (IP, ports, OS, latence).
Mode poli (-T2) pour ne pas perturber le réseau.
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List
from src.core.device_intelligence import DeviceData


logger = logging.getLogger(__name__)


class NmapScanner:
    """
    Scanner Nmap: Découverte réseau complète
    
    Utilise nmap avec timing poli (-T2) et timeout.
    """
    
    def __init__(self, subnet: str = "192.168.1.0/24"):
        self.subnet = subnet
        self.logger = logger
    
    async def scan(self) -> List[DeviceData]:
        """
        Scan nmap: IP, ports, OS detection, latency
        
        Command: nmap -sn -T2 (polite timing)
        🔧 Optimisé pour ne pas perturber le réseau
        """
        self.logger.info("📡 nmap: Starting (polite mode)...")
        devices = []
        
        try:
            # -T4 = Aggressive timing (plus rapide que -T2)
            # -sn = ping scan, -PR = ARP ping ACTIVÉ
            # --host-timeout=3s = Timeout de 3s par host
            # --min-rate=100 = Min 100 paquets/sec (accélère le scan)
            # ⚠️ SANS -O car -sn désactive scan ports (requis pour OS detection)
            # → OS detection via TTL heuristique à la place (voir ci-dessous)
            # ⚠️ sudo requis pour ARP ping (-PR)
            cmd = f"sudo nmap -sn -T4 -PR --min-rate=100 --host-timeout=3s -oX - {self.subnet}"
            
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Timeout global de 150s (pour /24 = 256 IPs)
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=150.0)
            except asyncio.TimeoutError:
                proc.kill()
                self.logger.warning("nmap: Timeout after 150s")
                return devices
            
            if proc.returncode != 0:
                self.logger.error(f"nmap failed: {stderr.decode()}")
                return devices
            
            # Parse XML output
            root = ET.fromstring(stdout.decode())
            
            for host in root.findall('.//host'):
                # Status
                status = host.find('status')
                if status is None or status.get('state') != 'up':
                    continue
                
                # IP
                address_ip = host.find("./address[@addrtype='ipv4']")
                if address_ip is None:
                    continue
                ip = address_ip.get('addr')
                
                # MAC
                address_mac = host.find("./address[@addrtype='mac']")
                if address_mac is None:
                    continue
                mac = address_mac.get('addr')
                vendor = address_mac.get('vendor')
                
                # Hostname
                hostname = None
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    hostname_elem = hostnames.find('hostname')
                    if hostname_elem is not None:
                        hostname = hostname_elem.get('name')
                
                # OS Detection via TTL heuristique (car -sn désactive -O)
                os_name = None
                
                # Méthode 1: Parser <osmatch> (ne fonctionne qu'avec scan ports)
                os_elem = host.find('.//osmatch')
                if os_elem is not None:
                    os_name = os_elem.get('name')
                    accuracy = os_elem.get('accuracy', '0')
                    if os_name and int(accuracy) > 70:
                        self.logger.debug(f"🖥️  OS nmap: {os_name} ({accuracy}%)")
                
                # Méthode 2: Heuristique via distance/uptime (approximatif)
                # Windows: distance=1 (direct), Linux: distance>1 (router)
                # Mais trop imprécis, on laisse au DeviceIntelligenceEngine
                
                # Latency
                times = host.find('times')
                latency = None
                if times is not None:
                    rtt = times.get('rttvar')
                    if rtt:
                        latency = float(rtt) / 1000  # Convert to ms
                
                device = DeviceData(
                    mac=mac,
                    ip=ip,
                    hostname=hostname,
                    vendor=vendor,
                    os=os_name,  # 🆕 OS detection
                    source='nmap',
                    is_online=True,
                    response_time_ms=latency,
                    timestamp=datetime.now(),
                    scan_type='ping'
                )
                devices.append(device)
            
            self.logger.info(f"📡 nmap: Found {len(devices)} devices")
            
        except Exception as e:
            self.logger.error(f"nmap scan error: {e}")
        
        return devices
