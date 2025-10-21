"""
🏠 333HOME - DHCP Tracker

Suivi de l'historique des adresses IP attribuées aux appareils
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class DHCPTracker:
    """
    Suivi des changements d'IP DHCP pour chaque appareil
    """
    
    def __init__(self):
        self.history_file = settings.data_dir / "dhcp_history.json"
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Créer le fichier de stockage s'il n'existe pas"""
        if not self.history_file.exists():
            self._save_history({
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "devices": {}
            })
            logger.info(f"📝 DHCP history file created: {self.history_file}")
    
    def _load_history(self) -> Dict[str, Any]:
        """Charger l'historique depuis le fichier"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load DHCP history: {e}")
            return {
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "devices": {}
            }
    
    def _save_history(self, data: Dict[str, Any]):
        """Sauvegarder l'historique"""
        try:
            data["updated_at"] = datetime.now().isoformat()
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save DHCP history: {e}")
    
    def track_ip_change(self, mac: str, ip: str, hostname: Optional[str] = None):
        """
        Enregistrer un changement d'IP pour un appareil
        
        Args:
            mac: Adresse MAC de l'appareil
            ip: Nouvelle adresse IP
            hostname: Nom d'hôte (optionnel)
        """
        mac = mac.upper()
        history = self._load_history()
        
        # Créer l'entrée du device si inexistante
        if mac not in history["devices"]:
            history["devices"][mac] = {
                "mac": mac,
                "hostname": hostname,
                "current_ip": ip,
                "ip_history": [],
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "total_ip_changes": 0
            }
        
        device = history["devices"][mac]
        
        # Vérifier si l'IP a changé
        if device["current_ip"] != ip:
            # Ajouter l'ancienne IP à l'historique
            if device["current_ip"]:
                device["ip_history"].append({
                    "ip": device["current_ip"],
                    "assigned_at": device.get("ip_assigned_at", device["last_seen"]),
                    "released_at": datetime.now().isoformat()
                })
            
            # Mettre à jour avec la nouvelle IP
            device["current_ip"] = ip
            device["ip_assigned_at"] = datetime.now().isoformat()
            device["total_ip_changes"] += 1
            
            logger.info(f"📍 IP changed for {mac}: {device['ip_history'][-1]['ip'] if device['ip_history'] else 'N/A'} → {ip}")
        
        # Mettre à jour les métadonnées
        device["last_seen"] = datetime.now().isoformat()
        if hostname:
            device["hostname"] = hostname
        
        # Limiter l'historique à 50 entrées par device
        if len(device["ip_history"]) > 50:
            device["ip_history"] = device["ip_history"][-50:]
        
        self._save_history(history)
    
    def get_device_ip_history(self, mac: str) -> List[Dict[str, Any]]:
        """
        Récupérer l'historique des IPs d'un appareil
        
        Args:
            mac: Adresse MAC
            
        Returns:
            Liste des IPs avec dates
        """
        mac = mac.upper()
        history = self._load_history()
        
        device = history["devices"].get(mac)
        if not device:
            return []
        
        # Retourner historique + IP actuelle
        ip_list = device.get("ip_history", []).copy()
        ip_list.append({
            "ip": device["current_ip"],
            "assigned_at": device.get("ip_assigned_at", device["last_seen"]),
            "released_at": None,  # IP actuelle
            "is_current": True
        })
        
        return ip_list
    
    def get_all_devices_summary(self) -> List[Dict[str, Any]]:
        """
        Récupérer un résumé de tous les devices suivis
        
        Returns:
            Liste des devices avec leur statut DHCP
        """
        history = self._load_history()
        
        summary = []
        for mac, device in history["devices"].items():
            summary.append({
                "mac": mac,
                "hostname": device.get("hostname"),
                "current_ip": device["current_ip"],
                "ip_assigned_at": device.get("ip_assigned_at"),
                "last_seen": device["last_seen"],
                "first_seen": device["first_seen"],
                "total_ip_changes": device["total_ip_changes"],
                "ip_history_count": len(device.get("ip_history", []))
            })
        
        return summary
    
    def get_ip_conflicts(self) -> List[Dict[str, Any]]:
        """
        Détecter les conflits d'IP (même IP attribuée à plusieurs MACs)
        
        Returns:
            Liste des conflits détectés
        """
        history = self._load_history()
        
        # Grouper par IP actuelle
        ip_map = {}
        for mac, device in history["devices"].items():
            current_ip = device["current_ip"]
            if current_ip not in ip_map:
                ip_map[current_ip] = []
            ip_map[current_ip].append({
                "mac": mac,
                "hostname": device.get("hostname"),
                "last_seen": device["last_seen"]
            })
        
        # Identifier les conflits
        conflicts = []
        for ip, devices in ip_map.items():
            if len(devices) > 1:
                conflicts.append({
                    "ip": ip,
                    "devices": devices,
                    "conflict_count": len(devices)
                })
        
        return conflicts
    
    def get_dhcp_pool_usage(self, subnet: str = "192.168.1") -> Dict[str, Any]:
        """
        Analyser l'utilisation du pool DHCP
        
        Args:
            subnet: Sous-réseau à analyser (ex: "192.168.1")
            
        Returns:
            Statistiques d'utilisation
        """
        history = self._load_history()
        
        # IPs utilisées dans le subnet
        used_ips = set()
        for device in history["devices"].values():
            ip = device["current_ip"]
            if ip and ip.startswith(subnet):
                used_ips.add(ip)
        
        # Calculer les stats (suppose range .1-.254)
        total_ips = 254
        used_count = len(used_ips)
        
        return {
            "subnet": subnet + ".0/24",
            "total_ips": total_ips,
            "used_ips": used_count,
            "free_ips": total_ips - used_count,
            "usage_percent": round((used_count / total_ips) * 100, 2),
            "used_ip_list": sorted(used_ips, key=lambda x: int(x.split('.')[-1]))
        }
    
    def cleanup_old_entries(self, days: int = 30):
        """
        Nettoyer les entrées anciennes
        
        Args:
            days: Supprimer les devices non vus depuis N jours
        """
        history = self._load_history()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        removed = 0
        devices_to_remove = []
        
        for mac, device in history["devices"].items():
            last_seen = datetime.fromisoformat(device["last_seen"])
            if last_seen < cutoff_date:
                devices_to_remove.append(mac)
                removed += 1
        
        for mac in devices_to_remove:
            del history["devices"][mac]
        
        if removed > 0:
            self._save_history(history)
            logger.info(f"🧹 Cleaned up {removed} old DHCP entries (>{days} days)")
        
        return removed


# Singleton
_tracker = None

def get_dhcp_tracker() -> DHCPTracker:
    """Récupérer l'instance du tracker DHCP"""
    global _tracker
    if _tracker is None:
        _tracker = DHCPTracker()
    return _tracker
