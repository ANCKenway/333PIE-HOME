"""
Détection mobile avancée - Techniques poussées pour identifier iPhone/Android
Focus: REDMI 12 (Xiaomi) et iPhone 13 Pro
"""

import subprocess
import re
import json
from typing import Dict, Optional, Tuple, List

class AdvancedMobileDetector:
    """Détecteur mobile avancé avec techniques poussées"""
    
    def __init__(self):
        self.device_fingerprints = self._load_device_fingerprints()
    
    def _load_device_fingerprints(self) -> Dict:
        """Signatures connues d'appareils mobiles"""
        return {
            "xiaomi_redmi": {
                "hostnames": ["redmi", "xiaomi", "mi-", "pocophone", "poco"],
                "mdns_services": ["_miio._udp", "_miot._tcp"],
                "http_agents": ["MIUI", "Xiaomi", "Redmi"],
                "mac_indicators": ["8CFABA", "50EC50", "781D8A", "F8A45F"],
                "device_names": ["Redmi", "POCO", "Mi ", "Xiaomi"]
            },
            "apple_iphone": {
                "hostnames": ["iphone", "ios", "apple"],
                "mdns_services": ["_airplay._tcp", "_apple-mobdev2._tcp", "_homekit._tcp"],
                "http_agents": ["iPhone", "iOS", "Mobile Safari"],
                "mac_indicators": ["randomized"],
                "device_names": ["iPhone", "iOS"]
            },
            "samsung_android": {
                "hostnames": ["samsung", "galaxy", "sm-"],
                "mdns_services": ["_samsung._tcp", "_smartview._tcp"],
                "http_agents": ["Samsung", "Galaxy"],
                "mac_indicators": ["7C11CB", "E8039A", "78F882"],
                "device_names": ["Galaxy", "Samsung"]
            }
        }
    
    def analyze_mobile_device(self, ip: str, mac: str, hostname: str = None) -> Dict:
        """Analyse poussée d'un appareil mobile"""
        results = {
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "detection_methods": [],
            "device_info": {},
            "confidence": 0
        }
        
        print(f"    🔍 Analyse mobile poussée pour {ip}")
        
        # 1. Analyse mDNS/Bonjour approfondie
        mdns_info = self._analyze_mdns_services(ip)
        if mdns_info:
            results["detection_methods"].append("mDNS")
            results["device_info"].update(mdns_info)
            results["confidence"] += 30
        
        # 2. Analyse HTTP/User-Agent si possible
        http_info = self._analyze_http_fingerprint(ip)
        if http_info:
            results["detection_methods"].append("HTTP")
            results["device_info"].update(http_info)
            results["confidence"] += 25
        
        # 3. Analyse UPnP avancée
        upnp_info = self._analyze_upnp_detailed(ip)
        if upnp_info:
            results["detection_methods"].append("UPnP")
            results["device_info"].update(upnp_info)
            results["confidence"] += 20
        
        # 4. Scan de ports mobiles spécifiques
        mobile_ports = self._scan_mobile_ports(ip)
        if mobile_ports:
            results["detection_methods"].append("Mobile Ports")
            results["device_info"]["mobile_ports"] = mobile_ports
            results["confidence"] += 15
        
        # 5. Analyse du hostname pour patterns
        if hostname:
            hostname_analysis = self._analyze_hostname_patterns(hostname)
            if hostname_analysis:
                results["detection_methods"].append("Hostname Pattern")
                results["device_info"].update(hostname_analysis)
                results["confidence"] += 20
        
        # 6. Détection finale basée sur tous les indices
        final_detection = self._determine_device_type(results)
        results["final_detection"] = final_detection
        
        return results
    
    def _analyze_mdns_services(self, ip: str) -> Dict:
        """Analyse approfondie des services mDNS/Bonjour"""
        services_info = {}
        
        # Services spécifiques à analyser
        mobile_services = [
            "_airplay._tcp",           # Apple AirPlay
            "_apple-mobdev2._tcp",     # Apple Mobile Device
            "_homekit._tcp",           # Apple HomeKit
            "_companion-link._tcp",    # Apple Companion
            "_miio._udp",              # Xiaomi IoT
            "_miot._tcp",              # Xiaomi IoT
            "_googlecast._tcp",        # Google Cast (Android)
            "_spotify-connect._tcp",   # Spotify Connect
            "_raop._tcp",              # AirTunes (Apple)
            "_device-info._tcp",       # Device Info
            "_samsung._tcp",           # Samsung
            "_smartview._tcp"          # Samsung Smart View
        ]
        
        for service in mobile_services:
            try:
                result = subprocess.run([
                    'avahi-browse', '-r', '-t', service, '-p', '--resolve'
                ], capture_output=True, text=True, timeout=3)
                
                for line in result.stdout.split('\n'):
                    if ip in line and ';' in line:
                        parts = line.split(';')
                        if len(parts) >= 7:
                            service_name = parts[2]
                            device_name = parts[3]
                            txt_record = parts[9] if len(parts) > 9 else ""
                            
                            services_info[service] = {
                                "name": service_name,
                                "device": device_name,
                                "txt": txt_record
                            }
                            
                            # Analyse du TXT record pour plus d'infos
                            if txt_record:
                                device_details = self._parse_txt_record(txt_record)
                                services_info[service]["details"] = device_details
                            
                            print(f"      📡 Service {service}: {device_name}")
            except:
                continue
        
        return services_info
    
    def _parse_txt_record(self, txt_record: str) -> Dict:
        """Parse les TXT records mDNS pour extraire infos device"""
        details = {}
        
        # Recherche de patterns connus
        patterns = {
            "model": r"model=([^\\s]+)",
            "os": r"os=([^\\s]+)", 
            "version": r"version=([^\\s]+)",
            "device": r"device=([^\\s]+)",
            "name": r"name=([^\\s]+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, txt_record, re.IGNORECASE)
            if match:
                details[key] = match.group(1)
        
        return details
    
    def _analyze_http_fingerprint(self, ip: str) -> Dict:
        """Analyse User-Agent HTTP pour identification"""
        http_info = {}
        
        # Ports HTTP potentiels
        http_ports = [80, 443, 8080, 8443, 5000]
        
        for port in http_ports:
            try:
                # Test simple avec curl pour récupérer headers
                protocol = "https" if port in [443, 8443] else "http"
                result = subprocess.run([
                    'curl', '-m', '3', '-s', '-I', '--insecure',
                    f'{protocol}://{ip}:{port}/'
                ], capture_output=True, text=True, timeout=5)
                
                if result.stdout:
                    headers = result.stdout
                    
                    # Recherche User-Agent dans les headers
                    for line in headers.split('\n'):
                        if 'server:' in line.lower():
                            server = line.split(':')[1].strip()
                            http_info["server"] = server
                            
                            # Détecter mobile dans server
                            if any(mobile in server.lower() for mobile in ['android', 'ios', 'mobile', 'iphone']):
                                http_info["mobile_detected"] = True
                                
                        # Parfois on trouve des infos dans d'autres headers
                        elif 'x-' in line.lower() and any(term in line.lower() for term in ['device', 'model', 'version']):
                            http_info["custom_header"] = line.strip()
                
                if http_info:
                    break  # Premier port qui répond
                    
            except:
                continue
        
        return http_info
    
    def _analyze_upnp_detailed(self, ip: str) -> Dict:
        """Analyse UPnP détaillée pour mobiles"""
        upnp_info = {}
        
        try:
            # Scan UPnP avec nmap script détaillé
            result = subprocess.run([
                'nmap', '-sU', '-p', '1900', '--script=upnp-info', ip
            ], capture_output=True, text=True, timeout=10)
            
            output = result.stdout
            
            # Recherche de friendlyName et deviceType
            patterns = {
                "friendly_name": r"friendlyName:\s*(.+)",
                "device_type": r"deviceType:\s*(.+)",
                "manufacturer": r"manufacturer:\s*(.+)",
                "model_name": r"modelName:\s*(.+)",
                "model_number": r"modelNumber:\s*(.+)"
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    upnp_info[key] = value
                    
                    # Détecter mobile dans les infos UPnP
                    if any(mobile in value.lower() for mobile in ['android', 'iphone', 'mobile', 'phone', 'redmi', 'xiaomi']):
                        upnp_info["mobile_detected"] = True
                        
        except:
            pass
        
        return upnp_info
    
    def _scan_mobile_ports(self, ip: str) -> List[int]:
        """Scan de ports spécifiques aux mobiles"""
        mobile_ports = [
            5353,  # mDNS
            62078, # Apple Mobile Device
            58888, # Xiaomi
            8009,  # Google Cast
            7000,  # AirPlay
            49152, # UPnP/DLNA commun
            49153,
            49154
        ]
        
        open_ports = []
        
        try:
            ports_str = ','.join(map(str, mobile_ports))
            result = subprocess.run([
                'nmap', '-p', ports_str, '--open', '-T4', ip
            ], capture_output=True, text=True, timeout=15)
            
            for line in result.stdout.split('\n'):
                if '/tcp' in line and 'open' in line:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
                elif '/udp' in line and 'open' in line:
                    port = int(line.split('/')[0])
                    open_ports.append(port)
                    
        except:
            pass
        
        return open_ports
    
    def _analyze_hostname_patterns(self, hostname: str) -> Dict:
        """Analyse patterns dans le hostname"""
        analysis = {}
        
        if not hostname or hostname.lower() in ["unknown", "nbt"]:
            return analysis
        
        hostname_lower = hostname.lower()
        
        # Patterns Xiaomi/REDMI
        if any(pattern in hostname_lower for pattern in ['redmi', 'xiaomi', 'mi-', 'poco']):
            analysis["brand"] = "Xiaomi"
            analysis["type"] = "Android Phone"
            if 'redmi' in hostname_lower:
                analysis["model_line"] = "Redmi"
        
        # Patterns Apple
        elif any(pattern in hostname_lower for pattern in ['iphone', 'ios', 'apple']):
            analysis["brand"] = "Apple"
            analysis["type"] = "iPhone"
        
        # Patterns Samsung
        elif any(pattern in hostname_lower for pattern in ['samsung', 'galaxy', 'sm-']):
            analysis["brand"] = "Samsung"
            analysis["type"] = "Android Phone"
        
        return analysis
    
    def _determine_device_type(self, results: Dict) -> Dict:
        """Détermination finale du type d'appareil"""
        detection = {
            "brand": "Unknown",
            "model": "Unknown",
            "type": "Unknown",
            "confidence": results["confidence"]
        }
        
        device_info = results["device_info"]
        
        # Analyse par priorité des méthodes
        
        # 1. Recherche Xiaomi/REDMI dans tous les champs
        xiaomi_indicators = []
        for key, value in device_info.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str) and any(term in subvalue.lower() for term in ['xiaomi', 'redmi', 'mi-', 'miui']):
                        xiaomi_indicators.append(f"{key}.{subkey}: {subvalue}")
            elif isinstance(value, str) and any(term in value.lower() for term in ['xiaomi', 'redmi', 'mi-', 'miui']):
                xiaomi_indicators.append(f"{key}: {value}")
        
        if xiaomi_indicators:
            detection["brand"] = "Xiaomi"
            detection["type"] = "Android Phone"
            if any('redmi' in ind.lower() for ind in xiaomi_indicators):
                detection["model"] = "Redmi"
            detection["indicators"] = xiaomi_indicators
            detection["confidence"] += 40
        
        # 2. Recherche Apple/iPhone
        apple_indicators = []
        for key, value in device_info.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str) and any(term in subvalue.lower() for term in ['iphone', 'ios', 'apple', 'airplay']):
                        apple_indicators.append(f"{key}.{subkey}: {subvalue}")
            elif isinstance(value, str) and any(term in value.lower() for term in ['iphone', 'ios', 'apple', 'airplay']):
                apple_indicators.append(f"{key}: {value}")
        
        if apple_indicators:
            detection["brand"] = "Apple"
            detection["type"] = "iPhone"
            detection["indicators"] = apple_indicators
            detection["confidence"] += 40
        
        return detection