"""
Scanner réseau avancé utilisant nmap, ARP et autres techniques
Pour une détection précise des appareils sur le réseau local
"""

import nmap
import subprocess
import json
import ipaddress
import socket
import logging
import time
import threading
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import netifaces

logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.scan_results = {}
        self.last_scan_time = None
        
        # Configuration par défaut PROFESSIONNELLE
        self.default_ports = '21,22,23,25,53,80,110,139,143,443,445,993,995,1723,3389,5353,5432,8080,8443,9100'
        self.scan_timeout = 45  # Plus de temps pour scan complet
        self.max_threads = 20   # Plus de threads pour performance
        
        # Ports spécialisés pour détection OS/Services
        self.os_detection_ports = '22,135,139,445,3389,5353,62078'  # SSH, NetBIOS, SMB, RDP, mDNS, iPhone
        self.service_ports = '21,25,53,80,110,143,443,993,995,8080,8443,9100'  # Services courants
        
        # Fingerprints OS (basés sur patterns de services)
        self.os_fingerprints = {
            'windows': [135, 139, 445, 3389],      # NetBIOS, SMB, RDP
            'linux': [22, 111, 514, 5353],        # SSH, RPC, Syslog, mDNS
            'macos': [22, 548, 5353, 62078],       # SSH, AFP, mDNS, iOS sync
            'ios': [62078, 5353],                  # iOS specific
            'android': [5555, 5353],               # ADB, mDNS
            'router': [22, 23, 53, 80, 443],       # SSH, Telnet, DNS, Web
            'printer': [9100, 631, 80],            # JetDirect, IPP, Web
        }
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Récupérer les interfaces réseau disponibles"""
        interfaces = []
        
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                
                # IPv4 addresses
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info.get('addr')
                        netmask = addr_info.get('netmask')
                        
                        if ip and netmask and not ip.startswith('127.'):
                            try:
                                network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                                interfaces.append({
                                    'interface': interface,
                                    'ip': ip,
                                    'netmask': netmask,
                                    'network': str(network.network_address),
                                    'cidr': str(network),
                                    'broadcast': addr_info.get('broadcast')
                                })
                            except Exception as e:
                                logger.warning(f"Erreur processing interface {interface}: {e}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des interfaces: {e}")
        
        return interfaces
    
    def get_default_network(self) -> Optional[str]:
        """Récupérer le réseau par défaut à scanner"""
        interfaces = self.get_network_interfaces()
        
        # Préférer les réseaux privés
        for interface in interfaces:
            ip = interface['ip']
            if (ip.startswith('192.168.') or 
                ip.startswith('10.') or 
                (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)):
                return interface['cidr']
        
        # Fallback sur la première interface non-loopback
        if interfaces:
            return interfaces[0]['cidr']
        
        return None
    
    def ping_sweep(self, network: str, timeout: int = 2) -> List[str]:
        """
        Effectuer un ping sweep rapide pour trouver les hôtes actifs
        """
        active_hosts = []
        
        try:
            net = ipaddress.IPv4Network(network, strict=False)
            hosts = list(net.hosts())
            
            logger.info(f"Ping sweep sur {network} ({len(hosts)} hôtes)")
            
            def ping_host(host_ip):
                try:
                    # Utiliser ping système pour plus de rapidité
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', str(timeout), str(host_ip)],
                        capture_output=True,
                        timeout=timeout + 1
                    )
                    if result.returncode == 0:
                        return str(host_ip)
                except Exception:
                    pass
                return None
            
            # Paralléliser les pings
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = {executor.submit(ping_host, host): host for host in hosts}
                
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        active_hosts.append(result)
            
            logger.info(f"Ping sweep terminé: {len(active_hosts)} hôtes actifs trouvés")
            
        except Exception as e:
            logger.error(f"Erreur lors du ping sweep: {e}")
        
        return sorted(active_hosts, key=lambda x: ipaddress.IPv4Address(x))
    
    def arp_scan(self, network: str) -> Dict[str, str]:
        """
        Scan ARP pour récupérer les adresses MAC
        """
        arp_table = {}
        
        try:
            # Utiliser nmap pour le scan ARP
            logger.info(f"Scan ARP sur {network}")
            self.nm.scan(hosts=network, arguments='-sn -n')
            
            for host in self.nm.all_hosts():
                if 'mac' in self.nm[host]['addresses']:
                    mac = self.nm[host]['addresses']['mac']
                    arp_table[host] = mac
            
            # Fallback: lire la table ARP système
            try:
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if '(' in line and ')' in line and 'at' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            ip_part = parts[1].strip('()')
                            mac_part = parts[3]
                            if ':' in mac_part and len(mac_part) == 17:
                                arp_table[ip_part] = mac_part.upper()
            except Exception as e:
                logger.debug(f"Erreur lecture ARP système: {e}")
            
            logger.info(f"Scan ARP terminé: {len(arp_table)} entrées trouvées")
            
        except Exception as e:
            logger.error(f"Erreur lors du scan ARP: {e}")
        
        return arp_table
    
    def port_scan(self, host: str, ports: str = None) -> Dict[str, Any]:
        """
        Scanner les ports d'un hôte spécifique
        """
        if ports is None:
            ports = self.default_ports
        
        port_info = {
            'open_ports': [],
            'services': [],
            'scan_time': 0
        }
        
        try:
            start_time = time.time()
            
            # Scanner les ports avec nmap
            self.nm.scan(host, ports, arguments='-sV --version-intensity 0')
            
            if host in self.nm.all_hosts():
                host_info = self.nm[host]
                
                if 'tcp' in host_info:
                    for port, port_data in host_info['tcp'].items():
                        if port_data['state'] == 'open':
                            port_info['open_ports'].append(port)
                            
                            service_info = {
                                'port': port,
                                'service': port_data.get('name', 'unknown'),
                                'product': port_data.get('product', ''),
                                'version': port_data.get('version', ''),
                                'extrainfo': port_data.get('extrainfo', '')
                            }
                            port_info['services'].append(service_info)
            
            port_info['scan_time'] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Erreur lors du scan de port pour {host}: {e}")
            port_info['error'] = str(e)
        
        return port_info
    
    def get_hostname(self, ip: str) -> str:
        """Récupérer le hostname d'une IP avec plusieurs méthodes"""
        hostname = ""
        
        # Méthode 1: Reverse DNS classique
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname and hostname != ip:
                # Nettoyer le hostname (enlever domaine si local)
                if '.' in hostname:
                    hostname = hostname.split('.')[0]
                return hostname
        except Exception:
            pass
        
        # Méthode 2: nmap hostname detection
        try:
            self.nm.scan(ip, arguments='-sn')
            if ip in self.nm.all_hosts():
                nmap_hostname = self.nm[ip].hostname()
                if nmap_hostname and nmap_hostname != ip:
                    return nmap_hostname.split('.')[0]
        except Exception:
            pass
        
        # Méthode 3: NetBIOS name (Windows)
        try:
            result = subprocess.run(
                ['nmblookup', '-A', ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '<00>' in line and 'B <ACTIVE>' in line and not '<GROUP>' in line:
                        # Format: "        333SRV          <00> -         B <ACTIVE>"
                        parts = line.strip().split()
                        if parts and not parts[0].startswith('.') and len(parts[0]) > 1:
                            netbios_name = parts[0]
                            if netbios_name and not netbios_name.startswith('MAC'):
                                return netbios_name
        except Exception:
            pass
        
        # Méthode 4: SSH banner hostname (Linux)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 22))
            if result == 0:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                sock.close()
                # Chercher hostname dans le banner SSH
                if 'SSH' in banner:
                    parts = banner.split()
                    for part in parts:
                        if not part.startswith('SSH') and not part.startswith('OpenSSH') and len(part) > 3:
                            if not any(char in part for char in ['/', '\\', '(', ')', '-']):
                                return part
            else:
                sock.close()
        except Exception:
            pass
        
        return hostname
    
    def scan_host_details(self, ip: str, include_ports: bool = True) -> Dict[str, Any]:
        """
        Scanner les détails d'un hôte spécifique
        """
        host_details = {
            'ip': ip,
            'hostname': '',
            'mac_address': '',
            'vendor': '',
            'status': 'unknown',
            'response_time': 0,
            'last_seen': time.time(),
            'services': [],
            'open_ports': []
        }
        
        try:
            start_time = time.time()
            
            # Test de connectivité
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', ip],
                capture_output=True
            )
            
            if result.returncode == 0:
                host_details['status'] = 'up'
                host_details['response_time'] = time.time() - start_time
                
                # Hostname
                host_details['hostname'] = self.get_hostname(ip)
                
                # MAC address via ARP
                arp_info = self.arp_scan(f"{ip}/32")
                if ip in arp_info:
                    host_details['mac_address'] = arp_info[ip]
                
                # Scan des ports si demandé
                if include_ports:
                    port_info = self.port_scan(ip)
                    host_details['open_ports'] = port_info['open_ports']
                    host_details['services'] = port_info['services']
            else:
                host_details['status'] = 'down'
        
        except Exception as e:
            logger.error(f"Erreur lors du scan détaillé de {ip}: {e}")
            host_details['status'] = 'error'
            host_details['error'] = str(e)
        
        return host_details
    
    def full_network_scan(self, network: str = None, include_ports: bool = True) -> Dict[str, Any]:
        """
        Effectuer un scan complet du réseau
        """
        if network is None:
            network = self.get_default_network()
            if not network:
                raise ValueError("Impossible de déterminer le réseau à scanner")
        
        logger.info(f"Début du scan complet du réseau: {network}")
        start_time = time.time()
        
        scan_results = {
            'network': network,
            'scan_time': start_time,
            'devices': [],
            'statistics': {
                'total_ips_scanned': 0,
                'active_devices': 0,
                'devices_with_ports': 0,
                'scan_duration': 0
            }
        }
        
        try:
            # Étape 1: Ping sweep pour trouver les hôtes actifs
            active_hosts = self.ping_sweep(network)
            scan_results['statistics']['total_ips_scanned'] = len(list(ipaddress.IPv4Network(network, strict=False).hosts()))
            scan_results['statistics']['active_devices'] = len(active_hosts)
            
            # Étape 2: Scan détaillé de chaque hôte actif
            def scan_single_host(ip):
                return self.scan_host_details(ip, include_ports)
            
            with ThreadPoolExecutor(max_workers=min(self.max_threads, len(active_hosts))) as executor:
                futures = {executor.submit(scan_single_host, ip): ip for ip in active_hosts}
                
                for future in as_completed(futures):
                    host_details = future.result()
                    if host_details['status'] == 'up':
                        scan_results['devices'].append(host_details)
                        
                        if host_details['open_ports']:
                            scan_results['statistics']['devices_with_ports'] += 1
            
            scan_results['statistics']['scan_duration'] = time.time() - start_time
            self.scan_results = scan_results
            self.last_scan_time = time.time()
            
            logger.info(f"Scan terminé: {len(scan_results['devices'])} appareils trouvés en {scan_results['statistics']['scan_duration']:.2f}s")
            
        except Exception as e:
            logger.error(f"Erreur lors du scan complet: {e}")
            scan_results['error'] = str(e)
        
        return scan_results
    
    def quick_scan(self, network: str = None) -> Dict[str, Any]:
        """
        Scan rapide sans ports (ping + ARP seulement)
        """
        return self.full_network_scan(network, include_ports=False)
    
    def get_device_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Récupérer les détails d'un appareil par son IP"""
        if not self.scan_results or 'devices' not in self.scan_results:
            return None
        
        for device in self.scan_results['devices']:
            if device['ip'] == ip:
                return device
        
        return None
    
    def get_device_by_mac(self, mac: str) -> Optional[Dict[str, Any]]:
        """Récupérer les détails d'un appareil par son MAC"""
        if not self.scan_results or 'devices' not in self.scan_results:
            return None
        
        mac_upper = mac.upper()
        for device in self.scan_results['devices']:
            if device.get('mac_address', '').upper() == mac_upper:
                return device
        
        return None
    
    def export_results(self, format: str = 'json') -> str:
        """Exporter les résultats du scan"""
        if format.lower() == 'json':
            return json.dumps(self.scan_results, indent=2, default=str)
        
        # Format texte simple
        output = []
        if self.scan_results and 'devices' in self.scan_results:
            output.append(f"Scan réseau: {self.scan_results['network']}")
            output.append(f"Appareils trouvés: {len(self.scan_results['devices'])}")
            output.append("-" * 50)
            
            for device in self.scan_results['devices']:
                output.append(f"IP: {device['ip']}")
                if device['hostname']:
                    output.append(f"  Hostname: {device['hostname']}")
                if device['mac_address']:
                    output.append(f"  MAC: {device['mac_address']}")
                if device['open_ports']:
                    output.append(f"  Ports ouverts: {', '.join(map(str, device['open_ports']))}")
                output.append("")
        
        return '\n'.join(output)
    
    def enrich_device_info(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichir les informations d'un appareil avec vendor et autres détails"""
        enriched = device.copy()
        
        # Enrichissement MAC Vendor
        if enriched.get('mac_address'):
            try:
                from .mac_vendor import MacVendorAPI
                vendor_api = MacVendorAPI()
                vendor_info = vendor_api.get_vendor_info(enriched['mac_address'])
                if vendor_info.get('vendor'):
                    enriched['vendor'] = vendor_info['vendor']
                    enriched['vendor_details'] = vendor_info
                    logger.debug(f"✅ Vendor lookup réussi pour {enriched['ip']}: {vendor_info['vendor']}")
                else:
                    logger.debug(f"⚠️ Vendor lookup vide pour {enriched['ip']} MAC:{enriched['mac_address']}")
            except Exception as e:
                logger.warning(f"❌ Erreur vendor lookup {enriched['ip']}: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Tentative hostname si vide
        if not enriched.get('hostname'):
            hostname = self.get_hostname(enriched['ip'])
            if hostname:
                enriched['hostname'] = hostname
        
        # Detection du type d'appareil basé sur hostname et MAC
        device_type = self.guess_device_type(enriched)
        if device_type:
            enriched['device_type'] = device_type
        
        # DÉTECTION OS AVANCÉE (nouvelle méthode)
        os_detection = self.advanced_os_detection(enriched)
        enriched['os_detected'] = os_detection['os']
        enriched['os_confidence'] = os_detection['confidence_level']
        enriched['os_all_scores'] = os_detection['all_scores']
        enriched['os_detection_details'] = os_detection['detection_details']
        
        # Mise à jour du device_type basé sur l'OS détecté si plus précis
        if os_detection['confidence'] >= 25:  # Confiance minimum
            os = os_detection['os']
            vendor = enriched.get('vendor', '').lower()
            hostname = enriched.get('hostname', '').lower()
            open_ports = enriched.get('open_ports', [])
            
            if os == 'Linux':
                if 22 in open_ports and 'raspberry' in vendor:
                    enriched['device_type'] = '🍓 Raspberry Pi'
                elif 22 in open_ports and hostname:
                    enriched['device_type'] = f'🐧 Linux ({hostname})'
                elif hostname:
                    enriched['device_type'] = f'🐧 Linux ({hostname})'
                else:
                    enriched['device_type'] = '🐧 Serveur/PC Linux'
            elif os == 'Windows':
                if 3389 in open_ports and hostname:
                    enriched['device_type'] = f'🪟 PC Windows ({hostname})'
                elif hostname:
                    enriched['device_type'] = f'💻 PC Windows ({hostname})'
                elif any(v in vendor for v in ['dell', 'hp', 'lenovo', 'asus', 'msi']):
                    enriched['device_type'] = f'💻 PC Windows ({vendor.title()})'
                else:
                    enriched['device_type'] = '🪟 Windows'
            elif os == 'Android':
                if any(v in vendor for v in ['samsung', 'lg', 'sony']) and not hostname:
                    enriched['device_type'] = f'📺 Smart TV ({vendor.title()})'
                elif any(v in vendor for v in ['huawei', 'xiaomi', 'oneplus', 'google', 'oppo']):
                    enriched['device_type'] = f'📱 Mobile ({vendor.title()})'
                elif hostname and any(pattern in hostname for pattern in ['samsung', 'lg', 'tv']):
                    enriched['device_type'] = f'📺 Smart TV ({hostname})'
                else:
                    enriched['device_type'] = '🤖 Appareil Android'
            elif os == 'iOS/macOS':
                if hostname:
                    if any(pattern in hostname for pattern in ['iphone', 'phone']):
                        enriched['device_type'] = f'📱 iPhone ({hostname})'
                    elif any(pattern in hostname for pattern in ['ipad', 'pad']):
                        enriched['device_type'] = f'📱 iPad ({hostname})'
                    elif any(pattern in hostname for pattern in ['macbook', 'mac', 'imac']):
                        enriched['device_type'] = f'💻 Mac ({hostname})'
                    else:
                        enriched['device_type'] = f'🍎 Apple ({hostname})'
                else:
                    # Sans hostname, on devine par vendor ou pattern de réponse
                    enriched['device_type'] = '🍎 iPhone/iPad'
        
        return enriched
    
    def enrich_device_info_no_vendor(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Version de enrich_device_info sans vendor lookup (fait en batch après)"""
        enriched = device.copy()
        
        # Tentative hostname si vide
        if not enriched.get('hostname'):
            hostname = self.get_hostname(enriched['ip'])
            if hostname:
                enriched['hostname'] = hostname
        
        # Detection du type d'appareil basé sur hostname et MAC
        device_type = self.guess_device_type(enriched)
        if device_type:
            enriched['device_type'] = device_type
        
        # DÉTECTION OS AVANCÉE (nouvelle méthode)
        os_detection = self.advanced_os_detection(enriched)
        enriched['os_detected'] = os_detection['os']
        enriched['os_confidence'] = os_detection['confidence_level']
        enriched['os_all_scores'] = os_detection['all_scores']
        enriched['os_detection_details'] = os_detection['detection_details']
        
        # Mise à jour du device_type basé sur l'OS détecté si plus précis
        if os_detection['confidence'] >= 25:  # Confiance minimum
            os = os_detection['os']
            vendor = enriched.get('vendor', '').lower()
            hostname = enriched.get('hostname', '').lower()
            open_ports = enriched.get('open_ports', [])
            
            if os == 'Linux':
                if 22 in open_ports and 'raspberry' in vendor:
                    enriched['device_type'] = '🍓 Raspberry Pi'
                elif 22 in open_ports and hostname:
                    enriched['device_type'] = f'🐧 Linux ({hostname})'
                elif hostname:
                    enriched['device_type'] = f'🐧 Linux ({hostname})'
                else:
                    enriched['device_type'] = '🐧 Serveur/PC Linux'
            elif os == 'Windows':
                if 3389 in open_ports and hostname:
                    enriched['device_type'] = f'🪟 PC Windows ({hostname})'
                elif hostname:
                    enriched['device_type'] = f'💻 PC Windows ({hostname})'
                elif any(v in vendor for v in ['dell', 'hp', 'lenovo', 'asus', 'msi']):
                    enriched['device_type'] = f'💻 PC Windows ({vendor.title()})'
                else:
                    enriched['device_type'] = '🪟 Windows'
            elif os == 'Android':
                if any(v in vendor for v in ['samsung', 'lg', 'sony']) and not hostname:
                    enriched['device_type'] = f'📺 Smart TV ({vendor.title()})'
                elif any(v in vendor for v in ['huawei', 'xiaomi', 'oneplus', 'google', 'oppo']):
                    enriched['device_type'] = f'📱 Mobile ({vendor.title()})'
                elif hostname and any(pattern in hostname for pattern in ['samsung', 'lg', 'tv']):
                    enriched['device_type'] = f'📺 Smart TV ({hostname})'
                else:
                    enriched['device_type'] = '🤖 Appareil Android'
            elif os == 'iOS/macOS':
                if hostname:
                    if any(pattern in hostname for pattern in ['iphone', 'phone']):
                        enriched['device_type'] = f'📱 iPhone ({hostname})'
                    elif any(pattern in hostname for pattern in ['ipad', 'pad']):
                        enriched['device_type'] = f'📱 iPad ({hostname})'
                    elif any(pattern in hostname for pattern in ['macbook', 'mac', 'imac']):
                        enriched['device_type'] = f'💻 Mac ({hostname})'
                    else:
                        enriched['device_type'] = f'🍎 Apple ({hostname})'
                else:
                    # Sans hostname, on devine par vendor ou pattern de réponse
                    enriched['device_type'] = '🍎 iPhone/iPad'
        
        return enriched
    
    def guess_device_type(self, device: Dict[str, Any]) -> str:
        """Deviner le type d'appareil basé sur les informations disponibles"""
        hostname = device.get('hostname', '').lower()
        vendor = device.get('vendor', '').lower()
        ip = device.get('ip', '')
        
        # Patterns pour différents types d'appareils
        if any(pattern in hostname for pattern in ['router', 'gateway', 'livebox', 'bbox']):
            return 'Routeur'
        elif any(pattern in hostname for pattern in ['switch', 'sw-']):
            return 'Switch'
        elif any(pattern in hostname for pattern in ['ap-', 'wifi', 'wlan']):
            return 'Point d\'accès'
        elif any(pattern in hostname for pattern in ['printer', 'print', 'hp-', 'canon']):
            return 'Imprimante'
        elif any(pattern in hostname for pattern in ['nas', 'storage', 'synology', 'qnap']):
            return 'NAS'
        elif any(pattern in hostname for pattern in ['pc-', 'desktop', 'workstation']):
            return 'PC'
        elif any(pattern in hostname for pattern in ['laptop', 'portable']):
            return 'Laptop'
        elif any(pattern in hostname for pattern in ['server', 'srv-', 'raspberry']):
            return 'Serveur'
        elif any(pattern in hostname for pattern in ['phone', 'mobile', 'android', 'iphone']):
            return 'Mobile'
        elif any(pattern in hostname for pattern in ['tablet', 'ipad']):
            return 'Tablette'
        elif any(pattern in hostname for pattern in ['macbook', 'imac', 'mac-']):
            return 'Mac'
        elif any(pattern in hostname for pattern in ['tv', 'smart', 'samsung', 'lg']):
            return 'Smart TV'
        elif any(pattern in hostname for pattern in ['iot', 'sensor', 'camera', 'bulb']):
            return 'IoT'
        
        # Basé sur vendor
        if 'apple' in vendor:
            return 'Appareil Apple'
        elif any(vendor_name in vendor for vendor_name in ['samsung', 'lg', 'sony']):
            return 'Smart TV/Mobile'
        elif any(vendor_name in vendor for vendor_name in ['cisco', 'netgear', 'linksys', 'tp-link']):
            return 'Équipement réseau'
        elif 'raspberry' in vendor or 'foundation' in vendor:
            return 'Raspberry Pi'
        
        # Basé sur IP (patterns courants)
        if ip.endswith('.1') or ip.endswith('.254'):
            return 'Routeur'
        
        return 'Inconnu'
    
    def guess_os_by_ping_pattern(self, response_time: float) -> str:
        """Estimation basique de l'OS basée sur le temps de réponse"""
        if response_time < 0.001:
            return 'Linux/Unix (très rapide)'
        elif response_time < 0.01:
            return 'Linux/macOS (rapide)'
        elif response_time < 0.05:
            return 'Windows/Mixed (normal)'
        elif response_time > 0.1:
            return 'Mobile/IoT (lent)'
        return 'Inconnu'
    
    def scan_network_range(self, network: str = None) -> List[Dict[str, Any]]:
        """Scanner rapide de la plage réseau avec enrichissement - retourne liste d'appareils"""
        result = self.quick_scan(network)
        devices = result.get('devices', [])
        
        # Enrichir chaque appareil
        enriched_devices = []
        for device in devices:
            enriched = self.enrich_device_info(device)
            enriched_devices.append(enriched)
        
        return enriched_devices
    
    def professional_network_scan(self, network: str = None) -> Dict[str, Any]:
        """
        🔥 SCANNER RÉSEAU PROFESSIONNEL COMPLET
        Détection OS, services, fingerprinting, identification précise
        """
        if network is None:
            network = self.get_default_network()
        
        logger.info(f"🚀 Démarrage scan professionnel de {network}")
        start_time = time.time()
        
        scan_results = {
            'network': network,
            'scan_type': 'professional_complete',
            'devices': [],
            'scan_time': 0,
            'summary': {},
            'timestamp': time.time()
        }
        
        try:
            # Phase 1: Découverte hôtes actifs (ping sweep + ARP)
            logger.info("📡 Phase 1: Découverte hôtes actifs")
            active_hosts = self.enhanced_host_discovery(network)
            logger.info(f"✅ {len(active_hosts)} hôtes actifs découverts")
            
            # Phase 2: Scan détaillé de chaque hôte
            logger.info("🔍 Phase 2: Analyse détaillée des hôtes")
            devices = []
            
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                future_to_ip = {
                    executor.submit(self.deep_host_analysis, ip): ip 
                    for ip in active_hosts
                }
                
                for future in as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        device_info = future.result(timeout=self.scan_timeout)
                        if device_info:
                            devices.append(device_info)
                            logger.debug(f"✅ {ip}: {device_info.get('device_type', 'Unknown')} détecté")
                    except Exception as e:
                        logger.warning(f"❌ Erreur analyse {ip}: {e}")
            
            # Phase 3: Vendor lookup en série (pour respecter rate limits)
            logger.info("🏭 Phase 3: Lookup vendors (série)")
            devices_with_vendors = self.batch_vendor_lookup(devices)
            
            # Phase 4: Tri et enrichissement final
            logger.info("🎯 Phase 4: Enrichissement et classification")
            devices_final = self.classify_and_enrich_devices(devices_with_vendors)
            
            scan_results['devices'] = devices_final
            scan_results['scan_time'] = time.time() - start_time
            scan_results['summary'] = self.generate_scan_summary(devices_final)
            
            self.scan_results = scan_results
            self.last_scan_time = time.time()
            
            logger.info(f"🏆 Scan terminé en {scan_results['scan_time']:.1f}s - {len(devices)} appareils analysés")
            return scan_results
            
        except Exception as e:
            logger.error(f"❌ Erreur scan professionnel: {e}")
            return {'error': str(e), 'devices': []}
    
    def enhanced_host_discovery(self, network: str) -> List[str]:
        """Découverte d'hôtes améliorée (ping + ARP + nmap)"""
        active_hosts = set()
        
        # Méthode 1: Ping sweep rapide
        ping_hosts = self.ping_sweep(network)
        active_hosts.update(ping_hosts)
        
        # Méthode 2: Scan ARP pour appareils silencieux
        arp_info = self.arp_scan(network)
        active_hosts.update(arp_info.keys())
        
        # Méthode 3: nmap discovery scan
        try:
            logger.debug("🔍 nmap discovery scan")
            self.nm.scan(hosts=network, arguments='-sn -T4')
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    active_hosts.add(host)
        except Exception as e:
            logger.debug(f"nmap discovery error: {e}")
        
        return sorted(list(active_hosts), key=lambda x: ipaddress.IPv4Address(x))
    
    def batch_vendor_lookup(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Lookup vendor amélioré avec mDNS et base locale étendue"""
        try:
            from .mac_vendor import MacVendorAPI
            from .extended_oui import ExtendedOUIDatabase
            from .mdns_scanner import MDNSScanner
            
            vendor_api = MacVendorAPI()
            extended_oui = ExtendedOUIDatabase()
            mdns_scanner = MDNSScanner()
            
            logger.info(f"🔍 Vendor lookup amélioré pour {len(devices)} appareils")
            
            # Phase 3.1: Vendor lookup classique + base locale étendue D'ABORD
            local_found = 0
            api_found = 0
            
            for i, device in enumerate(devices, 1):
                mac = device.get('mac_address')
                if mac and mac.strip() and (not device.get('vendor') or device.get('vendor') == ''):
                    try:
                        logger.debug(f"Vendor lookup {i}/{len(devices)}: {device['ip']} ({mac[:8]}...)")
                        
                        # Tentative base locale étendue d'abord (plus rapide)
                        local_info = extended_oui.get_comprehensive_device_info(mac)
                        if local_info['vendor'] != 'Unknown':
                            device['vendor'] = local_info['vendor']
                            device['device_type'] = local_info['device_type']
                            device['category'] = local_info['category'] 
                            device['vendor_details'] = local_info
                            device['detection_method'] = 'local_oui_extended'
                            local_found += 1
                            logger.info(f"✅ LOCAL VENDOR: {device['ip']} ({mac[:8]}) = {local_info['vendor']}")
                            continue
                        
                        # Fallback API macvendors.com
                        vendor_info = vendor_api.get_vendor_info(mac)
                        
                        if vendor_info.get('vendor') and vendor_info['vendor'] != 'Unknown':
                            device['vendor'] = vendor_info['vendor']
                            device['vendor_details'] = vendor_info
                            device['detection_method'] = 'macvendors_api'
                            api_found += 1
                            logger.info(f"✅ API VENDOR: {device['ip']} = {vendor_info['vendor']}")
                        else:
                            device['detection_method'] = 'no_mac'
                    except Exception as e:
                        logger.warning(f"❌ Erreur vendor lookup {device['ip']}: {e}")
                        device['detection_method'] = 'no_mac'
            
            logger.info(f"� Vendor lookup local/API: {local_found} local + {api_found} API")
            
            # Phase 3.2: mDNS/Bonjour pour appareils Apple (après vendor lookup pour éviter l'écrasement)
            logger.info("🍎 Scan mDNS/Bonjour pour appareils Apple...")
            unknown_ips = [d['ip'] for d in devices if not d.get('vendor') or d.get('vendor') == '']
            
            # Scan mDNS complet
            mdns_devices = mdns_scanner.scan_bonjour_services()
            
            # Test rapide iOS Companion pour les IPs sans vendor
            apple_quick = mdns_scanner.quick_apple_detection(unknown_ips[:8])
            
            # Merge des résultats mDNS avec LOGS DÉTAILLÉS
            mdns_found = 0
            logger.info(f"🔍 mDNS merge: {len(mdns_devices)} devices + {len(apple_quick)} quick")
            
            for ip, mdns_info in {**mdns_devices, **apple_quick}.items():
                logger.info(f"🍎 mDNS candidat {ip}: {mdns_info}")
                for device in devices:
                    if device['ip'] == ip:
                        old_vendor = device.get('vendor', '')
                        if not device.get('vendor') or device.get('vendor') == '':
                            device['vendor'] = mdns_info.get('vendor', '')
                            device['device_type'] = mdns_info.get('device_type', device.get('device_type', ''))
                            device['mdns_services'] = mdns_info.get('services', [])
                            device['detection_method'] = mdns_info.get('detection_method', 'mDNS')
                            mdns_found += 1
                            logger.info(f"✅ mDNS APPLIQUÉ: {ip} '{old_vendor}' → '{device['vendor']}' ({device['device_type']})")
                        else:
                            logger.info(f"⏭️ mDNS IGNORÉ: {ip} a déjà vendor '{old_vendor}'")
            
            logger.info(f"🍎 mDNS: {mdns_found} appareils Apple découverts")
            
            # Phase 3.3: Fallback intelligent pour MACs randomisées
            logger.info("🎭 Détection des MACs randomisées...")
            randomized_count = 0
            context_found = 0
            
            for device in devices:
                if not device.get('vendor') or device.get('vendor') == '':
                    mac = device.get('mac_address', '')
                    if self.is_randomized_mac(mac):
                        randomized_count += 1
                        logger.info(f"🎭 MAC randomisée détectée: {device['ip']} ({mac[:8]}...)")
                        
                        # Essayer de deviner depuis le contexte (SEULEMENT si fiable)
                        context_vendor = self.guess_vendor_from_context(device)
                        if context_vendor:
                            device['vendor'] = context_vendor
                            device['detection_method'] = 'hostname_based'
                            context_found += 1
                            logger.info(f"✅ HOSTNAME VENDOR: {device['ip']} = {context_vendor}")
                        else:
                            # Approche neutre et factuelle
                            device['vendor'] = 'Appareil avec MAC Privée'
                            device['detection_method'] = 'privacy_mac'
                            logger.info(f"� PRIVACY MAC: {device['ip']} = Adresse MAC randomisée")
            
            if randomized_count > 0:
                logger.info(f"🔒 MACs privées: {randomized_count} détectées, {context_found} identifiées par hostname")
            
            # Finalisation des appareils sans vendor
            for device in devices:
                if not device.get('vendor'):
                    device['vendor'] = ''
                    device['detection_method'] = 'no_mac'
            
            total_found = mdns_found + local_found + api_found + context_found
            logger.info(f"🎯 Vendor lookup terminé: {total_found}/{len(devices)} identifiés")
            logger.info(f"   🏠 Local: {local_found}, 🌐 API: {api_found}, 📱 mDNS: {mdns_found}, 🎭 Contexte: {context_found}")
            
            # RE-DÉTECTION OS après vendor lookup (important pour Apple mDNS)
            logger.info("🔄 Re-détection OS avec vendors...")
            for device in devices:
                if device.get('vendor'):  # Si vendor trouvé après scan
                    old_os = device.get('os_detected', 'N/A')
                    vendor = device.get('vendor', 'N/A')
                    logger.info(f"🔄 Re-détection {device['ip']}: vendor='{vendor}', old_os='{old_os}'")
                    
                    os_detection = self.advanced_os_detection(device)
                    
                    device['os_detected'] = os_detection['os']
                    device['os_confidence'] = os_detection['confidence_level']
                    device['os_all_scores'] = os_detection['all_scores']
                    device['os_detection_details'] = os_detection['detection_details']
                    
                    logger.info(f"✅ Re-détection {device['ip']}: '{old_os}' → '{device['os_detected']}'")
                else:
                    logger.info(f"⏭️ Re-détection ignorée {device['ip']}: pas de vendor")
                    
            return devices
            
        except Exception as e:
            logger.error(f"Erreur batch vendor lookup: {e}")
            return devices
    
    def deep_host_analysis(self, ip: str) -> Dict[str, Any]:
        """Analyse approfondie d'un hôte (OS, services, fingerprinting)"""
        device = {
            'ip': ip,
            'hostname': '',
            'mac_address': '',
            'vendor': '',
            'device_type': 'Inconnu',
            'os_family': 'Inconnu',
            'os_details': '',
            'confidence': 0,
            'open_ports': [],
            'services': [],
            'response_time': 0,
            'last_seen': time.time(),
            'fingerprint': {},
            'status': 'up',
            'detection_method': 'pending'
        }
        
        try:
            start_time = time.time()
            
            # 1. Informations de base (hostname, MAC)
            device['hostname'] = self.get_hostname(ip)
            device['mac_address'] = self.get_mac_address(ip)
            device['response_time'] = time.time() - start_time
            
            # 2. Scan des ports pour OS detection
            device.update(self.scan_ports_for_os_detection(ip))
            
            # 3. Fingerprinting OS basé sur les ports ouverts
            device.update(self.fingerprint_operating_system(device['open_ports'], device))
            
            # 4. Identification du type d'appareil
            device['device_type'] = self.identify_device_type(device)
            
            # 5. DÉTECTION OS AVANCÉE (vendor lookup se fait en batch après)
            device = self.enrich_device_info_no_vendor(device)
            
            return device
            
        except Exception as e:
            logger.debug(f"Erreur analyse {ip}: {e}")
            return device
    
    def scan_ports_for_os_detection(self, ip: str) -> Dict[str, Any]:
        """Scan ciblé des ports pour détection OS"""
        result = {'open_ports': [], 'services': []}
        
        try:
            # Scan rapide des ports OS-specific
            port_args = f"-p {self.os_detection_ports} -T4 --open"
            self.nm.scan(ip, arguments=port_args)
            
            if ip in self.nm.all_hosts():
                host_info = self.nm[ip]
                
                for protocol in host_info.all_protocols():
                    ports = host_info[protocol].keys()
                    for port in ports:
                        port_info = host_info[protocol][port]
                        if port_info['state'] == 'open':
                            result['open_ports'].append(port)
                            
                            # Identification du service
                            service_name = port_info.get('name', f'port-{port}')
                            service_product = port_info.get('product', '')
                            service_version = port_info.get('version', '')
                            
                            service = {
                                'port': port,
                                'service': service_name,
                                'product': service_product,
                                'version': service_version
                            }
                            result['services'].append(service)
                            
        except Exception as e:
            logger.debug(f"Port scan error for {ip}: {e}")
        
        return result
    
    def fingerprint_operating_system(self, open_ports: List[int], device_info: Dict) -> Dict[str, Any]:
        """Fingerprinting OS basé sur ports ouverts + autres indices"""
        os_scores = {}
        hostname = device_info.get('hostname', '').lower()
        vendor = device_info.get('vendor', '').lower()
        
        # Score basé sur les ports caractéristiques
        for os_family, characteristic_ports in self.os_fingerprints.items():
            score = 0
            for port in characteristic_ports:
                if port in open_ports:
                    score += 1
            
            if score > 0:
                os_scores[os_family] = score / len(characteristic_ports)
        
        # Bonus basés sur hostname
        hostname_patterns = {
            'windows': ['pc-', 'desktop', 'win', 'workstation'],
            'linux': ['ubuntu', 'debian', 'linux', 'server'],
            'macos': ['mac', 'imac', 'macbook'],
            'ios': ['iphone', 'ipad', 'ios'],
            'android': ['android', 'galaxy', 'pixel'],
            'router': ['router', 'gateway', 'livebox', 'bbox'],
            'printer': ['printer', 'hp-', 'canon', 'epson']
        }
        
        for os_family, patterns in hostname_patterns.items():
            if any(pattern in hostname for pattern in patterns):
                os_scores[os_family] = os_scores.get(os_family, 0) + 0.5
        
        # Bonus basés sur vendor
        vendor_patterns = {
            'windows': ['microsoft', 'dell', 'hp', 'lenovo'],
            'macos': ['apple'],
            'ios': ['apple'],
            'android': ['samsung', 'google', 'lg', 'huawei'],
            'router': ['cisco', 'netgear', 'linksys', 'tp-link'],
            'linux': ['raspberry']
        }
        
        for os_family, patterns in vendor_patterns.items():
            if any(pattern in vendor for pattern in patterns):
                os_scores[os_family] = os_scores.get(os_family, 0) + 0.3
        
        # Déterminer l'OS le plus probable
        if os_scores:
            best_os = max(os_scores, key=os_scores.get)
            confidence = min(os_scores[best_os] * 100, 95)  # Max 95% confidence
            
            return {
                'os_family': best_os.title(),
                'confidence': int(confidence),
                'os_details': self.get_os_details(best_os, open_ports),
                'fingerprint': os_scores
            }
        
        return {
            'os_family': 'Inconnu',
            'confidence': 0,
            'os_details': 'Impossible à déterminer',
            'fingerprint': {}
        }
    
    def get_os_details(self, os_family: str, open_ports: List[int]) -> str:
        """Détails spécifiques de l'OS basés sur les ports"""
        details = {
            'windows': {
                135: 'Windows avec RPC',
                3389: 'Windows avec RDP activé',
                445: 'Windows avec partage SMB',
                139: 'Windows NetBIOS'
            },
            'linux': {
                22: 'Linux avec SSH',
                111: 'Linux avec RPC',
                5353: 'Linux avec Avahi/mDNS'
            },
            'macos': {
                548: 'macOS avec AFP',
                62078: 'macOS avec services iOS sync'
            },
            'ios': {
                62078: 'iPhone/iPad détecté'
            },
            'router': {
                23: 'Routeur avec Telnet',
                80: 'Interface web routeur'
            }
        }
        
        os_details = []
        if os_family in details:
            for port in open_ports:
                if port in details[os_family]:
                    os_details.append(details[os_family][port])
        
        return ' | '.join(os_details) if os_details else f'{os_family.title()} détecté'
    
    def identify_device_type(self, device: Dict[str, Any]) -> str:
        """Identification précise du type d'appareil"""
        hostname = device.get('hostname', '').lower()
        vendor = device.get('vendor', '').lower()
        os_family = device.get('os_family', '').lower()
        open_ports = device.get('open_ports', [])
        ip = device.get('ip', '')
        mac = device.get('mac_address', '')
        
        # 🎯 NOUVELLES RÈGLES POUR APPAREILS MOBILES/IoT
        
        # 1. Identification par vendor (très précise)
        vendor_identification = {
            'apple': '📱 iPhone/iPad/Mac',
            'samsung': '📱 Samsung (Mobile/TV)',
            'lg': '📺 LG Smart TV',
            'sony': '📺 Sony (TV/Console)',
            'dyson': '🏠 Dyson (IoT)',
            'google': '📱 Google/Android',
            'huawei': '📱 Huawei Mobile',
            'xiaomi': '📱 Xiaomi',
            'amazon': '🏠 Amazon (Echo/IoT)',
            'microsoft': '💻 Microsoft',
            'nintendo': '🎮 Nintendo Console',
            'philips': '🏠 Philips Hue/IoT',
            'ring': '🏠 Ring (Sécurité)',
            'tesla': '🚗 Tesla',
            'sonos': '🔊 Sonos Audio',
            'roku': '📺 Roku Media',
            'hp': '🖨️ HP (Imprimante)',
            'canon': '🖨️ Canon Imprimante',
            'epson': '🖨️ Epson Imprimante',
            'brother': '🖨️ Brother Imprimante',
            'nest': '🏠 Google Nest',
            'tp-link': '🌐 TP-Link (Réseau)',
            'netgear': '🌐 Netgear (Réseau)',
            'cisco': '🌐 Cisco (Réseau)',
            'linksys': '🌐 Linksys (Réseau)',
            'asus': '🌐 ASUS (Réseau/PC)',
            'dell': '💻 Dell PC',
            'lenovo': '💻 Lenovo PC',
            'raspberry': '🔧 Raspberry Pi'
        }
        
        for vendor_key, device_type in vendor_identification.items():
            if vendor_key in vendor:
                # Affinage pour certains vendors ambigus
                if vendor_key == 'samsung':
                    if not open_ports:  # Mobile/TV sans ports ouverts
                        return '📱 Samsung Mobile/TV'
                    else:
                        return '📺 Samsung Smart TV'
                elif vendor_key == 'apple':
                    if not open_ports:  # iPhone/iPad typiquement
                        return '📱 iPhone/iPad'
                    elif 22 in open_ports:  # Mac avec SSH
                        return '🍎 Mac'
                    else:
                        return '📱 Apple Mobile'
                elif vendor_key == 'asus':
                    if any(p in open_ports for p in [22, 80, 443]):
                        return '🌐 ASUS Routeur'
                    else:
                        return '💻 ASUS PC'
                else:
                    return device_type
        
        # 2. Détection par patterns MAC (pour vendors inconnus)
        if mac:
            mac_patterns = {
                # Plages MAC connues pour certains constructeurs
                '00:50:56': '💻 VMware VM',
                '08:00:27': '💻 VirtualBox VM',
                '52:54:00': '💻 QEMU VM',
            }
            
            mac_prefix = mac[:8]
            if mac_prefix in mac_patterns:
                return mac_patterns[mac_prefix]
        
        # 3. Règles existantes (routeurs/infrastructure réseau)
        if (ip.endswith('.1') or ip.endswith('.254')) and any(p in open_ports for p in [53, 80, 443]):
            return '🌐 Routeur/Gateway'
        
        if any(pattern in hostname for pattern in ['router', 'gateway', 'livebox', 'bbox', 'freebox']):
            return '🌐 Routeur Internet'
        
        # 4. Serveurs et ordinateurs avec ports ouverts
        if 'raspberry' in hostname or 'raspberry' in vendor:
            return '🔧 Raspberry Pi'
        
        if any(pattern in hostname for pattern in ['server', 'srv-', 'nas', 'synology', 'qnap']):
            return '🖥️ Serveur/NAS'
        
        if 22 in open_ports and os_family == 'linux':
            return '🐧 Serveur Linux'
        
        # 5. Windows avec détection spécifique
        if os_family == 'windows':
            if 3389 in open_ports:  # RDP
                return '💻 PC Windows (RDP)'
            elif any(p in open_ports for p in [135, 139, 445]):  # SMB/NetBIOS
                return '💻 PC Windows'
            else:
                return '💻 Windows'
        
        # 6. macOS
        if os_family == 'macos':
            if any(pattern in hostname for pattern in ['macbook', 'imac']):
                return '🍎 Mac ' + ('Book' if 'book' in hostname else 'Desktop')
            return '🍎 Mac'
        
        if os_family == 'linux' and 22 in open_ports:
            return '🐧 Linux Desktop/Server'
        
        # 7. Mobiles par OS détecté
        if os_family == 'ios' or 'iphone' in hostname or 'ipad' in hostname:
            return '📱 iPhone/iPad'
        
        if os_family == 'android' or any(pattern in hostname for pattern in ['android', 'galaxy', 'pixel']):
            return '📱 Android'
        
        # 8. Imprimantes
        if 9100 in open_ports or 631 in open_ports:  # JetDirect, IPP
            return '🖨️ Imprimante'
        
        if any(pattern in hostname for pattern in ['printer', 'hp-', 'canon', 'epson', 'brother']):
            return '🖨️ Imprimante'
        
        # 9. Smart TV / Media (sans vendor spécifique)
        if any(pattern in hostname for pattern in ['tv', 'smart', 'android-tv', 'roku', 'chromecast']):
            return '📺 Smart TV'
        
        # 10. IoT / Domotique
        if any(pattern in hostname for pattern in ['iot', 'sensor', 'camera', 'bulb', 'echo', 'alexa', 'nest']):
            return '🏠 IoT/Domotique'
        
        # 11. Fallback intelligent basé sur comportement
        if not open_ports and vendor != 'unknown':
            # Appareil sans ports ouverts mais avec vendor → probablement mobile/IoT
            if any(mobile_hint in vendor for mobile_hint in ['electronics', 'technology', 'inc', 'limited']):
                return '📱 Appareil mobile/IoT'
        
        # 12. Fallback basé sur OS détecté
        if os_family == 'windows':
            return '💻 Windows'
        elif os_family == 'linux':
            return '🐧 Linux'
        elif os_family == 'macos':
            return '🍎 macOS'
        elif os_family in ['ios', 'android']:
            return '📱 Mobile'
        
        # 13. Derniers patterns
        if not open_ports and vendor and vendor != 'unknown':
            return f'📱 {vendor.title()}'
        
        # 14. Si tout échoue
        if vendor and vendor != 'unknown':
            return f'❓ {vendor.title()}'
        
        return '❓ Appareil inconnu'
    
    def get_mac_address(self, ip: str) -> str:
        """Récupérer adresse MAC via ARP avec fallback"""
        try:
            # Méthode 1: ARP table système
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ip in line and ':' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and len(part) == 17:
                            return part.upper()
            
            # Méthode 2: nmap
            arp_info = self.arp_scan(f"{ip}/32")
            return arp_info.get(ip, '')
            
        except Exception:
            return ''
    
    def get_vendor_from_mac(self, mac_address: str) -> str:
        """Récupérer vendor depuis MAC avec cache local"""
        try:
            from .mac_vendor import MacVendorAPI
            vendor_api = MacVendorAPI()
            vendor_info = vendor_api.get_vendor_info(mac_address)
            return vendor_info.get('vendor', 'Inconnu')
        except Exception:
            return 'Inconnu'
    
    def is_randomized_mac(self, mac_address: str) -> bool:
        """Détecter si une MAC est randomisée (privacy feature)"""
        if not mac_address or len(mac_address) < 17:
            return False
        
        try:
            # Extraire le premier octet
            first_octet = mac_address.split(':')[0]
            first_byte = int(first_octet, 16)
            
            # Bit 1 (locally administered) = MAC randomisée
            return bool(first_byte & 0x02)
        except:
            return False
    
    def guess_vendor_from_context(self, device: Dict) -> str:
        """Deviner le vendor à partir du contexte pour MACs randomisées - APPROCHE CONSERVATIVE"""
        hostname = device.get('hostname', '').lower()
        
        # SEULEMENT si hostname est très spécifique et fiable
        xiaomi_patterns = ['redmi', 'mi-', 'xiaomi', 'poco']
        samsung_patterns = ['galaxy', 'samsung', 'sm-']
        apple_patterns = ['iphone', 'ipad', 'macbook', 'imac']
        
        # Détection fiable par hostname uniquement
        if any(pattern in hostname for pattern in xiaomi_patterns):
            return 'Xiaomi Inc.'
        
        if any(pattern in hostname for pattern in samsung_patterns):
            return 'Samsung Electronics'
            
        if any(pattern in hostname for pattern in apple_patterns):
            return 'Apple Inc.'
        
        # SINON : Rester neutre, pas de spéculation OS-based
        return ''
    
    def classify_and_enrich_devices(self, devices: List[Dict]) -> List[Dict]:
        """Classification finale et enrichissement"""
        
        # ÉTAPE 1: Mise à jour des device_types maintenant qu'on a les vendors
        for device in devices:
            self.update_device_type_with_vendor(device)
        
        # ÉTAPE 2: Calcul des scores de confiance et catégorisation
        for device in devices:
            # Calcul de score de confiance global
            confidence_factors = []
            
            if device.get('os_family') != 'Inconnu':
                confidence_factors.append(device.get('confidence', 0))
            
            if device.get('vendor') and device.get('vendor') != 'Inconnu':
                confidence_factors.append(70)
            
            if device.get('open_ports'):
                confidence_factors.append(60)
            
            if device.get('hostname'):
                confidence_factors.append(50)
            
            device['global_confidence'] = int(sum(confidence_factors) / len(confidence_factors)) if confidence_factors else 20
            
            # Catégorisation
            device_type = device.get('device_type', '')
            if any(cat in device_type for cat in ['💻', '🐧', '🍎']):
                device['category'] = 'Ordinateurs'
            elif any(cat in device_type for cat in ['📱']):
                device['category'] = 'Mobiles'
            elif any(cat in device_type for cat in ['🌐']):
                device['category'] = 'Réseau'
            elif any(cat in device_type for cat in ['🖨️', '📺', '🏠']):
                device['category'] = 'Périphériques'
            elif any(cat in device_type for cat in ['🔧', '🖥️']):
                device['category'] = 'Serveurs'
            else:
                device['category'] = 'Autres'
        
        # Tri par catégorie puis IP
        return sorted(devices, key=lambda x: (x.get('category', 'ZZZ'), ipaddress.IPv4Address(x['ip'])))
    
    def update_device_type_with_vendor(self, device: Dict[str, Any]):
        """Mise à jour du device_type maintenant qu'on a le vendor"""
        vendor = device.get('vendor', '').lower()
        os = device.get('os_detected', 'Inconnu')
        hostname = device.get('hostname', '').lower()
        open_ports = device.get('open_ports', [])
        
        if not vendor or vendor == 'unknown':
            return  # Pas de vendor, on garde le device_type existant
        
        # Mise à jour basée sur vendor + OS + détails spéciaux
        if os == 'Linux':
            if 'raspberry' in vendor or 'foundation' in vendor:
                device['device_type'] = '🍓 Raspberry Pi'
            elif 22 in open_ports and 3389 in open_ports:
                # Cas spécial Linux + RDP (xrdp)
                if hostname:
                    device['device_type'] = f'🐧 Linux Server ({hostname}) + RDP'
                elif any(pc_vendor in vendor for pc_vendor in ['asus', 'msi', 'dell', 'hp', 'lenovo']):
                    device['device_type'] = f'🐧 Linux PC ({vendor.title()}) + RDP'
                else:
                    device['device_type'] = '🐧 Linux Server + RDP'
            elif hostname:
                if any(server_pattern in hostname for server_pattern in ['server', 'srv', 'ubuntu', 'debian', 'centos']):
                    device['device_type'] = f'🖥️ Serveur Linux ({hostname})'
                else:
                    device['device_type'] = f'🐧 Linux ({hostname})'
            elif any(pc_vendor in vendor for pc_vendor in ['asus', 'msi', 'dell', 'hp', 'lenovo']):
                device['device_type'] = f'🐧 Linux ({vendor.title()})'
            else:
                device['device_type'] = '🐧 Serveur/PC Linux'
                
        elif os == 'Windows':
            if hostname:
                if any(server_pattern in hostname for server_pattern in ['server', 'srv', 'dc', 'ad']):
                    device['device_type'] = f'🖥️ Serveur Windows ({hostname})'
                else:
                    device['device_type'] = f'🪟 PC Windows ({hostname})'
            elif any(pc_vendor in vendor for pc_vendor in ['asus', 'msi', 'dell', 'hp', 'lenovo']):
                device['device_type'] = f'💻 PC Windows ({vendor.title()})'
            elif 'freebox' in vendor or 'sas' in vendor:
                device['device_type'] = f'🌐 Routeur ({vendor.title()})'
            else:
                device['device_type'] = '🪟 Windows'
                
        elif os == 'Android':
            if 'samsung' in vendor:
                if hostname and 'tv' in hostname:
                    device['device_type'] = f'📺 Smart TV Samsung ({hostname})'
                elif hostname and any(model in hostname for model in ['galaxy', 'sm-', 'samsung']):
                    device['device_type'] = f'� Samsung ({hostname})'
                else:
                    device['device_type'] = f'�📺 Smart TV Samsung' if not open_ports else f'📱 Mobile Samsung'
            elif any(iot_vendor in vendor for iot_vendor in ['dyson', 'philips', 'xiaomi']):
                device['device_type'] = f'🏠 IoT ({vendor.title()})'
            elif 'espressif' in vendor:
                device['device_type'] = f'🔧 Microcontrôleur ({vendor.title()})'
            elif any(mobile_vendor in vendor for mobile_vendor in ['huawei', 'oneplus', 'google', 'oppo']):
                # Essayer d'extraire le modèle du hostname
                if hostname:
                    device['device_type'] = f'📱 {vendor.title()} ({hostname})'
                else:
                    device['device_type'] = f'📱 Mobile ({vendor.title()})'
            else:
                if hostname:
                    device['device_type'] = f'🤖 Android ({hostname})'
                else:
                    device['device_type'] = '🤖 Appareil Android'
                
        elif os == 'iOS/macOS':
            if 'apple' in vendor:
                if hostname:
                    if any(pattern in hostname for pattern in ['iphone', 'phone']):
                        # Extraire modèle iPhone si disponible
                        model = self.extract_apple_model(hostname)
                        device['device_type'] = f'📱 iPhone ({model or hostname})'
                    elif any(pattern in hostname for pattern in ['ipad', 'pad']):
                        model = self.extract_apple_model(hostname)
                        device['device_type'] = f'📱 iPad ({model or hostname})'
                    elif any(pattern in hostname for pattern in ['macbook', 'mac', 'imac']):
                        model = self.extract_apple_model(hostname)
                        device['device_type'] = f'💻 Mac ({model or hostname})'
                    else:
                        device['device_type'] = f'🍎 Apple ({hostname})'
                else:
                    device['device_type'] = '🍎 iPhone/iPad'
            else:
                device['device_type'] = '🍎 iPhone/iPad'
        
        # Cas spéciaux basés uniquement sur vendor (si OS non détecté)
        elif os == 'Inconnu':
            if 'freebox' in vendor:
                device['device_type'] = f'🌐 Routeur Freebox'
            elif 'dyson' in vendor:
                device['device_type'] = f'🏠 Aspirateur Dyson'
            elif 'samsung' in vendor:
                device['device_type'] = f'📺 Smart TV Samsung'
            elif 'espressif' in vendor:
                device['device_type'] = f'🔧 Microcontrôleur ESP32'
            elif any(pc_vendor in vendor for pc_vendor in ['asus', 'msi', 'dell', 'hp', 'lenovo']):
                device['device_type'] = f'💻 PC ({vendor.title()})'
            elif 'apple' in vendor:
                device['device_type'] = '🍎 Appareil Apple'
    
    def extract_apple_model(self, hostname: str) -> str:
        """Extraire le modèle d'appareil Apple depuis hostname ou données mDNS"""
        if not hostname:
            return ""
        
        hostname = hostname.lower()
        
        # Patterns iPhone
        iphone_patterns = {
            'iphone13': 'iPhone 13',
            'iphone12': 'iPhone 12', 
            'iphone11': 'iPhone 11',
            'iphonex': 'iPhone X',
            'iphone8': 'iPhone 8',
            'iphonese': 'iPhone SE',
            'iphone15': 'iPhone 15',
            'iphone14': 'iPhone 14'
        }
        
        # Patterns iPad
        ipad_patterns = {
            'ipadpro': 'iPad Pro',
            'ipadair': 'iPad Air',
            'ipadmini': 'iPad Mini',
            'ipad': 'iPad'
        }
        
        # Patterns Mac
        mac_patterns = {
            'macbookpro': 'MacBook Pro',
            'macbookair': 'MacBook Air',
            'macbook': 'MacBook',
            'imacpro': 'iMac Pro',
            'imac': 'iMac',
            'macmini': 'Mac Mini',
            'macstudio': 'Mac Studio'
        }
        
        # Chercher les patterns
        for pattern, model in {**iphone_patterns, **ipad_patterns, **mac_patterns}.items():
            if pattern in hostname:
                return model
        
        # Fallback: retourner hostname nettoyé
        return hostname.title()
    
    def generate_scan_summary(self, devices: List[Dict]) -> Dict[str, Any]:
        """Générer résumé du scan"""
        summary = {
            'total_devices': len(devices),
            'by_category': {},
            'by_os': {},
            'active_services': set(),
            'security_notes': []
        }
        
        for device in devices:
            # Par catégorie
            category = device.get('category', 'Autres')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            # Par OS
            os_family = device.get('os_family', 'Inconnu')
            summary['by_os'][os_family] = summary['by_os'].get(os_family, 0) + 1
            
            # Services actifs
            for service in device.get('services', []):
                summary['active_services'].add(f"{service.get('service', 'unknown')}:{service.get('port', 0)}")
            
            # Notes de sécurité
            open_ports = device.get('open_ports', [])
            if 23 in open_ports:  # Telnet
                summary['security_notes'].append(f"⚠️ Telnet détecté sur {device['ip']}")
            if 21 in open_ports:  # FTP
                summary['security_notes'].append(f"⚠️ FTP détecté sur {device['ip']}")
            if 3389 in open_ports and device.get('ip', '').startswith('192.168.'):  # RDP sur réseau local
                summary['security_notes'].append(f"ℹ️ RDP actif sur {device['ip']}")
        
        summary['active_services'] = list(summary['active_services'])
        return summary
    
    def scan_network_detailed(self, network: str = None) -> Dict[str, Any]:
        """Scanner détaillé de la plage réseau"""
        return self.full_network_scan(network, include_ports=True)
    
    def scan_host_detailed(self, ip: str) -> Dict[str, Any]:
        """Scanner détaillé d'un hôte spécifique"""
        return self.scan_host_details(ip, include_ports=True)
    
    def advanced_os_detection(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Détection OS avancée basée sur multiple indices"""
        ip = device['ip']
        open_ports = device.get('open_ports', [])
        services = device.get('services', [])
        hostname = device.get('hostname', '').lower()
        vendor = device.get('vendor', '').lower()
        response_time = device.get('response_time', 0)
        
        os_confidence = {}
        os_details = {}
        
        # === DÉTECTION PAR HOSTNAME ===
        if hostname:
            if any(pattern in hostname for pattern in ['ubuntu', 'debian', 'centos', 'fedora', 'linux']):
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 40
                os_details['hostname_hint'] = f"Hostname contient: {hostname}"
            elif any(pattern in hostname for pattern in ['win', 'windows', 'pc-', 'desktop']):
                os_confidence['Windows'] = os_confidence.get('Windows', 0) + 35
                os_details['hostname_hint'] = f"Hostname Windows: {hostname}"
            elif 'raspberry' in hostname or 'pi' in hostname:
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 50
                os_details['hostname_hint'] = "Raspberry Pi détecté"
            elif any(pattern in hostname for pattern in ['android', 'phone', 'mobile']):
                os_confidence['Android'] = os_confidence.get('Android', 0) + 45
                os_details['hostname_hint'] = f"Mobile Android: {hostname}"
        
        # === DÉTECTION PAR VENDOR ===
        if vendor:
            if any(v in vendor for v in ['apple', 'cupertino']):
                # Apple peut être iPhone, iPad, MacBook, etc.
                os_confidence['iOS/macOS'] = os_confidence.get('iOS/macOS', 0) + 60
                os_details['vendor_hint'] = "Vendor Apple détecté"
            elif any(v in vendor for v in ['microsoft', 'dell', 'hp', 'lenovo', 'asus', 'msi']):
                # Détection intelligente PC : SSH+RDP = Linux, sinon Windows
                if 22 in open_ports and 3389 in open_ports:
                    # SSH + RDP = Linux avec xrdp (cas prioritaire)
                    os_confidence['Linux'] = os_confidence.get('Linux', 0) + 40
                    os_details['vendor_hint'] = f"Vendor PC: {vendor} avec SSH+RDP = Linux+xrdp"
                elif 22 in open_ports and not (139 in open_ports or 445 in open_ports):
                    # SSH seul = Linux
                    os_confidence['Linux'] = os_confidence.get('Linux', 0) + 25
                    os_details['vendor_hint'] = f"Vendor PC: {vendor} avec SSH = Linux"
                else:
                    # Autres cas = Windows
                    os_confidence['Windows'] = os_confidence.get('Windows', 0) + 30
                    os_details['vendor_hint'] = f"Vendor PC: {vendor}"
            elif any(v in vendor for v in ['raspberry', 'foundation']):
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 55
                os_details['vendor_hint'] = "Raspberry Pi Foundation"
            elif any(v in vendor for v in ['samsung', 'lg', 'sony']):
                # Samsung/LG/Sony = Smart TV ou mobile
                os_confidence['Android'] = os_confidence.get('Android', 0) + 45
                os_details['vendor_hint'] = f"Vendor TV/Mobile: {vendor}"
            elif any(v in vendor for v in ['huawei', 'xiaomi', 'oneplus', 'google', 'oppo', 'vivo']):
                # Vendors mobiles Android
                os_confidence['Android'] = os_confidence.get('Android', 0) + 55
                os_details['vendor_hint'] = f"Vendor mobile Android: {vendor}"
        
        # === DÉTECTION PAR PORTS ET SERVICES ===
        for port in open_ports:
            if port == 22:  # SSH
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 25
                os_details['ssh_detected'] = "SSH ouvert (Linux probable)"
            elif port == 3389:  # RDP
                os_confidence['Windows'] = os_confidence.get('Windows', 0) + 45
                os_details['rdp_detected'] = "RDP ouvert (Windows)"
            elif port == 139 or port == 445:  # SMB
                os_confidence['Windows'] = os_confidence.get('Windows', 0) + 30
                os_details['smb_detected'] = "SMB ouvert (Windows)"
            elif port == 80 or port == 443:  # HTTP/HTTPS
                # Peut être n'importe quoi, bonus léger pour Linux (serveurs)
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 5
                os_details['web_server'] = "Serveur web détecté"
            elif port == 23:  # Telnet
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 10
                os_details['telnet'] = "Telnet ouvert"
            elif port == 21:  # FTP
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 10
                os_details['ftp'] = "FTP ouvert"
            elif port == 53:  # DNS
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 15
                os_details['dns'] = "Serveur DNS"
        
        # === DÉTECTION PAR TEMPS DE RÉPONSE ===
        if response_time:
            if response_time < 0.002:
                # Très rapide = Linux/Unix probable
                os_confidence['Linux'] = os_confidence.get('Linux', 0) + 10
                os_details['ping_speed'] = "Ping très rapide (Linux probable)"
            elif response_time > 0.05:
                # Lent = mobile/IoT probable
                os_confidence['Android'] = os_confidence.get('Android', 0) + 5
                os_confidence['iOS/macOS'] = os_confidence.get('iOS/macOS', 0) + 5
                os_details['ping_speed'] = "Ping lent (mobile probable)"
        
        # === DÉTECTION PAR ABSENCE DE PORTS ===
        if not open_ports:
            # Pas de ports ouverts = mobile ou firewall strict
            # iPhone/iPad ont tendance à être très fermés
            if vendor and 'apple' in vendor.lower():
                os_confidence['iOS/macOS'] = os_confidence.get('iOS/macOS', 0) + 30
                os_details['no_ports_apple'] = "Apple sans ports ouverts = iPhone/iPad probable"
            else:
                os_confidence['Android'] = os_confidence.get('Android', 0) + 15
                os_confidence['iOS/macOS'] = os_confidence.get('iOS/macOS', 0) + 15
                os_confidence['Windows'] = os_confidence.get('Windows', 0) + 5  # Windows avec firewall
                os_details['no_ports'] = "Aucun port ouvert (mobile/firewall)"
        
        # === COMBINAISONS SPÉCIALES ===
        # Si SSH + RDP = probablement Linux avec RDP forwarding/WSL
        if 22 in open_ports and 3389 in open_ports:
            os_confidence['Linux'] = os_confidence.get('Linux', 0) + 30
            os_details['ssh_rdp_combo'] = "SSH + RDP = Linux avec tunneling/WSL probable"
        # Si RDP + pas d'autres indices Linux = Windows sûr
        elif 3389 in open_ports and not (22 in open_ports):
            os_confidence['Windows'] = os_confidence.get('Windows', 0) + 20
        # Si SSH + pas de RDP = Linux probable
        elif 22 in open_ports and not (3389 in open_ports or 139 in open_ports or 445 in open_ports):
            os_confidence['Linux'] = os_confidence.get('Linux', 0) + 20
        
        # Trouver l'OS le plus probable
        if os_confidence:
            # PRIORITÉ ABSOLUE: SSH + RDP = Linux avec xrdp (surpasse tous les scores)
            if 22 in open_ports and 3389 in open_ports:
                best_os = "Linux (xrdp)"
                confidence = 95
                os_details['linux_rdp_override'] = f"SSH + RDP détectés = Linux avec xrdp forcé (scores ignorés)"
            
            # PRIORITÉ VENDOR: Si vendor Apple détecté, forcer iOS même avec scores égaux
            elif vendor and 'apple' in vendor and 'iOS/macOS' in os_confidence:
                best_os = "iOS/macOS"
                confidence = max(os_confidence['iOS/macOS'], 30)  # Minimum 30 pour Apple
                os_details['apple_vendor_override'] = f"Vendor Apple détecté = iOS forcé (scores: {dict(os_confidence)})"
            
            # Sinon, prendre le score maximum
            else:
                best_os = max(os_confidence, key=os_confidence.get)
                confidence = os_confidence[best_os]
            
            # Niveau de confiance
            if confidence >= 60:
                confidence_level = "Très élevée"
            elif confidence >= 40:
                confidence_level = "Élevée"
            elif confidence >= 25:
                confidence_level = "Moyenne"
            else:
                confidence_level = "Faible"
                
            return {
                'os': best_os,
                'confidence': confidence,
                'confidence_level': confidence_level,
                'all_scores': dict(os_confidence),
                'detection_details': os_details
            }
        else:
            return {
                'os': 'Inconnu',
                'confidence': 0,
                'confidence_level': 'Aucune',
                'all_scores': {},
                'detection_details': {'reason': 'Pas assez d\'indices'}
            }