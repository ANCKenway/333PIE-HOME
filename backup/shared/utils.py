"""
Utilitaires partagés pour 333HOME
"""
import logging
import json
import subprocess
import re
from pathlib import Path

def setup_logging(name="333HOME", level=logging.INFO):
    """Configure le logging basique"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def ping_host(ip, timeout=1):
    """Ping simple d'un hôte"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', str(timeout), ip], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def validate_ip(ip):
    """Valide une adresse IP"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def validate_mac(mac):
    """Valide une adresse MAC"""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def format_mac(mac):
    """Formate une adresse MAC"""
    if not mac:
        return ""
    return mac.upper().replace('-', ':')

def load_json_file(filepath, default=None):
    """Charge un fichier JSON"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return default or {}

def save_json_file(filepath, data):
    """Sauvegarde un fichier JSON"""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False