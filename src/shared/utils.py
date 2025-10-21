"""
🔧 333HOME - Utilitaires partagés
Fonctions helpers utilisées à travers l'application
"""

import re
import socket
import ipaddress
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import hashlib
import json


def is_valid_ip(ip: str) -> bool:
    """Vérifier si une chaîne est une IP valide"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_mac(mac: str) -> bool:
    """Vérifier si une chaîne est une adresse MAC valide"""
    # Format XX:XX:XX:XX:XX:XX ou XX-XX-XX-XX-XX-XX
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))


def normalize_mac(mac: str) -> str:
    """Normaliser une adresse MAC au format XX:XX:XX:XX:XX:XX"""
    if not mac:
        return ""
    
    # Supprimer les séparateurs
    clean_mac = re.sub(r'[:-]', '', mac.upper())
    
    # Reformater
    if len(clean_mac) == 12:
        return ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))
    
    return mac


def get_hostname() -> str:
    """Obtenir le hostname de la machine"""
    return socket.gethostname()


def get_local_ip() -> Optional[str]:
    """Obtenir l'IP locale de la machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def format_bytes(bytes_count: int) -> str:
    """Formater une taille en bytes en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_duration(seconds: float) -> str:
    """Formater une durée en secondes en format lisible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}j"


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formater une datetime"""
    return dt.strftime(format)


def parse_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parser une chaîne datetime"""
    try:
        return datetime.strptime(dt_str, format)
    except (ValueError, TypeError):
        return None


def time_ago(timestamp: float) -> str:
    """Convertir un timestamp en format 'il y a X temps'"""
    now = datetime.now().timestamp()
    diff = now - timestamp
    
    if diff < 60:
        return "à l'instant"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"il y a {minutes}min"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"il y a {hours}h"
    else:
        days = int(diff / 86400)
        return f"il y a {days}j"


def generate_id(data: str) -> str:
    """Générer un ID unique à partir de données"""
    return hashlib.md5(data.encode()).hexdigest()[:12]


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Parser JSON avec fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Sérialiser JSON avec fallback"""
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Tronquer une chaîne si trop longue"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Nettoyer un nom de fichier"""
    # Remplacer caractères invalides
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limiter la longueur
    return truncate_string(sanitized, 255, "")


def chunks(lst: list, n: int):
    """Diviser une liste en chunks de taille n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Aplatir un dictionnaire imbriqué"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(*dicts: Dict) -> Dict:
    """Fusionner plusieurs dictionnaires"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_nested(d: Dict, *keys, default=None) -> Any:
    """Obtenir une valeur imbriquée dans un dict de manière sûre"""
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def generate_unique_id(prefix: str = "", identifier: str = "") -> str:
    """
    Génère un ID unique
    
    Args:
        prefix: Préfixe (ex: "dev", "scan", "event")
        identifier: Identifiant additionnel (ex: MAC)
        
    Returns:
        ID unique (ex: "dev_aabbccddeeff", "scan_1729350000")
    """
    import time
    
    if identifier:
        # Nettoyer l'identifier (enlever : - .)
        clean_id = identifier.replace(':', '').replace('-', '').replace('.', '').lower()
        if prefix:
            return f"dev_{prefix}_{clean_id}"
        return f"dev_{clean_id}"
    
    # Timestamp basé
    timestamp = int(time.time())
    if prefix:
        return f"{prefix}_{timestamp}"
    return f"id_{timestamp}"
