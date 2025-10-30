"""
333HOME Agent - Hub Discovery
==============================

Auto-détection du Hub 333HOME sur le réseau.

Méthodes de découverte (par priorité):
1. **mDNS/Bonjour** : 333pie.local (réseau local)
2. **Tailscale API** : Scan devices VPN pour trouver 333PIE
3. **Fallback** : IPs connues (192.168.1.150, 100.115.207.11)

Usage:
    from hub_discovery import discover_hub
    
    hub_url = discover_hub()
    # Retourne: "ws://333pie.local:8000" ou "ws://IP:8000"
"""

import socket
import requests
import subprocess
import json
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


# Configuration
HUB_HOSTNAME = "333pie.local"  # mDNS hostname du Hub
HUB_PORT = 8000
HUB_WS_PATH = "/api/ws/agents"
CONNECTION_TIMEOUT = 2  # secondes

# Fallback IPs connues
FALLBACK_IPS = [
    "192.168.1.150",     # Local LAN
    "100.115.207.11",    # Tailscale VPN
]


def resolve_mdns(hostname: str, timeout: float = CONNECTION_TIMEOUT) -> Optional[str]:
    """
    Résout un hostname mDNS en adresse IP.
    
    Args:
        hostname: Hostname mDNS (ex: 333pie.local)
        timeout: Timeout résolution
        
    Returns:
        Adresse IP ou None si échec
    """
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(hostname)
        logger.info(f"✅ mDNS résolu: {hostname} → {ip}")
        return ip
    except socket.gaierror:
        logger.debug(f"❌ mDNS échec: {hostname}")
        return None
    finally:
        socket.setdefaulttimeout(None)


def get_tailscale_devices() -> List[Dict]:
    """
    Récupère la liste des devices Tailscale via CLI.
    
    Returns:
        Liste des devices Tailscale avec IP et hostname
    """
    try:
        # tailscale status --json
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return []
        
        status = json.loads(result.stdout)
        devices = []
        
        # Parser peers
        for peer_id, peer in status.get("Peer", {}).items():
            devices.append({
                "hostname": peer.get("HostName", ""),
                "ip": peer.get("TailscaleIPs", [None])[0],
                "online": peer.get("Online", False)
            })
        
        return devices
        
    except Exception as e:
        logger.debug(f"Tailscale CLI non disponible: {e}")
        return []


def find_hub_in_tailscale() -> Optional[str]:
    """
    Cherche le Hub dans les devices Tailscale.
    
    Returns:
        IP du Hub ou None
    """
    devices = get_tailscale_devices()
    
    for device in devices:
        # Chercher device avec hostname contenant "333pie" ou "333PIE"
        hostname = device.get("hostname", "").lower()
        if "333pie" in hostname and device.get("online"):
            ip = device.get("ip")
            if ip:
                logger.info(f"✅ Hub trouvé via Tailscale: {hostname} → {ip}")
                return ip
    
    return None


def test_hub_reachable(ip: str, port: int = HUB_PORT, timeout: float = CONNECTION_TIMEOUT) -> bool:
    """
    Teste si le Hub est joignable sur une IP donnée.
    
    Args:
        ip: Adresse IP du Hub
        port: Port du Hub
        timeout: Timeout connexion en secondes
        
    Returns:
        True si le Hub répond, False sinon
    """
    try:
        # Test 1: Connexion TCP simple (plus rapide que HTTP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result != 0:
            return False
        
        # Test 2: Vérifier que c'est bien le Hub 333HOME
        try:
            response = requests.get(
                f"http://{ip}:{port}/api/agents",
                timeout=timeout
            )
            # Si on a une réponse (même 404), c'est le bon serveur
            return response.status_code in [200, 404, 403]
        except:
            # Si HTTP échoue mais TCP OK, on accepte quand même
            return True
            
    except Exception as e:
        logger.debug(f"Hub non joignable sur {ip}:{port} - {e}")
        return False


def discover_hub() -> str:
    """
    Découvre automatiquement l'URL du Hub.
    
    Méthodes tentées (par ordre):
    1. mDNS: 333pie.local
    2. Tailscale: Scan devices pour trouver 333PIE
    3. Fallback: IPs connues
    
    Returns:
        URL WebSocket du Hub (ws://HOST:PORT/api/ws/agents)
    """
    logger.info("🔍 Découverte automatique du Hub 333HOME...")
    
    # Méthode 1: mDNS (réseau local)
    logger.info(f"   Tentative 1: mDNS ({HUB_HOSTNAME})...")
    mdns_ip = resolve_mdns(HUB_HOSTNAME)
    if mdns_ip and test_hub_reachable(mdns_ip):
        url = f"ws://{mdns_ip}:{HUB_PORT}{HUB_WS_PATH}"
        logger.info(f"✅ Hub trouvé via mDNS: {url}")
        return url
    
    # Méthode 2: Tailscale (VPN)
    logger.info("   Tentative 2: Scan Tailscale VPN...")
    ts_ip = find_hub_in_tailscale()
    if ts_ip and test_hub_reachable(ts_ip):
        url = f"ws://{ts_ip}:{HUB_PORT}{HUB_WS_PATH}"
        logger.info(f"✅ Hub trouvé via Tailscale: {url}")
        return url
    
    # Méthode 3: Fallback IPs connues
    logger.info("   Tentative 3: IPs fallback...")
    for ip in FALLBACK_IPS:
        logger.info(f"      Test {ip}...")
        if test_hub_reachable(ip):
            url = f"ws://{ip}:{HUB_PORT}{HUB_WS_PATH}"
            logger.info(f"✅ Hub trouvé sur IP fallback: {url}")
            return url
    
    # Aucun Hub trouvé - retourner première IP fallback par défaut
    logger.warning(f"⚠️  Aucun Hub joignable, fallback sur {FALLBACK_IPS[0]}")
    return f"ws://{FALLBACK_IPS[0]}:{HUB_PORT}{HUB_WS_PATH}"


def get_hub_http_url(ws_url: str) -> str:
    """
    Convertit une URL WebSocket en URL HTTP pour l'API REST.
    
    Args:
        ws_url: URL WebSocket (ws://...)
        
    Returns:
        URL HTTP (http://...)
    """
    return ws_url.replace("ws://", "http://").replace(HUB_WS_PATH, "")


if __name__ == "__main__":
    # Test découverte
    logging.basicConfig(level=logging.INFO)
    hub_url = discover_hub()
    print(f"\nHub URL: {hub_url}")
    print(f"HTTP URL: {get_hub_http_url(hub_url)}")

