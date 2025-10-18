"""
Scanner réseau unifié COMPLET et EXHAUSTIF
Objectif : détecter TOUT ce qui existe sur le réseau (Windows, Android, iOS, Linux, IoT...)
Priorité à l'exhaustivité plutôt qu'à la vitesse
"""

import subprocess
import socket
import json
import time
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
from .mac_detector import MacVendorDetector
from .mobile_detector import AdvancedMobileDetector

class UnifiedNetworkScanner:
    """Scanner réseau EXHAUSTIF - détecte tout ce qui bouge"""
    
    def __init__(self):
        self.network_range = "192.168.1.0/24"
        self.mac_detector = MacVendorDetector()
        self.mobile_detector = AdvancedMobileDetector()
        
    def scan_complete_network(self) -> List[Dict]:
        """Scan COMPLET du réseau - détecte tout"""
        print("🔍 Démarrage du scan réseau COMPLET...")
        devices = []
        network = ipaddress.IPv4Network(self.network_range, strict=False)
        
        # 1. D'abord découverte rapide des IPs actives avec nmap
        active_ips = self._discover_active_hosts()
        print(f"📡 {len(active_ips)} hôtes actifs détectés")
        
        # 2. Scan exhaustif de chaque IP active
        for i, ip in enumerate(active_ips):
            print(f"🔍 Scan exhaustif {i+1}/{len(active_ips)}: {ip}")
            device = self._scan_device_exhaustive(ip)
            if device:
                devices.append(device)
                print(f"✅ {ip}: {device['hostname']} ({device['device_type']})")
        
        print(f"🎉 Scan terminé - {len(devices)} appareils détectés")
        return devices
    
    def _discover_active_hosts(self) -> List[str]:
        """Découverte des hôtes actifs avec nmap"""
        try:
            # nmap ping scan pour découvrir tous les hôtes actifs
            result = subprocess.run([
                'nmap', '-sn', self.network_range
            ], capture_output=True, text=True, timeout=60)
            
            active_ips = []
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    # Extraire l'IP de la ligne
                    if '(' in line and ')' in line:
                        # Format: "Nmap scan report for hostname (192.168.1.1)"
                        ip = line.split('(')[1].split(')')[0]
                    else:
                        # Format: "Nmap scan report for 192.168.1.1"
                        ip = line.split('for ')[1].strip()
                    
                    # Vérifier que c'est une IP valide
                    try:
                        ipaddress.IPv4Address(ip)
                        active_ips.append(ip)
                    except:
                        pass
            
            return sorted(active_ips, key=lambda x: ipaddress.IPv4Address(x))
        except:
            # Fallback : scanner toute la plage
            network = ipaddress.IPv4Network(self.network_range, strict=False)
            return [str(ip) for ip in list(network.hosts())[:20]]  # Limiter pour test
    
    def _scan_device_exhaustive(self, ip: str) -> Optional[Dict]:
        """Scan EXHAUSTIF d'un appareil - toutes les méthodes"""
        try:
            print(f"  🔍 Analyse de {ip}...")
            
            # 1. Ping test
            if not self._ping_test(ip):
                print(f"  ❌ {ip} ne répond pas au ping")
                return None
            
            # 2. Récupération hostname EXHAUSTIVE
            hostname = self._get_hostname_exhaustive(ip)
            print(f"  📝 Hostname: {hostname}")
            
            # 3. Récupération MAC address 
            mac = self._get_mac_address_exhaustive(ip)
            print(f"  🔗 MAC: {mac}")
            
            # 4. Détection vendor et type depuis MAC
            vendor, device_type_mac = self.mac_detector.detect_vendor_and_type(mac)
            
            # 5. Scan des ports pour identification
            open_ports = self._scan_critical_ports(ip)
            print(f"  🔌 Ports ouverts: {open_ports}")
            
            # 6. Détection du type d'appareil COMBINÉE (hostname + MAC + ports)
            device_type = self._detect_device_type_combined(hostname, mac, vendor, device_type_mac, open_ports)
            
            # 7. Analyse mobile avancée si mobile détecté
            mobile_analysis = None
            if ("Mobile" in device_type or "Privacy" in device_type or 
                vendor in ["Apple", "Samsung", "Xiaomi", "Huawei"] or
                "Unknown (Private MAC)" in vendor):
                print(f"  📱 Analyse mobile avancée...")
                try:
                    mobile_analysis = self.mobile_detector.analyze_mobile_device(ip, mac, hostname)
                    if mobile_analysis and mobile_analysis.get('final_detection'):
                        final_det = mobile_analysis['final_detection']
                        if final_det['confidence'] > 30:  # Seuil de confiance
                            # Mettre à jour avec les infos avancées
                            if final_det['brand'] != "Unknown":
                                vendor = final_det['brand']
                            if final_det['type'] != "Unknown":
                                device_type = final_det['type']
                            print(f"    🎯 Détection avancée: {final_det['brand']} {final_det['type']} (conf: {final_det['confidence']}%)")
                except Exception as e:
                    print(f"    ❌ Erreur mobile detection: {e}")
            
            # 8. Informations système si possible
            system_info = self._get_system_info(ip, open_ports)
            
            # 9. Description complète avec le détecteur MAC
            description = self.mac_detector.get_device_description(vendor, device_type, hostname)
            
            device = {
                'ip': ip,
                'hostname': hostname,
                'mac': mac,
                'vendor': vendor,
                'device_type': device_type,
                'open_ports': open_ports,
                'system_info': system_info,
                'mobile_analysis': mobile_analysis,
                'description': description,
                'status': 'online',
                'last_seen': time.time()
            }
            
            return device
            
        except Exception as e:
            print(f"  ❌ Erreur scan {ip}: {e}")
            return None
    
    def _ping_test(self, ip: str) -> bool:
        """Test ping simple"""
        try:
            result = subprocess.run([
                'ping', '-c', '1', '-W', '2', ip
            ], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _get_hostname_exhaustive(self, ip: str) -> str:
        """Récupération hostname EXHAUSTIVE - toutes les méthodes"""
        
        # 1. DNS reverse lookup
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname and hostname != ip and not hostname.startswith('192.168'):
                print(f"    ✅ DNS: {hostname}")
                return hostname
        except:
            pass
        
        # 2. NetBIOS lookup pour Windows (nmblookup)
        try:
            result = subprocess.run([
                'nmblookup', '-A', ip
            ], capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if '<00>' in line and 'ACTIVE' in line and 'GROUP' not in line:
                    clean_line = line.replace('\t', '').strip()
                    if '<00>' in clean_line:
                        hostname = clean_line.split('<00>')[0].strip()
                        if hostname and hostname != ip and len(hostname) > 1:
                            if not hostname.startswith('__') and hostname != 'WORKGROUP':
                                print(f"    ✅ NetBIOS (nmblookup): {hostname}")
                                return hostname
        except:
            pass
        
        # 3. NetBIOS avec nbtscan
        try:
            result = subprocess.run([
                'nbtscan', '-r', ip
            ], capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        hostname = parts[1]
                        if hostname and hostname not in ['*', '<unknown>', 'SENDTO', 'Failed']:
                            print(f"    ✅ NetBIOS (nbtscan): {hostname}")
                            return hostname
        except:
            pass
        
        # 4. SMB/CIFS lookup pour Windows
        try:
            result = subprocess.run([
                'smbclient', '-L', ip, '-N', '--option=client min protocol=NT1'
            ], capture_output=True, text=True, timeout=5)
            
            for line in result.stdout.split('\n'):
                if 'Server=' in line:
                    for part in line.split():
                        if part.startswith('Server='):
                            server = part.split('=')[1]
                            if server and server not in ['UNKNOWN', '', 'NT_STATUS_IO_TIMEOUT']:
                                print(f"    ✅ SMB: {server}")
                                return server
        except:
            pass
        
        # 5. mDNS/Bonjour pour Mac/iOS
        try:
            result = subprocess.run([
                'avahi-resolve', '-a', ip
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    hostname = parts[1].replace('.local', '')
                    if hostname and hostname != ip:
                        print(f"    ✅ mDNS: {hostname}")
                        return hostname
        except:
            pass
        
        # 6. Service discovery mDNS pour Android/iOS
        services = [
            "_device-info._tcp",
            "_androidtvremote._tcp", 
            "_googlecast._tcp",
            "_airplay._tcp",
            "_spotify-connect._tcp",
            "_http._tcp"
        ]
        
        for service in services:
            try:
                result = subprocess.run([
                    'avahi-browse', '-r', '-t', service, '-p', '--resolve'
                ], capture_output=True, text=True, timeout=3)
                
                for line in result.stdout.split('\n'):
                    if ip in line and ';' in line:
                        parts = line.split(';')
                        if len(parts) > 6:
                            device_name = parts[6]
                            if device_name and device_name != ip and len(device_name) > 1:
                                print(f"    ✅ mDNS service ({service}): {device_name}")
                                return device_name
            except:
                continue
        
        # 7. nmap hostname detection
        try:
            result = subprocess.run([
                'nmap', '-sn', ip
            ], capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line and '(' in line:
                    hostname = line.split('for ')[1].split(' (')[0].strip()
                    if hostname and hostname != ip:
                        print(f"    ✅ nmap: {hostname}")
                        return hostname
        except:
            pass
        
        # 8. DHCP lookup (si accessible)
        try:
            for dhcp_file in ['/var/lib/dhcp/dhcpd.leases', '/var/lib/dhcpcd5/dhcpcd.leases']:
                result = subprocess.run([
                    'grep', '-A', '10', '-B', '2', ip, dhcp_file
                ], capture_output=True, text=True, timeout=2)
                
                for line in result.stdout.split('\n'):
                    if 'client-hostname' in line:
                        hostname = line.split('"')[1]
                        if hostname and hostname != ip:
                            print(f"    ✅ DHCP: {hostname}")
                            return hostname
        except:
            pass
        
        print(f"    ❌ Aucun hostname trouvé")
        return f"device-{ip.split('.')[-1]}"
    
    def _get_mac_address_exhaustive(self, ip: str) -> str:
        """Récupération MAC address exhaustive"""
        
        # 1. Table ARP
        try:
            result = subprocess.run([
                'arp', '-n', ip
            ], capture_output=True, text=True, timeout=2)
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.lower()
        except:
            pass
        
        # 2. Ping + ARP
        try:
            subprocess.run(['ping', '-c', '1', ip], capture_output=True, timeout=3)
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=2)
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.lower()
        except:
            pass
        
        # 3. nmap MAC detection
        try:
            result = subprocess.run([
                'nmap', '-sn', ip
            ], capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\n'):
                if 'MAC Address:' in line:
                    mac = line.split('MAC Address: ')[1].split()[0]
                    return mac.lower()
        except:
            pass
        
        return "unknown"
    
    def _scan_critical_ports(self, ip: str) -> List[int]:
        """Scan des ports critiques pour identification"""
        # Ports importants pour identification des services
        critical_ports = [22, 23, 53, 80, 135, 139, 443, 445, 548, 554, 993, 995, 1900, 3389, 5353, 8080, 9100]
        
        try:
            # nmap scan rapide des ports critiques
            ports_str = ','.join(map(str, critical_ports))
            result = subprocess.run([
                'nmap', '-p', ports_str, '--open', '-T4', ip
            ], capture_output=True, text=True, timeout=30)
            
            open_ports = []
            for line in result.stdout.split('\n'):
                if '/tcp' in line and 'open' in line:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
            
            return sorted(open_ports)
        except:
            return []
    
    def _detect_device_type_combined(self, hostname: str, mac: str, vendor: str, device_type_mac: str, open_ports: List[int]) -> str:
        """Détection COMBINÉE du type d'appareil - hostname + MAC + ports"""
        
        # 1. Si le détecteur MAC a trouvé quelque chose de spécifique, priorité
        if device_type_mac and device_type_mac not in ["Unknown Device"]:
            # Vérifier si les ports confirment
            if "Mobile" in device_type_mac and not open_ports:
                return device_type_mac  # Mobiles ont rarement des ports ouverts
            elif "Android" in device_type_mac:
                return device_type_mac
            elif "Apple" in device_type_mac:
                # Affiner selon le hostname si possible
                if hostname and hostname.lower() != "unknown":
                    hostname_lower = hostname.lower()
                    if any(term in hostname_lower for term in ['iphone', 'phone']):
                        return "iPhone"
                    elif any(term in hostname_lower for term in ['ipad', 'tablet']):
                        return "iPad"
                    elif any(term in hostname_lower for term in ['macbook', 'imac', 'mac']):
                        return "Mac"
                    elif any(term in hostname_lower for term in ['appletv', 'tv']):
                        return "Apple TV"
                return device_type_mac
        
        # 2. Analyse des ports pour identification Windows/Linux
        has_smb = 445 in open_ports or 139 in open_ports
        has_rdp = 3389 in open_ports  
        has_ssh = 22 in open_ports
        has_http = 80 in open_ports or 443 in open_ports or 8080 in open_ports
        has_printer = 9100 in open_ports
        
        # Windows PC/Server
        if has_smb or has_rdp:
            if has_rdp or (hostname and 'server' in hostname.lower()):
                return "Windows Server"
            return "Windows PC"
        
        # Imprimante
        if has_printer:
            return "Printer"
        
        # Linux/Unix servers
        if has_ssh and not has_smb:
            return "Linux Server"
        
        # 3. Analyse du hostname
        if hostname and hostname.lower() != "unknown":
            hostname_lower = hostname.lower()
            
            # Windows patterns
            if any(term in hostname_lower for term in ['windows', 'win', 'pc', 'desktop']):
                return "Windows PC"
            
            # Mobile patterns
            if any(term in hostname_lower for term in ['iphone', 'android', 'phone', 'mobile']):
                return "Mobile Phone"
            
            # Apple patterns
            if any(term in hostname_lower for term in ['macbook', 'imac', 'mac-', 'apple']):
                return "Mac"
            
            # Network equipment
            if any(term in hostname_lower for term in ['router', 'gateway', 'access', 'switch']):
                return "Network Equipment"
            
            # Smart devices
            if any(term in hostname_lower for term in ['tv', 'chromecast', 'roku', 'alexa', 'nest']):
                return "Smart Device"
        
        # 4. Fallback sur vendor + MAC analysis
        if vendor and vendor != "Unknown":
            vendor_lower = vendor.lower()
            
            if "apple" in vendor_lower:
                return "Apple Device"
            elif any(mobile_vendor in vendor_lower for mobile_vendor in ['samsung', 'xiaomi', 'huawei', 'oppo', 'vivo', 'oneplus']):
                return "Android Phone"
            elif any(pc_vendor in vendor_lower for pc_vendor in ['intel', 'dell', 'asus']):
                return "PC/Laptop"
            elif any(network_vendor in vendor_lower for network_vendor in ['tp-link', 'netgear', 'cisco']):
                return "Network Equipment"
        
        # 5. Si MAC privée détectée, probablement mobile
        if "Private MAC" in vendor or "Privacy Mode" in device_type_mac:
            return "Mobile Device (Privacy)"
        
        return "Unknown Device"
    
    def _get_system_info(self, ip: str, open_ports: List[int]) -> Dict:
        """Récupération d'informations système si possible"""
        info = {}
        
        # Informations SMB si disponible
        if 445 in open_ports:
            try:
                result = subprocess.run([
                    'smbclient', '-L', ip, '-N'
                ], capture_output=True, text=True, timeout=5)
                
                for line in result.stdout.split('\n'):
                    if 'Domain=' in line:
                        domain = line.split('Domain=')[1].split()[0] if 'Domain=' in line else None
                        if domain:
                            info['domain'] = domain
                    elif 'OS=' in line:
                        os_info = line.split('OS=')[1].split()[0] if 'OS=' in line else None
                        if os_info:
                            info['os'] = os_info
            except:
                pass
        
        # Informations HTTP si disponible
        if 80 in open_ports or 443 in open_ports:
            try:
                port = 443 if 443 in open_ports else 80
                protocol = 'https' if port == 443 else 'http'
                
                result = subprocess.run([
                    'curl', '-m', '3', '-s', '-I', f'{protocol}://{ip}:{port}/'
                ], capture_output=True, text=True, timeout=5)
                
                for line in result.stdout.split('\n'):
                    if 'Server:' in line:
                        info['web_server'] = line.split('Server:')[1].strip()
                        break
            except:
                pass
        
        return info
    
    def _generate_description(self, hostname: str, device_type: str, vendor: str, system_info: Dict) -> str:
        """Génération de description complète"""
        parts = []
        
        # Type d'appareil en premier
        parts.append(device_type)
        
        # Hostname si disponible et significatif
        if hostname and not hostname.startswith('device-') and hostname != "unknown":
            parts.append(f"({hostname})")
        
        # Vendor si disponible
        if vendor and vendor != "Unknown":
            parts.append(f"- {vendor}")
        
        # Informations système
        if system_info:
            if 'os' in system_info:
                parts.append(f"- {system_info['os']}")
            if 'domain' in system_info:
                parts.append(f"- Domain: {system_info['domain']}")
            if 'web_server' in system_info:
                parts.append(f"- Web: {system_info['web_server']}")
        
        return " ".join(parts)