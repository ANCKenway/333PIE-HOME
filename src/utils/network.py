"""
Utilitaires réseau partagés
Fonctions communes pour tous les services réseau
"""

import subprocess
import socket
import ipaddress
from typing import Optional, Dict, List

def ping_host(ip: str) -> bool:
    """Test de ping rapide"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def get_hostname_netbios(ip: str) -> Optional[str]:
    """Récupération hostname via NetBIOS"""
    try:
        # nmblookup
        result = subprocess.run(
            ['nmblookup', '-A', ip],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if '<00>' in line and not line.strip().startswith('Looking'):
                    hostname = line.split()[0].strip()
                    if hostname and hostname != ip:
                        return hostname
        
        # Fallback nbtscan
        result = subprocess.run(
            ['nbtscan', ip],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
                        
    except Exception:
        pass
    
    return None

def get_mac_address_arp(ip: str) -> Optional[str]:
    """Récupération adresse MAC via ARP"""
    try:
        result = subprocess.run(
            ['arp', '-n', ip],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                        if ':' in mac and len(mac) == 17:
                            return mac.upper()
    except Exception:
        pass
    
    return None

def scan_ports_quick(ip: str, ports: List[int] = None) -> List[int]:
    """Scan rapide des ports les plus courants"""
    if ports is None:
        ports = [22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 3389]
    
    open_ports = []
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            continue
    
    return open_ports

def get_network_range() -> str:
    """Détection automatique de la plage réseau"""
    try:
        # Récupération de l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Calcul de la plage réseau (assume /24)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return str(network)
    except:
        return "192.168.1.0/24"

def is_private_ip(ip: str) -> bool:
    """Vérifie si l'IP est privée"""
    try:
        return ipaddress.IPv4Address(ip).is_private
    except:
        return False