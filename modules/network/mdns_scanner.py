"""
Scanner mDNS/Bonjour pour la détection d'appareils Apple et IoT
Complément au scanner réseau principal pour les appareils "cachés"
"""

import socket
import struct
import time
import threading
import logging
import subprocess
from typing import Dict, List, Set, Any, Optional
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MDNSScanner:
    def __init__(self):
        self.mdns_multicast = "224.0.0.251"
        self.mdns_port = 5353
        self.timeout = 3.0
        self.apple_services = [
            "_airplay._tcp.local",
            "_raop._tcp.local", 
            "_homekit._tcp.local",
            "_companion-link._tcp.local",
            "_sleep-proxy._udp.local",
            "_device-info._tcp.local",
            "_http._tcp.local",
            "_airport._tcp.local",
            "_airdrop._tcp.local",
            "_rdlink._tcp.local"
        ]
        self.discovered_devices = {}
        
    def create_mdns_query(self, service_name: str) -> bytes:
        """Créer une requête mDNS pour un service spécifique"""
        # Transaction ID
        transaction_id = 0x0000
        
        # Flags (standard query)
        flags = 0x0000
        
        # Questions count
        questions = 1
        
        # Answer/Authority/Additional counts
        answers = authority = additional = 0
        
        # Header
        header = struct.pack('!HHHHHH', transaction_id, flags, questions, answers, authority, additional)
        
        # Question section
        question = b''
        for part in service_name.split('.'):
            question += struct.pack('B', len(part)) + part.encode('ascii')
        question += b'\x00'  # End of name
        
        # Query type (PTR = 12) and class (IN = 1)
        question += struct.pack('!HH', 12, 1)
        
        return header + question
    
    def parse_mdns_response(self, data: bytes, source_ip: str) -> Optional[Dict[str, Any]]:
        """Parser une réponse mDNS"""
        try:
            if len(data) < 12:
                return None
                
            # Parse header
            transaction_id, flags, questions, answers, authority, additional = struct.unpack('!HHHHHH', data[:12])
            
            if answers == 0:
                return None
            
            device_info = {
                'ip': source_ip,
                'services': [],
                'txt_records': {},
                'device_name': '',
                'device_type': 'mDNS Device',
                'vendor': '',
                'confidence': 'medium'
            }
            
            # Parse answers (simplification - extraction basique)
            offset = 12
            
            # Skip questions
            for _ in range(questions):
                while offset < len(data) and data[offset] != 0:
                    offset += 1
                offset += 5  # Null terminator + type + class
            
            # Parse answer records
            for _ in range(min(answers, 10)):  # Limite pour éviter les boucles infinies
                if offset >= len(data) - 10:
                    break
                    
                # Skip name (simplified)
                while offset < len(data) and data[offset] != 0 and data[offset] < 64:
                    offset += data[offset] + 1
                if offset < len(data):
                    offset += 1
                
                if offset + 10 > len(data):
                    break
                    
                # Parse type, class, TTL, data length
                record_type, record_class, ttl, data_length = struct.unpack('!HHIH', data[offset:offset+10])
                offset += 10
                
                if offset + data_length > len(data):
                    break
                
                record_data = data[offset:offset+data_length]
                offset += data_length
                
                # Analyse du type d'enregistrement
                if record_type == 16:  # TXT record
                    txt_data = self.parse_txt_record(record_data)
                    device_info['txt_records'].update(txt_data)
                elif record_type == 12:  # PTR record
                    service_name = self.parse_domain_name(record_data)
                    device_info['services'].append(service_name)
            
            # Détection Apple basée sur les services
            if any(apple_svc in str(device_info['services']) for apple_svc in ['_airplay', '_raop', '_homekit', '_companion']):
                device_info['vendor'] = 'Apple Inc.'
                device_info['confidence'] = 'high'
                
                # Détection spécifique du type d'appareil Apple
                if '_airplay' in str(device_info['services']):
                    device_info['device_type'] = '📺 Apple TV / AirPlay'
                elif '_companion' in str(device_info['services']):
                    device_info['device_type'] = '📱 iPhone/iPad'
                elif '_homekit' in str(device_info['services']):
                    device_info['device_type'] = '🏠 HomeKit Device'
                else:
                    device_info['device_type'] = '🍎 Apple Device'
            
            return device_info
            
        except Exception as e:
            logger.debug(f"Erreur parsing mDNS: {e}")
            return None
    
    def parse_txt_record(self, data: bytes) -> Dict[str, str]:
        """Parser un enregistrement TXT"""
        txt_data = {}
        offset = 0
        
        while offset < len(data):
            if offset >= len(data):
                break
            length = data[offset]
            offset += 1
            
            if offset + length > len(data):
                break
                
            record = data[offset:offset+length].decode('utf-8', errors='ignore')
            offset += length
            
            if '=' in record:
                key, value = record.split('=', 1)
                txt_data[key] = value
            else:
                txt_data[record] = ''
        
        return txt_data
    
    def parse_domain_name(self, data: bytes) -> str:
        """Parser un nom de domaine depuis les données DNS"""
        try:
            name = ""
            offset = 0
            
            while offset < len(data):
                length = data[offset]
                if length == 0:
                    break
                if length > 63:  # Compression pointer
                    break
                    
                offset += 1
                if offset + length > len(data):
                    break
                    
                part = data[offset:offset+length].decode('utf-8', errors='ignore')
                name += part + "."
                offset += length
            
            return name.rstrip('.')
        except:
            return ""
    
    def send_mdns_queries(self, interface_ip: str = None) -> Dict[str, Any]:
        """Envoyer des requêtes mDNS et écouter les réponses"""
        discovered = {}
        
        try:
            # Socket d'envoi
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Socket d'écoute
            listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_sock.bind(('', self.mdns_port))
            listen_sock.settimeout(self.timeout)
            
            # Rejoindre le groupe multicast
            mreq = struct.pack('4sl', socket.inet_aton(self.mdns_multicast), socket.INADDR_ANY)
            listen_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            # Envoyer les requêtes pour les services Apple
            for service in self.apple_services:
                query = self.create_mdns_query(service)
                send_sock.sendto(query, (self.mdns_multicast, self.mdns_port))
                time.sleep(0.1)  # Petit délai entre les requêtes
            
            # Écouter les réponses
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = listen_sock.recvfrom(1024)
                    source_ip = addr[0]
                    
                    device_info = self.parse_mdns_response(data, source_ip)
                    if device_info and device_info['services']:
                        if source_ip not in discovered:
                            discovered[source_ip] = device_info
                        else:
                            # Merge services and txt records
                            discovered[source_ip]['services'].extend(device_info['services'])
                            discovered[source_ip]['txt_records'].update(device_info['txt_records'])
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"Erreur réception mDNS: {e}")
                    continue
            
            send_sock.close()
            listen_sock.close()
            
        except Exception as e:
            logger.error(f"Erreur scanner mDNS: {e}")
        
        return discovered
    
    def scan_bonjour_services(self) -> Dict[str, Any]:
        """Scanner Bonjour/mDNS pour les appareils cachés"""
        logger.info("🔍 Scan mDNS/Bonjour pour appareils Apple...")
        
        discovered = self.send_mdns_queries()
        
        # Post-traitement des résultats
        for ip, device in discovered.items():
            # Enrichir les informations basées sur les TXT records
            txt = device['txt_records']
            
            if 'model' in txt:
                device['model'] = txt['model']
                if 'iPhone' in txt['model']:
                    device['device_type'] = f"📱 iPhone ({txt['model']})"
                elif 'iPad' in txt['model']:
                    device['device_type'] = f"📱 iPad ({txt['model']})"
                elif 'Mac' in txt['model']:
                    device['device_type'] = f"💻 Mac ({txt['model']})"
                elif 'AppleTV' in txt['model']:
                    device['device_type'] = f"📺 Apple TV ({txt['model']})"
            
            if 'fn' in txt:  # Friendly name
                device['device_name'] = txt['fn']
            
            if 'osxvers' in txt:  # macOS version
                device['os_version'] = txt['osxvers']
                device['os_detected'] = 'macOS'
            elif 'srcvers' in txt:  # iOS version
                device['os_version'] = txt['srcvers'] 
                device['os_detected'] = 'iOS'
        
        logger.info(f"✅ mDNS scan terminé: {len(discovered)} appareils Apple découverts")
        return discovered
    
    def quick_apple_detection(self, target_ips: List[str]) -> Dict[str, Any]:
        """Détection rapide Apple pour IPs spécifiques"""
        apple_devices = {}
        
        for ip in target_ips:
            device_info = {}
            detected = False
            
            # Test 1: Port iOS Companion (62078)
            if self.test_ios_companion_port(ip):
                device_info = {
                    'ip': ip,
                    'device_type': '📱 iPhone/iPad (Companion)',
                    'vendor': 'Apple Inc.',
                    'os_detected': 'iOS',
                    'confidence': 'high',
                    'detection_method': 'iOS Companion Port'
                }
                detected = True
            
            # Test 2: Ports AirPlay/Bonjour communs
            elif self.test_apple_ports(ip):
                device_info = {
                    'ip': ip,
                    'device_type': '🍎 Appareil Apple (AirPlay)',
                    'vendor': 'Apple Inc.',
                    'os_detected': 'iOS/macOS',
                    'confidence': 'medium',
                    'detection_method': 'Apple Ports'
                }
                detected = True
            
            # Test 3: Pattern de réponse TCP (Apple a des timings spécifiques)
            elif self.test_apple_tcp_pattern(ip):
                device_info = {
                    'ip': ip,
                    'device_type': '🍎 Possible iPhone (Pattern TCP)',
                    'vendor': 'Apple Inc.',
                    'os_detected': 'iOS',
                    'confidence': 'low',
                    'detection_method': 'TCP Pattern'
                }
                detected = True
            
            if detected:
                apple_devices[ip] = device_info
        
        return apple_devices
    
    def test_ios_companion_port(self, ip: str) -> bool:
        """Test du port Companion spécifique iOS"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex((ip, 62078))  # Port iOS Companion
            sock.close()
            return result == 0
        except:
            return False
    
    def test_apple_ports(self, ip: str) -> bool:
        """Test des ports Apple communs"""
        apple_ports = [
            5353,   # mDNS
            7000,   # AirPlay
            7001,   # AirPlay
            49152,  # AirPlay range start
            49153,  # AirPlay range
            3689,   # DAAP (iTunes)
            5000,   # AirPlay
        ]
        
        open_count = 0
        for port in apple_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    open_count += 1
                    if open_count >= 2:  # Au moins 2 ports Apple ouverts
                        return True
            except:
                continue
        
        return False
    
    def test_apple_tcp_pattern(self, ip: str) -> bool:
        """Test pattern TCP spécifique iOS (timing, fenêtre TCP)"""
        try:
            import time
            start_time = time.time()
            
            # Test connexion HTTP avec timing
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            result = sock.connect_ex((ip, 80))
            
            if result == 0:
                # Mesurer temps de réponse
                response_time = time.time() - start_time
                
                # Envoyer requête HTTP simple
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
                response = sock.recv(512)
                sock.close()
                
                # Pattern iOS : réponse rapide mais connection fermée rapidement
                if 0.001 < response_time < 0.1 and len(response) < 100:
                    return True
            else:
                sock.close()
            
            # Test ping timing (iOS a des patterns spécifiques)
            ping_result = subprocess.run(
                ['ping', '-c', '3', '-W', '1000', ip],
                capture_output=True,
                text=True
            )
            
            if ping_result.returncode == 0:
                # Analyser les temps de ping iOS
                lines = ping_result.stdout.split('\n')
                times = []
                for line in lines:
                    if 'time=' in line:
                        try:
                            time_str = line.split('time=')[1].split(' ')[0]
                            times.append(float(time_str))
                        except:
                            continue
                
                # iOS tend à avoir des temps de ping très réguliers
                if len(times) >= 2:
                    avg_time = sum(times) / len(times)
                    variance = sum((t - avg_time) ** 2 for t in times) / len(times)
                    
                    # Pattern iOS : ping moyen 1-10ms avec très faible variance
                    if 1.0 < avg_time < 10.0 and variance < 1.0:
                        return True
            
        except Exception:
            pass
        
        return False