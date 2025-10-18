"""
Service de scan réseau simplifié et efficace
Fonctionnalités : découverte d'appareils, identification par hostname
"""

import subprocess
import socket
import json
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

class NetworkScanner:
    """Scanner réseau optimisé avec cache intelligent"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes de cache
        self.last_full_scan = 0
        self.network_range = "192.168.1.0/24"
        import time
        self.time = time
        
        # Configuration des timeouts OPTIMISÉS pour vitesse maximale
        self.timeouts = {
            'dns_lookup': 0.3,      # DNS ultra-rapide
            'nmap_host': 1,         # Host discovery très rapide
            'nmap_ports': 3,        # Scan ports plus rapide
            'ping': 0.5,            # Ping ultra-rapide
            'arp': 0.5,             # ARP ultra-rapide
            'netbios': 1.5,         # NetBIOS rapide mais efficace
            'mdns': 1,              # mDNS rapide
            'upnp': 2,              # UPnP un peu plus long mais utile
            'socket': 0.3,          # Socket très rapide
            'avahi': 2              # mDNS modéré
        }
    
    def quick_discover(self) -> List[Dict]:
        """Scan rapide du réseau local"""
        devices = []
        network = ipaddress.IPv4Network(self.network_range, strict=False)
        
        # Scan parallèle des IPs avec plus de workers pour vitesse maximale
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(self._scan_device_simple, str(ip)): str(ip) 
                for ip in network.hosts()
            }
            
            for future in as_completed(futures):
                device = future.result()
                if device:
                    devices.append(device)
        
        return sorted(devices, key=lambda x: ipaddress.IPv4Address(x['ip']))
    
    def _scan_device_simple(self, ip: str) -> Dict:
        """Scan SIMPLE et EFFICACE d'un appareil - une méthode à la fois"""
        try:
            # 1. Récupérer le hostname - méthodes testées une par une
            hostname = self._get_hostname_simple(ip)
            
            # 2. Récupérer l'adresse MAC
            mac = self._get_mac_address(ip)
            
            # 3. Déterminer le vendor depuis MAC
            vendor = self._get_vendor_from_mac(mac)
            
            # 4. Détecter le type d'appareil
            device_type = self._detect_device_type_simple(hostname, mac, vendor)
            
            # 5. Description claire
            description = self._get_description_simple(device_type, vendor, hostname)
            
            return {
                'ip': ip,
                'hostname': hostname,
                'mac': mac,
                'vendor': vendor,
                'device_type': device_type,
                'description': description,
                'status': 'online'
            }
        except Exception as e:
            print(f"❌ Erreur scan {ip}: {e}")
            return None
    
    def _detect_device_type_simple(self, hostname: str, mac: str, vendor: str) -> str:
        """Détection simple du type d'appareil"""
        hostname_lower = hostname.lower() if hostname else ""
        vendor_lower = vendor.lower() if vendor else ""
        
        # Windows PC
        if any(term in hostname_lower for term in ['pc', 'desktop', 'windows', 'win']) or \
           (hostname and len(hostname) < 15 and hostname.isalnum()):
            return "Windows PC"
            
        # Mac/Apple
        if "apple" in vendor_lower or any(term in hostname_lower for term in ['macbook', 'imac', 'mac']):
            return "Mac"
            
        # Mobile devices
        if any(term in hostname_lower for term in ['iphone', 'android', 'samsung', 'phone']):
            return "Mobile"
            
        # IoT/Smart devices  
        if any(term in hostname_lower for term in ['iot', 'smart', 'alexa', 'google']):
            return "Smart Device"
            
        # Serveurs
        if any(term in hostname_lower for term in ['server', 'srv', 'nas']):
            return "Server"
            
        # Router/Network
        if any(term in hostname_lower for term in ['router', 'gateway', 'access']):
            return "Network"
            
        # Default basé sur vendor
        if "intel" in vendor_lower:
            return "PC"
        elif "apple" in vendor_lower:
            return "Apple Device"
        elif vendor != "Unknown":
            return f"{vendor} Device"
            
        return "Unknown Device"
        
    def _get_description_simple(self, device_type: str, vendor: str, hostname: str) -> str:
        """Description simple et claire"""
        if hostname and hostname != "unknown" and not hostname.startswith("Appareil-"):
            return f"{device_type} ({hostname})"
        elif vendor and vendor != "Unknown":
            return f"{device_type} - {vendor}"
        else:
            return device_type
    
    def _scan_ip(self, ip: str) -> Dict:
        """Scanne une IP spécifique et retourne les informations complètes de l'appareil"""
        hostname = self._get_hostname(ip)
        mac = self._get_mac_address(ip)
        vendor = self._get_vendor_from_mac(mac)
        device_type = self._detect_device_type(hostname, mac, ip)
        description = self._get_device_description(device_type, vendor, hostname)
        
        return {
            'ip': ip,
            'hostname': hostname,
            'mac': mac,
            'vendor': vendor,
            'device_type': device_type,
            'description': description,
            'status': 'online'
        }
    

    
    def _ping_host(self, ip: str) -> bool:
        """Ping ULTRA-RAPIDE optimisé"""
        try:
            # Ping avec timeout ultra-court pour vitesse maximale
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "500", ip],  # 500ms timeout
                capture_output=True,
                timeout=self.timeouts['ping']
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_hostname_simple(self, ip: str) -> str:
        """Hostname simple - DNS puis NetBIOS puis mDNS puis nmap"""
        # 1. DNS d'abord 
        hostname = self._try_dns_simple(ip)
        if hostname != "unknown":
            return hostname
            
        # 2. NetBIOS pour Windows
        hostname = self._try_netbios_simple(ip) 
        if hostname != "unknown":
            return hostname
            
        # 3. mDNS pour Mac/iOS
        hostname = self._try_mdns_simple(ip)
        if hostname != "unknown":
            return hostname
            
        # 4. nmap en dernier recours
        hostname = self._try_nmap_hostname_simple(ip)
        if hostname != "unknown":
            return hostname
            
        return f"Appareil-{ip.split('.')[-1]}"
        
    def _try_dns_simple(self, ip: str) -> str:
        """DNS reverse simple"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname and hostname != ip and not hostname.startswith('192.168'):
                return hostname
        except:
            pass
        return "unknown"
    
    def _get_mac_address(self, ip: str) -> str:
        """Récupération avancée adresse MAC"""
        
        # 1. Table ARP standard
        try:
            result = subprocess.run(
                ["arp", "-n", ip],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.lower()
        except:
            pass
        
        # 2. Ping puis ARP (force l'entrée ARP)
        try:
            subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True,
                timeout=2
            )
            
            result = subprocess.run(
                ["arp", "-n", ip],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            for line in result.stdout.split('\n'):
                if ip in line and ':' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.lower()
        except:
            pass
        
        # 3. nmap MAC detection
        try:
            result = subprocess.run(
                ["nmap", "-sn", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            for line in result.stdout.split('\n'):
                if 'MAC Address:' in line:
                    mac = line.split('MAC Address: ')[1].split(' ')[0].strip()
                    if len(mac) == 17:
                        return mac.lower()
        except:
            pass
        
        # 4. arping (plus agressif)
        try:
            result = subprocess.run(
                ["arping", "-c", "1", "-w", "1", ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            for line in result.stdout.split('\n'):
                if '[' in line and ']' in line:
                    mac_part = line.split('[')[1].split(']')[0]
                    if ':' in mac_part and len(mac_part) == 17:
                        return mac_part.lower()
        except:
            pass
        
        return "unknown"
    
    def _fallback_ping_sweep(self) -> List[str]:
        """Ping sweep BRUTAL si nmap échoue"""
        print("🏓 PING SWEEP BRUTAL...")
        active_ips = []
        network = ipaddress.IPv4Network(self.network_range, strict=False)
        
        # Ping parallèle ultra-agressif
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {
                executor.submit(self._ping_host, str(ip)): str(ip) 
                for ip in network.hosts()
            }
            
            for future in as_completed(futures):
                ip = futures[future]
                if future.result():
                    active_ips.append(ip)
        
        print(f"🎯 PING SWEEP: {len(active_ips)} hôtes actifs")
        return active_ips
    
    def _get_hostname_simple(self, ip: str) -> str:
        """Récupération hostname SIMPLE - teste les méthodes dans l'ordre"""
        
        # 1. DNS reverse (le plus classique)
        hostname = self._try_dns_reverse(ip)
        if hostname != "unknown":
            print(f"  → DNS: {hostname}")
            return hostname
        
        # 2. NetBIOS pour Windows (très efficace)
        hostname = self._try_netbios_simple(ip)
        if hostname != "unknown":
            print(f"  → NetBIOS: {hostname}")
            return hostname
        
        # 3. mDNS pour Mac/iOS
        hostname = self._try_mdns_simple(ip)
        if hostname != "unknown":
            print(f"  → mDNS: {hostname}")
            return hostname
        
        # 4. Nmap avec hostname detection
        hostname = self._try_nmap_hostname_simple(ip)
        if hostname != "unknown":
            print(f"  → Nmap: {hostname}")
            return hostname
        
        print(f"  → Aucun hostname trouvé pour {ip}")
        return "unknown"
    
    def _try_dns_reverse(self, ip: str) -> str:
        """DNS reverse lookup"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname and hostname != ip and not hostname.startswith('192.168'):
                return hostname.split('.')[0]  # Prendre juste le nom, pas le FQDN
        except:
            pass
        return "unknown"
    
    def _try_nmap_hostname_simple(self, ip: str) -> str:
        """Nmap hostname detection simplifié"""
        try:
            result = subprocess.run([
                'nmap', '-sn', ip
            ], capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line and '(' in line:
                    # Format: "Nmap scan report for HOSTNAME (192.168.1.174)"
                    hostname = line.split('for ')[1].split(' (')[0].strip()
                    if hostname and hostname != ip and hostname != 'localhost':
                        return hostname
        except:
            pass
        return "unknown"
    
    def _try_netbios_simple(self, ip: str) -> str:
        """NetBIOS simple et efficace pour Windows - parsing corrigé"""
        try:
            # nmblookup pour NetBIOS
            result = subprocess.run([
                'nmblookup', '-A', ip
            ], capture_output=True, text=True, timeout=3)
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Chercher les lignes avec <00> qui contiennent le nom du PC
                # Format: "\tTITO            <00> -         B <ACTIVE>"
                if '<00>' in line and 'ACTIVE' in line and 'GROUP' not in line:
                    # Nettoyer la ligne et extraire le nom
                    clean_line = line.replace('\t', '').strip()
                    # Le nom est avant '<00>'
                    if '<00>' in clean_line:
                        hostname = clean_line.split('<00>')[0].strip()
                        if hostname and hostname != ip and len(hostname) > 1:
                            # Vérifier que ce n'est pas un nom système
                            if not hostname.startswith('__') and hostname != 'WORKGROUP':
                                return hostname
        except:
            pass
        
        # Si nmblookup échoue, essayer nbtscan (mais il a souvent des problèmes de permission)
        try:
            result = subprocess.run([
                'nbtscan', '-r', ip
            ], capture_output=True, text=True, timeout=3)
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if name and name not in ['*', '<unknown>', 'SENDTO']:
                            return name
        except:
            pass
            
        return "unknown"
    
    def _try_netbios_nbtscan(self, ip: str) -> str:
        """NetBIOS nbtscan"""
        try:
            result = subprocess.run([
                'nbtscan', '-r', ip
            ], capture_output=True, text=True, timeout=1)
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if name and name not in ['*', '<unknown>', 'SENDTO']:
                            return name
        except:
            pass
        return "unknown"
    
    def _try_smb_lookup(self, ip: str) -> str:
        """SMB/CIFS lookup"""
        try:
            result = subprocess.run([
                'smbclient', '-L', ip, '-N', '--option=client min protocol=NT1'
            ], capture_output=True, text=True, timeout=2)
            
            for line in result.stdout.split('\n'):
                if 'Server=' in line:
                    for part in line.split():
                        if part.startswith('Server='):
                            server = part.split('=')[1]
                            if server and server not in ['UNKNOWN', '']:
                                return server
        except:
            pass
        return "unknown"
    
    def _try_mdns_simple(self, ip: str) -> str:
        """mDNS simple pour Mac/iOS"""
        try:
            result = subprocess.run([
                'avahi-resolve', '-a', ip
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    hostname = parts[1].replace('.local', '')
                    if hostname and hostname != ip:
                        return hostname
        except:
            pass
        return "unknown"
    
    def _try_dhcp_lookup(self, ip: str) -> str:
        """DHCP lease lookup"""
        try:
            # Chercher dans les leases DHCP
            with open('/var/lib/dhcp/dhcpd.leases', 'r') as f:
                content = f.read()
                if ip in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if f'lease {ip}' in line:
                            # Chercher client-hostname dans les lignes suivantes
                            for j in range(i+1, min(i+10, len(lines))):
                                if 'client-hostname' in lines[j]:
                                    hostname = lines[j].split('"')[1]
                                    if hostname:
                                        return hostname
        except:
            pass
        return "unknown"
    
    def _try_arp_lookup(self, ip: str) -> str:
        """ARP table lookup"""
        try:
            result = subprocess.run([
                'arp', '-n', ip
            ], capture_output=True, text=True, timeout=1)
            
            # Si dans ARP, essayer reverse DNS plus agressif
            if ip in result.stdout and 'no entry' not in result.stdout:
                return self._try_dns_reverse(ip)
        except:
            pass
        return "unknown"
    
    def _detect_device_type_tanked(self, hostname: str, mac: str, ip: str) -> str:
        """Détection TANKÉE du type d'appareil avec scan de ports"""
        hostname_lower = hostname.lower()
        vendor = self._get_vendor_from_mac(mac).lower()
        
        # 1. Détection par vendor MAC (priorité max)
        if vendor:
            if vendor == 'apple':
                # Distinguer iOS vs macOS par scan de ports
                if self._has_port_open(ip, 62078):  # AirPlay iOS
                    return 'ios'
                elif self._has_port_open(ip, 88):   # Kerberos macOS
                    return 'mac'
                else:
                    return 'ios' if 'iphone' in hostname_lower or 'ipad' in hostname_lower else 'mac'
                    
            elif vendor in ['samsung', 'huawei', 'xiaomi', 'google', 'lg', 'sony', 'oneplus']:
                return 'android'
                
            elif vendor in ['microsoft', 'intel', 'dell', 'hp', 'lenovo']:
                return 'windows'
                
        # 2. Scan de ports pour identification précise
        if self._has_port_open(ip, 445):  # SMB Windows
            return 'windows'
        elif self._has_port_open(ip, 22):   # SSH (Linux/Mac)
            return 'linux'
        elif self._has_port_open(ip, 5353): # mDNS (Apple)
            return 'ios' if 'mobile' in hostname_lower else 'mac'
            
        # 3. Patterns hostname étendus
        android_patterns = ['android', 'samsung', 'galaxy', 'pixel', 'huawei', 'xiaomi', 'oneplus']
        if any(p in hostname_lower for p in android_patterns):
            return 'android'
            
        windows_patterns = ['desktop', 'laptop', 'pc-', 'win-', 'windows']
        if any(p in hostname_lower for p in windows_patterns):
            return 'windows'
            
        return 'unknown'
    
    def _has_port_open(self, ip: str, port: int) -> bool:
        """Vérification rapide si un port est ouvert"""
        try:
            result = subprocess.run([
                'nmap', '-p', str(port), '--open', '-T5', ip
            ], capture_output=True, text=True, timeout=2)
            return f'{port}/tcp open' in result.stdout
        except:
            return False
    
    def _get_device_description_tanked(self, device_type: str, vendor: str, hostname: str, ip: str) -> str:
        """Description TANKÉE avec informations détaillées"""
        desc_parts = []
        
        # Type d'appareil
        type_names = {
            'windows': '🖥️ PC Windows',
            'android': '📱 Android',
            'ios': '📱 iPhone/iPad', 
            'mac': '💻 Mac',
            'linux': '🐧 Linux',
            'raspberry-pi': '🍓 Raspberry Pi',
            'router': '🌐 Routeur',
            'unknown': '❓ Inconnu'
        }
        desc_parts.append(type_names.get(device_type, '❓ Inconnu'))
        
        # Vendor
        if vendor and vendor != 'unknown':
            desc_parts.append(f"({vendor})")
            
        # Hostname si informatif
        if hostname and hostname not in ['unknown', ip] and len(hostname) > 2:
            desc_parts.append(f"- {hostname}")
            
        return ' '.join(desc_parts)
    
    def _detect_device_type(self, hostname: str, mac: str, ip: str) -> str:
        """Détecte le type d'appareil basé sur le hostname, MAC et ports ouverts"""
        hostname_lower = hostname.lower()
        
        # Obtenir le fabricant depuis l'adresse MAC
        vendor = self._get_vendor_from_mac(mac).lower()
        
        # Détection TANKÉE par fabricant MAC avec plus de marques
        if vendor:
            if vendor == 'apple':
                if any(keyword in hostname_lower for keyword in ['iphone', 'ipad', 'ipod', 'ios']):
                    return 'ios'
                elif any(keyword in hostname_lower for keyword in ['macbook', 'imac', 'mac', 'macos']):
                    return 'mac'
                else:
                    # Si c'est Apple mais pas clair, essayer de deviner
                    if any(keyword in hostname_lower for keyword in ['mobile', 'phone', 'pad']):
                        return 'ios'
                    return 'mac'
                    
            elif vendor in ['samsung', 'huawei', 'xiaomi', 'google', 'lg', 'sony', 'oneplus', 'oppo', 'vivo', 'realme', 'honor']:
                return 'android'
                
            elif vendor == 'microsoft':
                return 'windows'
                
            elif vendor == 'raspberry pi':
                return 'raspberry-pi'
                
            elif vendor in ['intel', 'asus', 'dell', 'hp', 'lenovo', 'acer']:
                return 'windows'  # Probable PC/laptop
        
        # Détection TANKÉE par hostname avec plus de patterns
        if any(name in hostname_lower for name in ['iphone', 'ipad', 'ipod', 'ios']):
            return 'ios'
            
        # Android - Marques et modèles étendus
        android_patterns = [
            'android', 'samsung', 'galaxy', 'pixel', 'huawei', 'xiaomi', 'redmi', 'poco',
            'oneplus', 'lg-', 'sony', 'xperia', 'oppo', 'vivo', 'realme', 'honor',
            'sm-', 'gt-', 'sgh-', 'sch-', 'sph-',  # Préfixes Samsung
            'p30', 'p40', 'mate', 'nova',  # Modèles Huawei
            'mi-', 'note-', 'max-', 'mix-',  # Préfixes Xiaomi
            'pra-', 'ano-', 'ele-', 'vtr-'  # Préfixes Huawei
        ]
        if any(pattern in hostname_lower for pattern in android_patterns):
            return 'android'
            
        # Windows - Patterns étendus
        windows_patterns = [
            'desktop', 'laptop', 'windows', 'pc-', 'win-', 'workstation',
            'dell-', 'hp-', 'lenovo-', 'asus-', 'acer-', 'msi-',
            'surface', 'thinkpad', 'pavilion', 'inspiron', 'latitude'
        ]
        if any(pattern in hostname_lower for pattern in windows_patterns):
            return 'windows'
            
        if any(name in hostname_lower for name in ['macbook', 'imac', 'mac']):
            return 'mac'
        
        # Détection par ports ouverts
        open_ports = self._scan_ports(ip)
        
        # Routeur/Point d'accès
        if any(port in open_ports for port in [23, 8080, 8443]) and 80 in open_ports:
            return 'router'
        
        # Imprimante
        if any(port in open_ports for port in [631, 9100, 515]):
            return 'printer'
        
        # Windows (RDP, SMB, WinRM)
        if any(port in open_ports for port in [135, 139, 445, 3389, 5985]):
            return 'windows'
        
        # SSH uniquement = probablement Linux/Unix
        if 22 in open_ports and not any(port in open_ports for port in [135, 139, 445]):
            return 'linux'
        
        # HTTP/HTTPS seulement = probablement serveur web ou appareil réseau
        if any(port in open_ports for port in [80, 443]) and not any(port in open_ports for port in [22, 135, 139, 445]):
            return 'server'
        
        return 'unknown'
    
    def _check_port(self, ip: str, port: int) -> bool:
        """Vérification d'un port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_vendor_from_mac(self, mac: str) -> str:
        """Obtient le fabricant depuis l'adresse MAC"""
        if mac == 'unknown' or len(mac) < 8:
            return ''
        
        # Extraire les 6 premiers caractères (OUI - Organizationally Unique Identifier)
        oui = mac.replace(':', '').replace('-', '').upper()[:6]
        
        # Base de données TANKÉE des fabricants MAC (massively expanded)
        vendors = {
            # Apple (iPhone, iPad, Mac) - MASSIVELY EXPANDED
            '001124': 'Apple', '001451': 'Apple', '0016CB': 'Apple', '0017F2': 'Apple',
            '0019E3': 'Apple', '001B63': 'Apple', '001EC2': 'Apple', '0021E9': 'Apple',
            '002332': 'Apple', '002436': 'Apple', '002500': 'Apple', '0026BB': 'Apple',
            '28E02C': 'Apple', '28E7CF': 'Apple', '2C0E3D': 'Apple', '30F7C5': 'Apple',
            '342387': 'Apple', '380F4A': 'Apple', '3C2EFF': 'Apple', '40A6D9': 'Apple',
            '44D884': 'Apple', '4C7C5F': 'Apple', '4C8D79': 'Apple', '5433CB': 'Apple',
            '60334B': 'Apple', '68AE20': 'Apple', '6C19C0': 'Apple', '6CAB31': 'Apple',
            '7073CB': 'Apple', '786C1C': 'Apple', '7C6193': 'Apple', '84B153': 'Apple',
            '8C58F3': 'Apple', '90B21F': 'Apple', '9027E4': 'Apple', '983B16': 'Apple',
            'A03BE3': 'Apple', 'A40CC3': 'Apple', 'AC3C0B': 'Apple', 'B065BD': 'Apple',
            'B418D1': 'Apple', 'BC52B7': 'Apple', 'C08997': 'Apple', 'C42C03': 'Apple',
            'C82A14': 'Apple', 'CC25EF': 'Apple', 'D023DB': 'Apple', 'D49A20': 'Apple',
            'E0C97A': 'Apple', 'E425E7': 'Apple', 'E80688': 'Apple', 'F0766F': 'Apple',
            '8863DF': 'Apple', 'F45C89': 'Apple', '041552': 'Apple', '186590': 'Apple',
            
            # Samsung (Galaxy, Note, etc.) - EXPANDED
            '000E8B': 'Samsung', '0012FB': 'Samsung', '001485': 'Samsung', '0016E4': 'Samsung',
            '001AA0': 'Samsung', '001D25': 'Samsung', '00215D': 'Samsung', '002454': 'Samsung',
            '0026C6': 'Samsung', '002566': 'Samsung', 'C06599': 'Samsung', 'E4B021': 'Samsung',
            'F8A45F': 'Samsung', '885A92': 'Samsung', '70F927': 'Samsung', '48EE0C': 'Samsung',
            '5C0A5B': 'Samsung', '78D6F0': 'Samsung', '8C3AE3': 'Samsung', '002067': 'Samsung',
            'B853AC': 'Samsung', 'D85D4C': 'Samsung', '20A99B': 'Samsung', '542696': 'Samsung',
            
            # Google/Android (Pixel, Nexus, etc.)
            '001A11': 'Google', '00259C': 'Google', '3C5AB4': 'Google', '54FA3E': 'Google',
            '6476BA': 'Google', '68EF43': 'Google', '74E28C': 'Google', '7C6166': 'Google',
            '84F3EB': 'Google', '9C65B0': 'Google', 'A0143D': 'Google', 'A4F1E8': 'Google',
            'B4F0AB': 'Google', 'C4B301': 'Google', 'CC3A61': 'Google', 'F4F5E8': 'Google',
            
            # Xiaomi (Mi, Redmi, POCO) - EXPANDED
            '0008DC': 'Xiaomi', '002268': 'Xiaomi', '20CF30': 'Xiaomi', '286C07': 'Xiaomi',
            '34CE00': 'Xiaomi', '3448ED': 'Xiaomi', '50EC50': 'Xiaomi', '78F8DC': 'Xiaomi',
            '7C1DD9': 'Xiaomi', '8CFABA': 'Xiaomi', '98FA9B': 'Xiaomi', 'A0E45C': 'Xiaomi',
            '743A2F': 'Xiaomi', 'FC64BA': 'Xiaomi', '2CF05D': 'Xiaomi', '682737': 'Xiaomi',
            
            # Huawei (Honor, P-series, Mate) - EXPANDED
            '000FE2': 'Huawei', '001A2B': 'Huawei', '002E5D': 'Huawei', '00466F': 'Huawei',
            '0CF347': 'Huawei', '1816C9': 'Huawei', '244B03': 'Huawei', '28311F': 'Huawei',
            '389AF6': 'Huawei', '48DB50': 'Huawei', '5C0272': 'Huawei', '6C4B90': 'Huawei',
            'C40BCB': 'Huawei', 'AC853D': 'Huawei', 'E0E2E6': 'Huawei', '0894EF': 'Huawei',
            
            # OnePlus 
            '001D4F': 'OnePlus', 'A85B78': 'OnePlus', '0018D6': 'OnePlus', '8C1AB5': 'OnePlus',
            
            # LG Electronics
            '001C62': 'LG', '0019C6': 'LG', '001E75': 'LG', '002140': 'LG',
            '6C2906': 'LG', 'B0472F': 'LG', 'C49A02': 'LG', 'F80CF3': 'LG',
            
            # Sony (Xperia, PlayStation)
            '001125': 'Sony', '001656': 'Sony', '001EA9': 'Sony', '002148': 'Sony',
            '4CE576': 'Sony', '7C6166': 'Sony', '9C207B': 'Sony', 'C4E984': 'Sony',
            
            # Microsoft (Surface, Xbox)
            '000D3A': 'Microsoft', '001DD8': 'Microsoft', '0050F2': 'Microsoft', '7C1E52': 'Microsoft',
            'A41731': 'Microsoft', 'B496C8': 'Microsoft', 'E4A7C5': 'Microsoft', '001E41': 'Microsoft',
            
            # Intel (NUC, WiFi cards)
            '000423': 'Intel', '0007E9': 'Intel', '000C29': 'Intel', '001B21': 'Intel',
            '0021CC': 'Intel', '002448': 'Intel', '00262D': 'Intel', '088FC3': 'Intel',
            
            # ASUS (routers, motherboards)
            '000C6E': 'ASUS', '00184D': 'ASUS', '001E8C': 'ASUS', '002215': 'ASUS',
            '1C872C': 'ASUS', '2C56DC': 'ASUS', '50465D': 'ASUS', 'F46D04': 'ASUS',
            
            # Raspberry Pi
            'B827EB': 'Raspberry Pi', 'DC1FE5': 'Raspberry Pi', 'E45F01': 'Raspberry Pi',
            
            # Routeurs TANKÉS
            '001346': 'Netgear', '00146C': 'Netgear', '2C30F5': 'Netgear', '3085A9': 'Netgear',
            'A0040A': 'Netgear', 'C40415': 'Netgear', 'E091F5': 'Netgear', '04BF6D': 'Netgear',
            '00095B': 'Linksys', '000C41': 'Linksys', '0013F7': 'Linksys', '68725B': 'Linksys',
            '001839': 'Cisco', '001F26': 'Cisco', '002155': 'Cisco', '0023AC': 'Cisco',
            '14DAE9': 'TP-Link', '50C7BF': 'TP-Link', 'A42BB0': 'TP-Link', 'E848B8': 'TP-Link',
            '98DAC4': 'TP-Link', 'F09FC2': 'TP-Link', '84D47E': 'TP-Link', 'C4E90A': 'TP-Link',
            
            # D-Link
            '001195': 'D-Link', '0013461': 'D-Link', '0015E9': 'D-Link', '001CF0': 'D-Link',
            
            # Nintendo (Switch, 3DS)
            '001656': 'Nintendo', '0017AB': 'Nintendo', '001EA9': 'Nintendo', '001FC5': 'Nintendo',
            '34AF2C': 'Nintendo', '7CBB8A': 'Nintendo', 'A45E60': 'Nintendo', 'B88687': 'Nintendo',
            
            # Amazon (Echo, Fire TV)
            'F0D2F1': 'Amazon', '74C246': 'Amazon', '44650D': 'Amazon', '006171': 'Amazon',
            
            # Broadcom (WiFi chips)
            '001018': 'Broadcom', '0014A4': 'Broadcom', '001839': 'Broadcom', '002129': 'Broadcom',
            
            # Realtek (network adapters)
            '525400': 'Realtek', '001E06': 'Realtek', '00E04C': 'Realtek', '52540A': 'Realtek'
        }
        
        return vendors.get(oui, '')

    def _get_device_description(self, device_type: str, vendor: str, hostname: str) -> str:
        """Génère une description plus détaillée de l'appareil"""
        if device_type == 'ios':
            if 'ipad' in hostname.lower():
                return f"iPad ({vendor})"
            elif 'iphone' in hostname.lower():
                return f"iPhone ({vendor})"
            else:
                return f"Appareil iOS ({vendor})"
                
        elif device_type == 'android':
            if vendor:
                if vendor.lower() == 'samsung':
                    return f"Smartphone Samsung"
                elif vendor.lower() == 'huawei':
                    return f"Smartphone Huawei"
                elif vendor.lower() == 'xiaomi':
                    return f"Smartphone Xiaomi"
                elif vendor.lower() == 'google':
                    return f"Smartphone Google Pixel"
                else:
                    return f"Smartphone Android ({vendor})"
            return "Smartphone Android"
            
        elif device_type == 'windows':
            if 'laptop' in hostname.lower() or 'notebook' in hostname.lower():
                return f"PC Portable Windows ({vendor})" if vendor else "PC Portable Windows"
            elif 'desktop' in hostname.lower():
                return f"PC Bureau Windows ({vendor})" if vendor else "PC Bureau Windows"
            else:
                return f"PC Windows ({vendor})" if vendor else "PC Windows"
                
        elif device_type == 'mac':
            if 'macbook' in hostname.lower():
                return f"MacBook ({vendor})"
            elif 'imac' in hostname.lower():
                return f"iMac ({vendor})"
            else:
                return f"Mac ({vendor})"
                
        elif device_type == 'router':
            return f"Routeur ({vendor})" if vendor else "Routeur/Point d'accès"
            
        elif device_type == 'printer':
            return f"Imprimante ({vendor})" if vendor else "Imprimante"
            
        elif device_type == 'raspberry-pi':
            return "Raspberry Pi"
            
        elif device_type == 'linux':
            return f"Serveur Linux ({vendor})" if vendor else "Serveur Linux"
            
        elif device_type == 'server':
            return f"Serveur Web ({vendor})" if vendor else "Serveur Web"
            
        else:
            return f"Appareil réseau ({vendor})" if vendor else "Appareil réseau"

    def scan_network(self, network_range: str = None, force: bool = False) -> List[Dict]:
        """Scanner réseau SIMPLE et EFFICACE - Méthode par méthode"""
        
        # Cache simple
        if not force and self.cache:
            cache_age = self.time.time() - self.last_full_scan
            if cache_age < self.cache_ttl:
                print(f"Cache hit - scan réseau en {0:.2f}s")
                return list(self.cache.values())
        
        print("� Scan réseau simple et efficace...")
        start_time = self.time.time()
        
        # ÉTAPE 1: Découvrir les IPs actives avec nmap (simple et fiable)
        active_ips = self._simple_nmap_discovery()
        print(f"📡 {len(active_ips)} appareils détectés")
        
        # ÉTAPE 2: Scanner chaque appareil individuellement (pas de parallèle fou)
        devices = []
        for ip in active_ips:
            print(f"🔍 Analyse {ip}...")
            device = self._scan_device_simple(ip)
            if device:
                devices.append(device)
                self.cache[device['ip']] = device
        
        self.last_full_scan = self.time.time()
        scan_time = self.last_full_scan - start_time
        
        print(f"✅ Scan terminé: {len(devices)} appareils en {scan_time:.1f}s")
        return sorted(devices, key=lambda x: ipaddress.IPv4Address(x['ip']))
    
    def _simple_nmap_discovery(self) -> List[str]:
        """Découverte simple et fiable avec nmap"""
        try:
            print("📡 Découverte nmap simple...")
            # Nmap simple mais efficace
            result = subprocess.run([
                'nmap', '-sn', self.network_range
            ], capture_output=True, text=True, timeout=30)
            
            active_ips = []
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    # Extraire l'IP proprement
                    if '(' in line and ')' in line:
                        # Format: "Nmap scan report for hostname (192.168.1.1)"
                        ip = line.split('(')[1].split(')')[0]
                    else:
                        # Format: "Nmap scan report for 192.168.1.1"
                        ip = line.split()[-1]
                    
                    # Validation simple de l'IP
                    if self._is_valid_ip(ip):
                        active_ips.append(ip)
            
            return active_ips
            
        except Exception as e:
            print(f"❌ Erreur nmap: {e}")
            return []
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validation simple d'IP"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except:
            return False
    
    def _scan_ip_complete(self, ip: str) -> Dict:
        """Scan complet et tanké d'une IP avec toutes les méthodes de détection"""
        # Vérifier le cache d'abord
        cached = self._get_cached_device(ip)
        if cached:
            return cached
        
        # Scan complet avec toutes les méthodes
        hostname = self._get_hostname(ip)
        mac = self._get_mac_address(ip) 
        vendor = self._get_vendor_from_mac(mac)
        device_type = self._detect_device_type(hostname, mac, ip)
        description = self._get_device_description(device_type, vendor, hostname)
        
        return {
            'ip': ip,
            'hostname': hostname,
            'mac': mac,
            'vendor': vendor,
            'device_type': device_type,
            'description': description,
            'status': 'online'
        }
    

    

    
    def _is_host_up(self, ip: str) -> bool:
        """Vérifie si un hôte est accessible"""
        try:
            # Utiliser nmap pour une détection plus rapide et fiable
            result = subprocess.run(
                ['nmap', '-sn', '-T4', ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            return 'Host is up' in result.stdout
        except:
            # Fallback avec ping
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return result.returncode == 0
            except:
                return False
    
    def _scan_ports(self, ip: str, ports: List[int] = None) -> List[int]:
        """Scanne les ports ouverts sur une IP"""
        if ports is None:
            # Ports courants à scanner
            ports = [22, 23, 53, 80, 135, 139, 443, 445, 515, 631, 3389, 5985, 8080, 8443, 9100]
        
        open_ports = []
        
        # Utiliser nmap pour scanner les ports rapidement
        try:
            port_list = ','.join(map(str, ports))
            result = subprocess.run(
                ['nmap', '-p', port_list, '--open', '-T4', ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if '/tcp' in line and 'open' in line:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
                    
        except Exception as e:
            # Fallback: test manuel des ports critiques
            import socket
            critical_ports = [22, 80, 443, 445, 3389]
            for port in critical_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass
        
        return open_ports
    
    def _get_hostname_light(self, ip: str) -> str:
        """Version légère pour obtenir le hostname (DNS uniquement)"""
        try:
            socket.setdefaulttimeout(self.timeouts['dns_lookup'])
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname if hostname != ip else f"Appareil-{ip.split('.')[-1]}"
        except:
            return f"Appareil-{ip.split('.')[-1]}"
        finally:
            socket.setdefaulttimeout(None)
    
    def _get_mac_address_light(self, ip: str) -> str:
        """Version légère pour obtenir l'adresse MAC (ARP seulement)"""
        try:
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=self.timeouts['arp'])
            for line in result.stdout.split('\n'):
                if ip in line and ':' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.lower()
        except:
            pass
        return "unknown"
    
    def _detect_device_type_light(self, hostname: str, vendor: str) -> str:
        """Détection légère du type d'appareil (sans scan de ports)"""
        hostname_lower = hostname.lower()
        vendor_lower = vendor.lower()
        
        # Détection par fabricant MAC
        if vendor_lower == 'apple':
            if any(keyword in hostname_lower for keyword in ['iphone', 'ipad', 'ipod', 'ios']):
                return 'ios'
            return 'mac'
        elif vendor_lower in ['samsung', 'huawei', 'xiaomi', 'google']:
            return 'android'
        elif vendor_lower == 'microsoft':
            return 'windows'
        elif vendor_lower == 'raspberry pi':
            return 'raspberry-pi'
        
        # Détection par hostname
        if any(name in hostname_lower for name in ['iphone', 'ipad', 'ipod', 'ios']):
            return 'ios'
        if any(name in hostname_lower for name in ['android', 'samsung', 'galaxy', 'pixel']):
            return 'android'
        if any(name in hostname_lower for name in ['desktop', 'laptop', 'windows', 'pc-', 'win-']):
            return 'windows'
        if any(name in hostname_lower for name in ['macbook', 'imac', 'mac']):
            return 'mac'
        
        return 'unknown'

    def _is_cache_valid(self, ip: str) -> bool:
        """Vérifie si le cache est encore valide pour cette IP"""
        if ip not in self.cache:
            return False
        
        cache_time = self.cache[ip].get('_cached_at', 0)
        return (self.time.time() - cache_time) < self.cache_ttl
    
    def _cache_device(self, ip: str, device_info: Dict):
        """Met en cache les infos d'un appareil"""
        device_info['_cached_at'] = self.time.time()
        self.cache[ip] = device_info
    
    def _get_cached_device(self, ip: str) -> Optional[Dict]:
        """Récupère un appareil depuis le cache"""
        if self._is_cache_valid(ip):
            cached = self.cache[ip].copy()
            cached.pop('_cached_at', None)
            return cached
        return None

    def get_device_info(self, ip: str, use_cache: bool = True) -> Optional[Dict]:
        """Méthode publique pour obtenir les infos d'un appareil"""
        # Vérifier le cache d'abord
        if use_cache:
            cached = self._get_cached_device(ip)
            if cached:
                return cached
        
        # Scan et mise en cache
        device_info = self._scan_ip(ip)
        if device_info:
            self._cache_device(ip, device_info)
        
        return device_info