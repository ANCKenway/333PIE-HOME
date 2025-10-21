"""
🔍 333HOME - Port Scanner
Scanner de ports et détection de services

Fonctionnalités:
- Scan ports communs (async)
- Détection services (SSH, HTTP, RDP, VNC, etc.)
- Banner grabbing pour identification
- Timeout configurable
"""

import asyncio
import socket
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


# === PORTS COMMUNS ===

COMMON_PORTS = {
    # SSH & Remote Access
    22: {"name": "SSH", "service": "ssh", "icon": "🔐"},
    23: {"name": "Telnet", "service": "telnet", "icon": "📟"},
    3389: {"name": "RDP", "service": "rdp", "icon": "🖥️"},
    5900: {"name": "VNC", "service": "vnc", "icon": "👁️"},
    
    # Web
    80: {"name": "HTTP", "service": "http", "icon": "🌐"},
    443: {"name": "HTTPS", "service": "https", "icon": "🔒"},
    8080: {"name": "HTTP-Alt", "service": "http", "icon": "🌐"},
    8443: {"name": "HTTPS-Alt", "service": "https", "icon": "🔒"},
    9090: {"name": "Web-Admin", "service": "admin", "icon": "⚙️"},
    
    # File Sharing
    21: {"name": "FTP", "service": "ftp", "icon": "📁"},
    139: {"name": "NetBIOS", "service": "smb", "icon": "📂"},
    445: {"name": "SMB", "service": "smb", "icon": "📂"},
    548: {"name": "AFP", "service": "afp", "icon": "🍎"},
    2049: {"name": "NFS", "service": "nfs", "icon": "📁"},
    
    # Database
    3306: {"name": "MySQL", "service": "mysql", "icon": "🗄️"},
    5432: {"name": "PostgreSQL", "service": "postgresql", "icon": "🗄️"},
    27017: {"name": "MongoDB", "service": "mongodb", "icon": "🗄️"},
    6379: {"name": "Redis", "service": "redis", "icon": "💾"},
    
    # Email
    25: {"name": "SMTP", "service": "smtp", "icon": "📧"},
    110: {"name": "POP3", "service": "pop3", "icon": "📧"},
    143: {"name": "IMAP", "service": "imap", "icon": "📧"},
    587: {"name": "SMTP-TLS", "service": "smtp", "icon": "📧"},
    
    # IoT & Smart Home
    1883: {"name": "MQTT", "service": "mqtt", "icon": "🏠"},
    8883: {"name": "MQTT-TLS", "service": "mqtt", "icon": "🏠"},
    5353: {"name": "mDNS", "service": "mdns", "icon": "🔍"},
    
    # Media
    554: {"name": "RTSP", "service": "rtsp", "icon": "📹"},
    8554: {"name": "RTSP-Alt", "service": "rtsp", "icon": "📹"},
    32400: {"name": "Plex", "service": "plex", "icon": "🎬"},
    
    # Gaming
    25565: {"name": "Minecraft", "service": "minecraft", "icon": "🎮"},
    27015: {"name": "Steam", "service": "steam", "icon": "🎮"},
    
    # Printing
    631: {"name": "IPP", "service": "ipp", "icon": "🖨️"},
    9100: {"name": "JetDirect", "service": "printer", "icon": "🖨️"},
}


class PortScanner:
    """Scanner de ports asynchrone"""
    
    def __init__(self, timeout: float = 1.0):
        """
        Initialise le scanner
        
        Args:
            timeout: Timeout en secondes par port
        """
        self.timeout = timeout
    
    async def _check_port(
        self,
        ip: str,
        port: int,
    ) -> Optional[Dict]:
        """
        Vérifie si un port est ouvert
        
        Args:
            ip: Adresse IP
            port: Numéro de port
            
        Returns:
            Dict avec infos si ouvert, None sinon
        """
        try:
            # Tentative de connexion
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=self.timeout
            )
            
            # Port ouvert
            port_info = COMMON_PORTS.get(port, {
                "name": f"Port {port}",
                "service": "unknown",
                "icon": "❓"
            })
            
            # Banner grabbing (optionnel)
            banner = None
            try:
                # Lire les premières données (timeout court)
                data = await asyncio.wait_for(
                    reader.read(256),
                    timeout=0.5
                )
                banner = data.decode('utf-8', errors='ignore').strip()
            except:
                pass
            
            # Fermer la connexion
            writer.close()
            await writer.wait_closed()
            
            result = {
                "port": port,
                "state": "open",
                "service": port_info["service"],
                "name": port_info["name"],
                "icon": port_info["icon"],
            }
            
            if banner:
                result["banner"] = banner[:100]  # Limiter la longueur
            
            return result
        
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Port fermé ou timeout
            return None
        
        except Exception as e:
            logger.debug(f"Error checking {ip}:{port}: {e}")
            return None
    
    async def scan_host(
        self,
        ip: str,
        ports: Optional[List[int]] = None,
    ) -> List[Dict]:
        """
        Scan tous les ports d'un host
        
        Args:
            ip: Adresse IP
            ports: Liste de ports (si None, scan ports communs)
            
        Returns:
            Liste des ports ouverts avec infos
        """
        if ports is None:
            # Ports communs par défaut
            ports = list(COMMON_PORTS.keys())
        
        logger.debug(f"🔍 Scanning {len(ports)} ports on {ip}...")
        
        # Scanner tous les ports en parallèle
        tasks = [self._check_port(ip, port) for port in ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les ports ouverts
        open_ports = [r for r in results if r and isinstance(r, dict)]
        
        if open_ports:
            logger.info(
                f"✅ {ip}: {len(open_ports)} port(s) open - "
                f"{', '.join(str(p['port']) for p in open_ports)}"
            )
        
        return open_ports
    
    async def scan_multiple_hosts(
        self,
        ips: List[str],
        ports: Optional[List[int]] = None,
    ) -> Dict[str, List[Dict]]:
        """
        Scan plusieurs hosts
        
        Args:
            ips: Liste d'IPs
            ports: Liste de ports
            
        Returns:
            Dict {ip: [ports ouverts]}
        """
        logger.info(f"🔍 Port scanning {len(ips)} hosts...")
        
        tasks = [self.scan_host(ip, ports) for ip in ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Créer le dict résultat
        scan_results = {}
        for ip, result in zip(ips, results):
            if isinstance(result, list):
                scan_results[ip] = result
            else:
                scan_results[ip] = []
        
        total_open = sum(len(ports) for ports in scan_results.values())
        logger.info(f"✅ Port scan complete: {total_open} open ports found")
        
        return scan_results
    
    def identify_device_role(self, open_ports: List[Dict]) -> Dict:
        """
        Identifie le rôle d'un appareil basé sur ses ports
        
        Args:
            open_ports: Liste des ports ouverts
            
        Returns:
            Dict avec role, confidence, services
        """
        if not open_ports:
            return {
                "role": "unknown",
                "confidence": "low",
                "services": [],
            }
        
        services = [p["service"] for p in open_ports]
        ports_nums = [p["port"] for p in open_ports]
        
        # Détection par patterns
        roles = []
        
        # Web Server
        if any(s in services for s in ["http", "https"]):
            roles.append(("web_server", 0.8))
        
        # Database Server
        if any(s in services for s in ["mysql", "postgresql", "mongodb", "redis"]):
            roles.append(("database_server", 0.9))
        
        # File Server
        if any(s in services for s in ["smb", "nfs", "afp", "ftp"]):
            roles.append(("file_server", 0.85))
        
        # Media Server
        if "plex" in services or "rtsp" in services:
            roles.append(("media_server", 0.9))
        
        # IoT Device
        if "mqtt" in services:
            roles.append(("iot_device", 0.8))
        
        # Printer
        if any(s in services for s in ["ipp", "printer"]):
            roles.append(("printer", 0.95))
        
        # Router/Gateway
        if len(services) >= 5 and any(s in services for s in ["http", "ssh", "telnet"]):
            roles.append(("router", 0.7))
        
        # Desktop/Server
        if "rdp" in services or "vnc" in services:
            roles.append(("desktop", 0.8))
        
        # Gaming Server
        if any(s in services for s in ["minecraft", "steam"]):
            roles.append(("gaming_server", 0.9))
        
        # Déterminer le meilleur rôle
        if roles:
            best_role, confidence = max(roles, key=lambda x: x[1])
            confidence_level = "high" if confidence >= 0.8 else "medium"
        else:
            best_role = "generic_device"
            confidence_level = "low"
        
        return {
            "role": best_role,
            "confidence": confidence_level,
            "services": list(set(services)),
            "open_ports": len(open_ports),
        }


# === QUICK SCAN PRESETS ===

SCAN_PRESETS = {
    "quick": [22, 80, 443, 3389, 5900],  # 5 ports essentiels
    "common": list(COMMON_PORTS.keys()),  # Tous les ports communs (35+)
    "web": [80, 443, 8080, 8443, 9090],  # Web services
    "remote": [22, 23, 3389, 5900],  # Remote access
    "file": [21, 139, 445, 548, 2049],  # File sharing
    "database": [3306, 5432, 27017, 6379],  # Databases
    "iot": [1883, 8883, 5353],  # IoT/Smart Home
}


def get_scan_preset(preset_name: str) -> List[int]:
    """Récupère un preset de scan"""
    return SCAN_PRESETS.get(preset_name, SCAN_PRESETS["common"])
