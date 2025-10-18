"""
🔥 SCANNER RÉSEAU ULTRA BLINDÉ - IDENTIFICATION MAXIMALE 🔥
Utilise TOUTES les techniques possibles pour découvrir et identifier les appareils
- API macvendors.com + base JSON locale
- Nmap, Scapy, ping massif, ARP, DNS
- Détection OS, services, ports, fingerprinting
- Classification intelligente par IA-like scoring
"""

import asyncio
import json
import socket
import subprocess
import ipaddress
import re
import time
import platform
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 🚀 IMPORTS ULTRA POUSSÉS
import aiohttp
import nmap
import netifaces
import netaddr
from scapy.all import ARP, Ether, srp, ICMP, IP, sr1, TCP, UDP
from pythonping import ping as py_ping
import dns.resolver
import dns.reversename
from aiocache import Cache
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import paramiko

logger = logging.getLogger(__name__)
console = Console()

@dataclass
class AdvancedNetworkDevice:
    """Modèle ultra complet pour un appareil réseau"""
    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    device_type: str = ""
    os_guess: str = ""
    status: str = "unknown"
    response_time: float = 0.0
    ports_open: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    last_seen: float = field(default_factory=time.time)
    
    # 🔥 NOUVELLES DONNÉES ULTRA POUSSÉES
    nmap_fingerprint: str = ""
    ssh_banner: str = ""
    http_title: str = ""
    dns_names: List[str] = field(default_factory=list)
    netbios_name: str = ""
    uptime: str = ""
    manufacturer_guess: str = ""
    confidence_score: float = 0.0
    scan_techniques_used: List[str] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    
class UltraNetworkScanner:
    """🔥 SCANNER RÉSEAU ULTRA BLINDÉ ET POUSSÉ 🔥"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.vendor_db_path = self.base_path / "data" / "mac_vendors.json"
        self.vendor_cache = {}
        self.api_cache = {}
        self.nmap_scanner = nmap.PortScanner()
        self.console = Console()
        
        # 🗂️ CACHE AVANCÉ
        self.cache = Cache(Cache.MEMORY)
        
        self.load_vendor_database()
        
        # 🎯 PORTS ULTRA COMPLETS PAR CATÉGORIE
        self.critical_ports = {
            # Système & Remote Access
            22: "SSH", 23: "Telnet", 135: "RPC", 139: "NetBIOS-SSN", 445: "SMB",
            3389: "RDP", 5900: "VNC", 5901: "VNC", 5902: "VNC", 5903: "VNC",
            
            # Web & API
            80: "HTTP", 443: "HTTPS", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
            8000: "HTTP-Dev", 8888: "HTTP-Alt2", 9000: "HTTP-Alt3",
            
            # DNS & Network Services  
            53: "DNS", 67: "DHCP", 68: "DHCP-Client", 137: "NetBIOS-NS",
            161: "SNMP", 162: "SNMP-Trap", 514: "Syslog",
            
            # Mail & Communication
            25: "SMTP", 110: "POP3", 143: "IMAP", 993: "IMAPS", 995: "POP3S",
            587: "SMTP-TLS", 465: "SMTPS",
            
            # Media & Streaming
            554: "RTSP", 1935: "RTMP", 5353: "mDNS", 1900: "UPnP",
            
            # Databases
            1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 5432: "PostgreSQL",
            6379: "Redis", 27017: "MongoDB",
            
            # IoT & Smart Home
            1883: "MQTT", 8883: "MQTT-TLS", 502: "Modbus", 102: "S7",
            
            # Printers & Hardware
            9100: "Printer-Raw", 515: "LPD", 631: "IPP",
            
            # Gaming & Entertainment
            7777: "Gaming", 25565: "Minecraft", 19132: "Minecraft-PE",
            
            # Industrial & Special
            44818: "EtherNet/IP", 2404: "IEC-104", 20000: "DNP3"
        }
        
        # 🎭 SIGNATURES ULTRA DÉTAILLÉES
        self.device_signatures = {
            "smartphone": {
                "vendors": ["Apple", "Samsung", "Huawei", "Xiaomi", "OnePlus", "Google", "Oppo", "Vivo"],
                "hostnames": ["iphone", "android", "mobile", "phone", "galaxy", "pixel"],
                "ports": [5353, 62078, 7000],
                "os_hints": ["iOS", "Android"],
                "services": ["bonjour", "airplay"]
            },
            "tablet": {
                "vendors": ["Apple", "Samsung", "Huawei", "Lenovo"],
                "hostnames": ["ipad", "tablet", "tab"],
                "ports": [5353, 7000],
                "os_hints": ["iOS", "Android"]
            },
            "laptop": {
                "vendors": ["Apple", "HP", "Dell", "Lenovo", "Asus", "Acer", "MSI"],
                "hostnames": ["macbook", "laptop", "notebook", "portable"],
                "ports": [22, 135, 445, 5900],
                "os_hints": ["Windows", "macOS", "Linux"]
            },
            "desktop": {
                "vendors": ["HP", "Dell", "Lenovo", "Asus", "Intel", "AMD"],
                "hostnames": ["pc", "desktop", "workstation", "tower"],
                "ports": [135, 445, 3389],
                "os_hints": ["Windows", "Linux"]
            },
            "server": {
                "vendors": ["HP", "Dell", "IBM", "Supermicro", "Intel"],
                "hostnames": ["server", "srv", "node", "host"],
                "ports": [22, 80, 443, 3389, 8080],
                "os_hints": ["Linux", "Windows Server", "ESXi"]
            },
            "router": {
                "vendors": ["Cisco", "Netgear", "D-Link", "TP-Link", "Linksys", "Asus", "Ubiquiti"],
                "hostnames": ["router", "gateway", "firewall", "switch"],
                "ports": [80, 443, 23, 161],
                "services": ["http", "snmp", "upnp"]
            },
            "access_point": {
                "vendors": ["Ubiquiti", "Cisco", "Aruba", "Ruckus"],
                "hostnames": ["ap", "wifi", "wireless", "unifi"],
                "ports": [80, 443, 161, 22],
                "services": ["http", "snmp", "ssh"]
            },
            "printer": {
                "vendors": ["HP", "Canon", "Epson", "Brother", "Xerox", "Lexmark"],
                "hostnames": ["printer", "print", "hp", "canon", "epson"],
                "ports": [9100, 631, 515, 80, 443],
                "services": ["ipp", "lpd", "http"]
            },
            "smart_tv": {
                "vendors": ["Samsung", "LG", "Sony", "Philips", "TCL"],
                "hostnames": ["tv", "smarttv", "android-tv", "webos"],
                "ports": [8080, 1900, 7001, 8001],
                "services": ["upnp", "dlna", "http"]
            },
            "game_console": {
                "vendors": ["Sony", "Microsoft", "Nintendo"],
                "hostnames": ["playstation", "xbox", "ps4", "ps5", "switch"],
                "ports": [80, 443, 9103, 53],
                "services": ["http", "gaming"]
            },
            "raspberry_pi": {
                "vendors": ["Raspberry Pi Foundation", "Raspberry Pi Trading"],
                "hostnames": ["raspberrypi", "rpi", "pi", "raspberry"],
                "ports": [22, 80, 5000, 8080],
                "os_hints": ["Raspbian", "Ubuntu", "Linux"]
            },
            "nas": {
                "vendors": ["Synology", "QNAP", "Western Digital", "Netgear"],
                "hostnames": ["nas", "storage", "synology", "qnap", "diskstation"],
                "ports": [80, 443, 5000, 5001, 8080, 139, 445],
                "services": ["http", "smb", "nfs"]
            },
            "camera": {
                "vendors": ["Hikvision", "Dahua", "Axis", "Ubiquiti"],
                "hostnames": ["camera", "cam", "ipcam", "surveillance"],
                "ports": [80, 554, 8080, 443],
                "services": ["http", "rtsp"]
            },
            "iot_device": {
                "vendors": ["Espressif", "Arduino", "Particle"],
                "hostnames": ["esp", "arduino", "iot", "sensor"],
                "ports": [80, 443, 1883, 8080],
                "services": ["http", "mqtt"]
            }
        }

    def load_vendor_database(self):
        """Charge la base de données locale des vendeurs MAC"""
        try:
            if self.vendor_db_path.exists():
                with open(self.vendor_db_path, 'r', encoding='utf-8') as f:
                    self.vendor_cache = json.load(f)
                logger.info(f"🗂️ Base vendeurs chargée: {len(self.vendor_cache)} entrées")
            else:
                logger.warning("⚠️ Base de données vendeurs non trouvée")
                self.vendor_cache = {}
        except Exception as e:
            logger.error(f"❌ Erreur chargement base vendeurs: {e}")
            self.vendor_cache = {}

    async def get_vendor_from_api(self, mac: str) -> Optional[str]:
        """Récupère le vendeur via l'API macvendors.com avec retry et rate limiting"""
        if not mac or len(mac) < 8:
            return None
            
        cache_key = f"vendor_{mac}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.macvendors.com/{mac}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        vendor = await response.text()
                        vendor = vendor.strip()
                        await self.cache.set(cache_key, vendor, ttl=86400)  # Cache 24h
                        
                        # Mise à jour base locale
                        oui = mac.upper().replace(":", "")[:6]
                        self.vendor_cache[oui] = vendor
                        
                        await asyncio.sleep(0.2)  # Rate limiting strict
                        return vendor
                    elif response.status == 404:
                        await self.cache.set(cache_key, "Unknown", ttl=3600)
                        return "Unknown"
        except Exception as e:
            logger.debug(f"🌐 Erreur API vendeur pour {mac}: {e}")
            
        return None

    def get_vendor_from_local(self, mac: str) -> str:
        """Récupère le vendeur depuis la base locale"""
        if not mac or len(mac) < 8:
            return "Unknown"
            
        oui = mac.upper().replace(":", "")[:6]
        return self.vendor_cache.get(oui, "Unknown")

    async def get_vendor(self, mac: str) -> str:
        """Récupère le vendeur (API + fallback local)"""
        if not mac:
            return "Unknown"
            
        # D'abord l'API
        vendor = await self.get_vendor_from_api(mac)
        if vendor and vendor != "Unknown":
            return vendor
            
        # Fallback local
        return self.get_vendor_from_local(mac)

    async def advanced_ping(self, ip: str) -> Tuple[bool, float, List[str]]:
        """Ping ultra avancé avec multiple techniques"""
        techniques_used = []
        best_time = float('inf')
        is_alive = False
        
        try:
            # 1. Ping Python natif
            result = py_ping(ip, count=1, timeout=2)
            if result.success():
                is_alive = True
                best_time = min(best_time, result.rtt_avg_ms)
                techniques_used.append("python_ping")
        except:
            pass
            
        try:
            # 2. Ping système
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", "2000", ip]
            else:
                cmd = ["ping", "-c", "1", "-W", "2", ip]
                
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            await asyncio.wait_for(process.wait(), timeout=3)
            if process.returncode == 0:
                is_alive = True
                techniques_used.append("system_ping")
        except:
            pass
            
        try:
            # 3. TCP Connect scan sur port commun
            future = asyncio.open_connection(ip, 80)
            reader, writer = await asyncio.wait_for(future, timeout=1)
            writer.close()
            await writer.wait_closed()
            is_alive = True
            techniques_used.append("tcp_connect")
        except:
            pass
            
        return is_alive, best_time if best_time != float('inf') else 0.0, techniques_used

    async def scapy_arp_scan(self, network: str) -> Dict[str, str]:
        """Scan ARP avec Scapy pour découvrir les devices"""
        arp_results = {}
        try:
            # Création du packet ARP
            arp_request = ARP(pdst=network)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            
            # Envoi et réception
            answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
            
            for element in answered_list:
                ip = element[1].psrc
                mac = element[1].hwsrc
                arp_results[ip] = mac.upper()
                
            logger.info(f"🎯 Scapy ARP: {len(arp_results)} devices trouvés")
            
        except Exception as e:
            logger.error(f"❌ Erreur Scapy ARP: {e}")
            
        return arp_results

    async def nmap_discovery(self, network: str) -> List[Dict]:
        """Découverte ultra poussée avec Nmap"""
        devices = []
        try:
            logger.info(f"🔍 Nmap discovery sur {network}")
            
            # Scan de découverte intense
            result = self.nmap_scanner.scan(
                hosts=network,
                arguments='-sn -PE -PP -PS80,443,22 -PA80,443,22 -PU53,67,68,161 --source-port 53 -T4'
            )
            
            for host in self.nmap_scanner.all_hosts():
                if self.nmap_scanner[host].state() == 'up':
                    device_info = {
                        'ip': host,
                        'hostname': self.nmap_scanner[host].hostname(),
                        'nmap_state': self.nmap_scanner[host].state()
                    }
                    devices.append(device_info)
                    
            logger.info(f"🎯 Nmap: {len(devices)} devices UP")
            
        except Exception as e:
            logger.error(f"❌ Erreur Nmap discovery: {e}")
            
        return devices

    async def port_scan_comprehensive(self, ip: str) -> Tuple[List[int], Dict[int, str]]:
        """Scan de ports ultra complet avec identification des services"""
        open_ports = []
        services = {}
        
        try:
            # Scan des ports critiques avec Nmap
            critical_ports_str = ",".join(map(str, self.critical_ports.keys()))
            
            result = self.nmap_scanner.scan(
                ip, 
                critical_ports_str,
                arguments='-sS -sV -O --script=banner,http-title,ssh-hostkey -T4'
            )
            
            if ip in self.nmap_scanner.all_hosts():
                if 'tcp' in self.nmap_scanner[ip]:
                    for port, port_info in self.nmap_scanner[ip]['tcp'].items():
                        if port_info['state'] == 'open':
                            open_ports.append(port)
                            
                            # Service detection
                            service_name = port_info.get('name', 'unknown')
                            service_version = port_info.get('version', '')
                            services[port] = f"{service_name} {service_version}".strip()
                            
        except Exception as e:
            logger.debug(f"🔍 Erreur scan ports {ip}: {e}")
            
        return open_ports, services

    async def get_os_fingerprint(self, ip: str) -> Tuple[str, str]:
        """Détection OS ultra poussée"""
        os_guess = ""
        fingerprint = ""
        
        try:
            # OS Detection avec Nmap
            result = self.nmap_scanner.scan(ip, arguments='-O -sS -T4')
            
            if ip in self.nmap_scanner.all_hosts():
                if 'osmatch' in self.nmap_scanner[ip]:
                    matches = self.nmap_scanner[ip]['osmatch']
                    if matches:
                        best_match = max(matches, key=lambda x: int(x.get('accuracy', 0)))
                        os_guess = best_match.get('name', '')
                        fingerprint = f"Accuracy: {best_match.get('accuracy', 0)}%"
                        
        except Exception as e:
            logger.debug(f"🖥️ Erreur OS detection {ip}: {e}")
            
        return os_guess, fingerprint

    async def banner_grabbing(self, ip: str, ports: List[int]) -> Dict[str, str]:
        """Banner grabbing avancé sur les services"""
        banners = {}
        
        for port in ports[:5]:  # Limite pour éviter de surcharger
            try:
                if port == 22:  # SSH Banner
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        ssh_client.connect(ip, port=22, timeout=3, username='dummy', password='dummy')
                    except:
                        pass
                    transport = ssh_client.get_transport()
                    if transport:
                        banners['ssh'] = transport.remote_version
                    ssh_client.close()
                    
                elif port in [80, 8080, 443, 8443]:  # HTTP Title
                    protocol = 'https' if port in [443, 8443] else 'http'
                    async with aiohttp.ClientSession() as session:
                        try:
                            async with session.get(f"{protocol}://{ip}:{port}", timeout=3, ssl=False) as response:
                                html = await response.text()
                                title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                                if title_match:
                                    banners['http_title'] = title_match.group(1).strip()
                        except:
                            pass
                            
            except Exception as e:
                logger.debug(f"🏷️ Erreur banner {ip}:{port}: {e}")
                
        return banners

    async def dns_resolution_advanced(self, ip: str) -> Tuple[str, List[str]]:
        """Résolution DNS ultra poussée"""
        hostname = ""
        dns_names = []
        
        try:
            # Résolution inverse classique
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                pass
                
            # DNS reverse avec dnspython
            try:
                reversed_dns = dns.reversename.from_address(ip)
                result = dns.resolver.resolve(reversed_dns, "PTR")
                for rdata in result:
                    dns_names.append(str(rdata).rstrip('.'))
            except:
                pass
                
            # mDNS queries si pas de nom trouvé
            if not hostname and not dns_names:
                try:
                    # Tentative de résolution mDNS (port 5353)
                    process = await asyncio.create_subprocess_exec(
                        'nslookup', ip, 
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                    stdout, _ = await process.communicate()
                    if stdout:
                        output = stdout.decode()
                        name_match = re.search(r'name = (.+)', output)
                        if name_match:
                            hostname = name_match.group(1).strip().rstrip('.')
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"🌐 Erreur DNS {ip}: {e}")
            
        return hostname or "", dns_names

    def calculate_confidence_score(self, device: AdvancedNetworkDevice) -> float:
        """Calcule un score de confiance pour l'identification"""
        score = 0.0
        max_score = 100.0
        
        # Score basé sur la présence de données
        if device.mac: score += 15
        if device.hostname: score += 10
        if device.vendor and device.vendor != "Unknown": score += 20
        if device.os_guess: score += 15
        if device.ports_open: score += 10 + min(len(device.ports_open) * 2, 10)
        if device.services: score += 10
        if device.nmap_fingerprint: score += 10
        if device.device_type and device.device_type != "unknown": score += 10
        
        return min(score, max_score)

    def identify_device_type_advanced(self, device: AdvancedNetworkDevice) -> str:
        """Identification ultra poussée du type d'appareil"""
        scores = {}
        vendor = device.vendor.lower()
        hostname = device.hostname.lower()
        os_guess = device.os_guess.lower()
        open_ports = set(device.ports_open)
        services = [s.lower() for s in device.services.values()]
        
        for device_type, signature in self.device_signatures.items():
            score = 0
            
            # Score vendeur (poids fort)
            for sig_vendor in signature.get("vendors", []):
                if sig_vendor.lower() in vendor:
                    score += 25
                    break
                    
            # Score hostname (poids fort)
            for sig_hostname in signature.get("hostnames", []):
                if sig_hostname in hostname:
                    score += 20
                    break
                    
            # Score OS (poids moyen)
            for os_hint in signature.get("os_hints", []):
                if os_hint.lower() in os_guess:
                    score += 15
                    break
                    
            # Score ports (poids moyen)
            sig_ports = set(signature.get("ports", []))
            common_ports = open_ports.intersection(sig_ports)
            score += len(common_ports) * 8
            
            # Score services (poids faible)
            for service_hint in signature.get("services", []):
                if any(service_hint in service for service in services):
                    score += 5
                    
            scores[device_type] = score
            
        # Classification intelligente
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] >= 15:  # Seuil de confiance
                return best_type[0]
                
        # Fallback basé sur des indices simples
        if "phone" in hostname or "mobile" in hostname:
            return "smartphone"
        elif "ipad" in hostname or "tablet" in hostname:
            return "tablet"
        elif any(mobile in vendor for mobile in ["apple", "samsung", "huawei", "xiaomi"]):
            if any(port in open_ports for port in [5353, 62078]):
                return "smartphone"
        elif "raspberry" in vendor.lower():
            return "raspberry_pi"
        elif any(router in vendor for router in ["cisco", "netgear", "d-link", "tp-link"]):
            return "router"
        elif any(printer in vendor for printer in ["hp", "canon", "epson", "brother"]):
            return "printer"
        elif 9100 in open_ports or 631 in open_ports:
            return "printer"
        elif 3389 in open_ports or 135 in open_ports:
            return "desktop"
        elif 22 in open_ports and 80 in open_ports:
            return "server"
            
        return "unknown"

    def get_local_networks_advanced(self) -> List[str]:
        """Détection ultra poussée des réseaux locaux"""
        networks = []
        
        try:
            # Utilise netifaces pour une détection précise
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info.get('addr')
                            netmask = addr_info.get('netmask')
                            
                            if ip and netmask and not ip.startswith('127.'):
                                # Calcul du réseau
                                network = netaddr.IPNetwork(f"{ip}/{netmask}")
                                networks.append(str(network.cidr))
                                
                except Exception as e:
                    logger.debug(f"Interface {interface}: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur détection réseaux avancée: {e}")
            # Fallback classique
            networks = ["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]
            
        # Déduplication et tri
        networks = list(set(networks))
        logger.info(f"🌐 Réseaux détectés: {networks}")
        
        return networks

    async def scan_device_ultra_complete(self, ip: str, arp_data: Dict[str, str]) -> AdvancedNetworkDevice:
        """Scan ultra complet d'un appareil avec TOUTES les techniques"""
        
        with console.status(f"[bold green]🔬 Scan ultra complet de {ip}..."):
            
            # 1. Ping avancé
            is_alive, response_time, ping_techniques = await self.advanced_ping(ip)
            status = "online" if is_alive else "offline"
            
            # 2. Données de base
            mac = arp_data.get(ip, "")
            hostname, dns_names = await self.dns_resolution_advanced(ip)
            
            # 3. Scan de ports et services (seulement si vivant)
            open_ports, services = [], {}
            if is_alive:
                open_ports, services = await self.port_scan_comprehensive(ip)
                
            # 4. Récupération vendeur
            vendor = await self.get_vendor(mac) if mac else "Unknown"
            
            # 5. OS Fingerprinting
            os_guess, nmap_fingerprint = "", ""
            if is_alive and open_ports:
                os_guess, nmap_fingerprint = await self.get_os_fingerprint(ip)
                
            # 6. Banner grabbing
            banners = {}
            if is_alive and open_ports:
                banners = await self.banner_grabbing(ip, open_ports)
                
            # 7. Création du device
            device = AdvancedNetworkDevice(
                ip=ip,
                mac=mac,
                hostname=hostname,
                vendor=vendor,
                status=status,
                response_time=response_time,
                ports_open=open_ports,
                services=services,
                dns_names=dns_names,
                os_guess=os_guess,
                nmap_fingerprint=nmap_fingerprint,
                ssh_banner=banners.get('ssh', ''),
                http_title=banners.get('http_title', ''),
                scan_techniques_used=ping_techniques + ['nmap', 'banner_grab']
            )
            
            # 8. Identification du type
            device.device_type = self.identify_device_type_advanced(device)
            
            # 9. Score de confiance
            device.confidence_score = self.calculate_confidence_score(device)
            
            return device

    def discovery_multi_technique_sync(self, networks: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """Version synchrone simplifiée de la découverte multi-technique"""
        all_ips = set()
        all_arp_data = {}
        
        with Progress(
            TextColumn("[bold green]🔍 Discovery"),
            BarColumn(),
            TextColumn("[green]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Scan networks", total=len(networks))
            
            for network in networks:
                try:
                    # Scan ping simple avec nmap
                    import subprocess
                    result = subprocess.run(
                        ["nmap", "-sn", network], 
                        capture_output=True, 
                        text=True, 
                        timeout=30
                    )
                    
                    # Extraction des IPs
                    for line in result.stdout.split('\n'):
                        if "Nmap scan report for" in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                ip = parts[-1].strip('()')
                                all_ips.add(ip)
                
                    # ARP scan complémentaire
                    try:
                        arp_result = subprocess.run(
                            ["arp-scan", "-l"], 
                            capture_output=True, 
                            text=True, 
                            timeout=10
                        )
                        for line in arp_result.stdout.split('\n'):
                            parts = line.split()
                            if len(parts) >= 2 and parts[0].count('.') == 3:
                                ip, mac = parts[0], parts[1]
                                all_ips.add(ip)
                                all_arp_data[ip] = mac
                    except:
                        pass
                        
                except Exception as e:
                    console.print(f"❌ Erreur réseau {network}: {e}")
                
                progress.update(task, advance=1)
        
        return list(all_ips), all_arp_data

    async def discovery_multi_technique(self, networks: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """Découverte multi-technique ultra poussée"""
        all_ips = set()
        all_arp_data = {}
        
        with Progress(
            TextColumn("[bold blue]🔍 Discovery"),
            BarColumn(),
            TextColumn("[green]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Scan networks", total=len(networks))
            
            for network in networks:
                logger.info(f"🌐 Multi-technique discovery: {network}")
                
                # 1. Scapy ARP Discovery
                try:
                    arp_results = await self.scapy_arp_scan(network)
                    all_arp_data.update(arp_results)
                    all_ips.update(arp_results.keys())
                except Exception as e:
                    logger.debug(f"Scapy ARP failed: {e}")
                
                # 2. Nmap Discovery
                try:
                    nmap_devices = await self.nmap_discovery(network)
                    for device in nmap_devices:
                        all_ips.add(device['ip'])
                except Exception as e:
                    logger.debug(f"Nmap discovery failed: {e}")
                
                # 3. Ping Sweep rapide des IPs manquantes
                try:
                    net = ipaddress.IPv4Network(network, strict=False)
                    if net.num_addresses <= 256:  # Seulement pour les petits réseaux
                        ping_tasks = []
                        for ip in net.hosts():
                            ip_str = str(ip)
                            if ip_str not in all_ips:
                                ping_tasks.append(self.advanced_ping(ip_str))
                        
                        if ping_tasks:
                            ping_results = await asyncio.gather(*ping_tasks[:50], return_exceptions=True)
                            for i, result in enumerate(ping_results):
                                if isinstance(result, tuple) and result[0]:  # is_alive = True
                                    ip_str = str(list(net.hosts())[i])
                                    all_ips.add(ip_str)
                except Exception as e:
                    logger.debug(f"Ping sweep failed: {e}")
                    
                progress.advance(task)
                
        logger.info(f"🎯 Discovery terminée: {len(all_ips)} IPs actives, {len(all_arp_data)} MACs")
        return list(all_ips), all_arp_data

    def scan_network_ultra_blindé_sync(self, target_networks: Optional[List[str]] = None) -> List[AdvancedNetworkDevice]:
        """
        🔥 VERSION SYNCHRONE - SCAN RÉSEAU ULTRA BLINDÉ 🔥
        Pour l'utilisation dans les API et les contextes synchrones
        """
        logger.info("🔥 Démarrage Scanner ULTRA BLINDÉ (version sync)")
        start_time = time.time()
        
        # Détermine les réseaux
        if not target_networks:
            target_networks = self.get_local_networks_advanced()
        
        logger.info(f"📡 Réseaux cibles: {target_networks}")
        
        # PHASE 1: DISCOVERY MULTI-TECHNIQUE (sync)
        active_ips, arp_data = self.discovery_multi_technique_sync(target_networks)
        logger.info(f"📱 {len(active_ips)} appareils actifs détectés")
        
        # PHASE 2: ANALYSE SIMPLIFIÉE POUR SYNC
        devices = []
        
        for i, ip in enumerate(active_ips, 1):
            try:
                logger.info(f"🔬 Analyse {i}/{len(active_ips)}: {ip}")
                
                # Création de l'appareil avec les données disponibles
                device = AdvancedNetworkDevice(
                    ip=ip,
                    hostname=self.get_hostname_safe(ip),
                    mac=arp_data.get(ip, ""),
                    status="online"
                )
                
                # Tentative d'identification du vendeur si MAC disponible
                if device.mac and device.mac in self.mac_vendors:
                    device.vendor = self.mac_vendors[device.mac]
                elif device.mac:
                    # Extraction du OUI (3 premiers octets)
                    oui = device.mac.upper().replace(":", "")[:6]
                    if oui in self.mac_vendors:
                        device.vendor = self.mac_vendors[oui]
                
                # Type basique basé sur l'IP
                if ip.endswith('.1') or ip.endswith('.254'):
                    device.device_type = "router"
                elif device.vendor and any(x in device.vendor.lower() for x in ['apple', 'iphone', 'android']):
                    device.device_type = "mobile"
                else:
                    device.device_type = "computer"
                
                devices.append(device)
                
            except Exception as e:
                logger.warning(f"❌ Erreur analyse {ip}: {e}")
                continue
        
        duration = time.time() - start_time
        logger.info(f"✅ Scan ultra synchrone terminé: {len(devices)} appareils en {duration:.1f}s")
        
        return devices

    async def scan_network_ultra_blindé(self, target_networks: Optional[List[str]] = None) -> List[AdvancedNetworkDevice]:
        """
        🔥 SCAN RÉSEAU ULTRA BLINDÉ - DÉCOUVRE ET IDENTIFIE TOUT 🔥
        """
        console.print(Panel.fit("🔥 [bold red]SCANNER RÉSEAU ULTRA BLINDÉ[/bold red] 🔥", border_style="red"))
        start_time = time.time()
        
        # Détermine les réseaux
        if not target_networks:
            target_networks = self.get_local_networks_advanced()
        
        console.print(f"📡 [bold cyan]Réseaux cibles:[/bold cyan] {target_networks}")
        
        # 🎯 PHASE 1: DISCOVERY MULTI-TECHNIQUE
        active_ips, arp_data = self.discovery_multi_technique_sync(target_networks)
        
        console.print(f"📱 [bold green]{len(active_ips)} appareils actifs détectés[/bold green]")
        
        # 🔬 PHASE 2: ANALYSE ULTRA COMPLÈTE
        devices = []
        
        with Progress(
            TextColumn("[bold green]🔬 Analyse"),
            BarColumn(),
            TextColumn("[green]{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Scan devices", total=len(active_ips))
            
            # Limitation de la concurrence pour éviter de surcharger
            semaphore = asyncio.Semaphore(10)
            
            async def scan_with_semaphore(ip):
                async with semaphore:
                    result = await self.scan_device_ultra_complete(ip, arp_data)
                    progress.advance(task)
                    return result
            
            tasks = [scan_with_semaphore(ip) for ip in active_ips]
            devices = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrage des erreurs
        valid_devices = [d for d in devices if isinstance(d, AdvancedNetworkDevice)]
        
        # Tri par IP
        valid_devices.sort(key=lambda d: ipaddress.IPv4Address(d.ip))
        
        scan_time = time.time() - start_time
        
        # 📊 STATISTIQUES FINALES
        stats_table = Table(title="📊 Résultats du Scan Ultra Blindé")
        stats_table.add_column("Métrique", style="cyan")
        stats_table.add_column("Valeur", style="green")
        
        stats_table.add_row("🕐 Temps de scan", f"{scan_time:.2f}s")
        stats_table.add_row("📱 Appareils trouvés", str(len(valid_devices)))
        stats_table.add_row("🔗 Adresses MAC", str(len([d for d in valid_devices if d.mac])))
        stats_table.add_row("✅ Appareils en ligne", str(len([d for d in valid_devices if d.status == "online"])))
        
        # Stats par type
        type_stats = {}
        for device in valid_devices:
            type_stats[device.device_type] = type_stats.get(device.device_type, 0) + 1
        
        for device_type, count in type_stats.items():
            stats_table.add_row(f"📱 {device_type}", str(count))
            
        console.print(stats_table)
        
        logger.info(f"🔥 SCAN ULTRA BLINDÉ TERMINÉ: {len(valid_devices)} appareils en {scan_time:.2f}s")
        
        return valid_devices

    async def scan_live_ultra(self) -> Dict:
        """Point d'entrée API pour le scan ultra blindé"""
        try:
            devices = await self.scan_network_ultra_blindé()
            
            # Conversion en dictionnaire pour l'API
            devices_data = [asdict(device) for device in devices]
            
            # Statistiques ultra détaillées
            stats = {
                "total_devices": len(devices),
                "online_devices": len([d for d in devices if d.status == "online"]),
                "with_mac": len([d for d in devices if d.mac]),
                "identified_vendor": len([d for d in devices if d.vendor != "Unknown"]),
                "device_types": {},
                "vendors": {},
                "os_detected": {},
                "avg_confidence": sum(d.confidence_score for d in devices) / len(devices) if devices else 0,
                "techniques_used": list(set(sum([d.scan_techniques_used for d in devices], [])))
            }
            
            for device in devices:
                # Stats par type
                device_type = device.device_type
                stats["device_types"][device_type] = stats["device_types"].get(device_type, 0) + 1
                
                # Stats par vendeur
                vendor = device.vendor
                if vendor and vendor != "Unknown":
                    stats["vendors"][vendor] = stats["vendors"].get(vendor, 0) + 1
                    
                # Stats par OS
                if device.os_guess:
                    stats["os_detected"][device.os_guess] = stats["os_detected"].get(device.os_guess, 0) + 1
            
            return {
                "success": True,
                "devices": devices_data,
                "stats": stats,
                "scan_time": time.time(),
                "message": f"🔥 Scan ultra blindé terminé: {len(devices)} appareils analysés"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur scan ultra blindé: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "devices": [],
                "stats": {},
                "message": "❌ Erreur lors du scan ultra blindé"
            }

# 🔥 INSTANCE GLOBALE ULTRA BLINDÉE
ultra_scanner = UltraNetworkScanner()