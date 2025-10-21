"""
🌐 333HOME - Network History
Gestion de l'historique réseau et des événements

Fonctionnalités:
- Track apparitions/disparitions
- Détection changements IP/hostname
- Génération timeline
- Statistiques avancées
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .schemas import (
    NetworkDevice,
    NetworkEvent,
    NetworkEventType,
    NetworkTimeline,
    NetworkStats,
    DeviceStatistics,
    IPHistoryEntry,
    DeviceHistory,
    OnlinePeriod,
)
from .storage import (
    load_network_storage,
    save_network_storage,
    get_all_devices,
    get_device_by_mac,
)
from src.shared.utils import generate_unique_id


logger = logging.getLogger(__name__)


class NetworkHistory:
    """Gestionnaire d'historique réseau"""
    
    def __init__(self):
        self.storage = load_network_storage()
    
    def reload(self):
        """Recharge le storage"""
        self.storage = load_network_storage()
    
    # === ÉVÉNEMENTS ===
    
    def _create_event(
        self,
        event_type: NetworkEventType,
        device_mac: str,
        device_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> NetworkEvent:
        """Crée un événement réseau"""
        return NetworkEvent(
            event_id=generate_unique_id("event"),
            timestamp=datetime.now(),
            event_type=event_type,
            device_mac=device_mac,
            device_name=device_name,
            details=details or {},
        )
    
    def _save_event(self, event: NetworkEvent):
        """Sauvegarde un événement"""
        if "events" not in self.storage:
            self.storage["events"] = []
        
        self.storage["events"].append({
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "device_mac": event.device_mac,
            "device_name": event.device_name,
            "details": event.details,
        })
        
        # Limiter à 500 événements
        if len(self.storage["events"]) > 500:
            self.storage["events"] = self.storage["events"][-500:]
        
        save_network_storage(self.storage)
    
    def detect_and_log_changes(
        self,
        previous_device: Optional[NetworkDevice],
        current_device: NetworkDevice,
    ) -> List[NetworkEvent]:
        """
        Détecte et log les changements
        
        Args:
            previous_device: État précédent (None si nouveau)
            current_device: État actuel
            
        Returns:
            Liste des événements créés
        """
        events = []
        
        if not previous_device:
            # Nouveau device
            event = self._create_event(
                NetworkEventType.DEVICE_APPEARED,
                current_device.mac,
                current_device.current_hostname,
                {
                    "ip": current_device.current_ip,
                    "vendor": current_device.vendor,
                    "device_type": current_device.device_type,
                }
            )
            events.append(event)
            self._save_event(event)
            logger.info(f"✨ New device: {current_device.mac} ({current_device.current_ip})")
        
        else:
            # Changement IP
            if previous_device.current_ip != current_device.current_ip:
                event = self._create_event(
                    NetworkEventType.IP_CHANGED,
                    current_device.mac,
                    current_device.current_hostname,
                    {
                        "old_ip": previous_device.current_ip,
                        "new_ip": current_device.current_ip,
                    }
                )
                events.append(event)
                self._save_event(event)
                logger.info(f"🔄 IP changed: {current_device.mac} {previous_device.current_ip} → {current_device.current_ip}")
            
            # Changement hostname
            if (previous_device.current_hostname != current_device.current_hostname and
                current_device.current_hostname):
                event = self._create_event(
                    NetworkEventType.HOSTNAME_CHANGED,
                    current_device.mac,
                    current_device.current_hostname,
                    {
                        "old_hostname": previous_device.current_hostname,
                        "new_hostname": current_device.current_hostname,
                    }
                )
                events.append(event)
                self._save_event(event)
                logger.info(f"🔄 Hostname changed: {current_device.mac}")
            
            # Réapparition
            if not previous_device.currently_online and current_device.currently_online:
                event = self._create_event(
                    NetworkEventType.DEVICE_APPEARED,
                    current_device.mac,
                    current_device.current_hostname,
                    {
                        "ip": current_device.current_ip,
                        "offline_duration": "unknown",
                    }
                )
                events.append(event)
                self._save_event(event)
                logger.info(f"✨ Device reconnected: {current_device.mac}")
        
        return events
    
    def log_device_disappeared(self, device: NetworkDevice):
        """Log la disparition d'un device"""
        event = self._create_event(
            NetworkEventType.DEVICE_DISAPPEARED,
            device.mac,
            device.current_hostname,
            {
                "last_ip": device.current_ip,
            }
        )
        self._save_event(event)
        logger.info(f"👻 Device disappeared: {device.mac}")
    
    # === TIMELINE ===
    
    def get_timeline(
        self,
        hours: int = 24,
        device_mac: Optional[str] = None,
    ) -> NetworkTimeline:
        """
        Récupère la timeline des événements
        
        Args:
            hours: Nombre d'heures à récupérer
            device_mac: Filtrer par MAC (optionnel)
            
        Returns:
            NetworkTimeline
        """
        self.reload()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events_data = self.storage.get("events", [])
        
        # Filtrer et convertir
        events = []
        for event_data in events_data:
            timestamp = datetime.fromisoformat(event_data["timestamp"])
            
            if timestamp < cutoff_time:
                continue
            
            if device_mac and event_data["device_mac"] != device_mac:
                continue
            
            events.append(NetworkEvent(
                event_id=event_data["event_id"],
                timestamp=timestamp,
                event_type=NetworkEventType(event_data["event_type"]),
                device_mac=event_data["device_mac"],
                device_name=event_data.get("device_name"),
                details=event_data.get("details", {}),
            ))
        
        # Trier par date (plus récent en premier)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return NetworkTimeline(
            total_events=len(events),
            events=events,
            period_start=cutoff_time if events else None,
            period_end=datetime.now() if events else None,
        )
    
    # === STATISTIQUES ===
    
    def get_device_statistics(self, mac: str) -> Optional[DeviceStatistics]:
        """Statistiques d'un device"""
        self.reload()
        
        device_data = self.storage["devices"].get(mac)
        if not device_data:
            return None
        
        first_seen = datetime.fromisoformat(device_data["first_seen"])
        last_seen = datetime.fromisoformat(device_data["last_seen"])
        
        total_days = max((last_seen - first_seen).days, 1)
        total_appearances = device_data.get("total_appearances", 1)
        
        # Uptime (estimation simple)
        uptime_percentage = min((total_appearances / total_days) * 10, 100.0)
        
        # Durée moyenne connexion
        avg_duration = total_days / max(total_appearances, 1)
        
        return DeviceStatistics(
            mac=mac,
            name=device_data.get("current_hostname"),
            total_appearances=total_appearances,
            uptime_percentage=round(uptime_percentage, 2),
            average_connection_duration_hours=round(avg_duration * 24, 2),
            last_ip=device_data["current_ip"],
            last_seen=last_seen,
        )
    
    def get_network_stats(self) -> NetworkStats:
        """Statistiques réseau globales"""
        self.reload()
        
        devices = self.storage["devices"]
        
        currently_online = sum(1 for d in devices.values() if d.get("currently_online"))
        currently_offline = len(devices) - currently_online
        
        # Devices des dernières 24h
        cutoff_24h = datetime.now() - timedelta(hours=24)
        new_24h = 0
        ip_changes_24h = 0
        
        for device_data in devices.values():
            first_seen = datetime.fromisoformat(device_data["first_seen"])
            if first_seen > cutoff_24h:
                new_24h += 1
        
        # Compter changements IP dans events
        events = self.storage.get("events", [])
        for event in events:
            timestamp = datetime.fromisoformat(event["timestamp"])
            if timestamp > cutoff_24h and event["event_type"] == NetworkEventType.IP_CHANGED.value:
                ip_changes_24h += 1
        
        # Moyenne online (estimation)
        avg_online = currently_online if currently_online > 0 else 1
        
        # Device le plus stable
        most_stable = None
        max_uptime = 0
        
        # Device le plus actif
        most_active = None
        max_appearances = 0
        
        for mac, device_data in devices.items():
            stats = self.get_device_statistics(mac)
            if stats:
                if stats.uptime_percentage > max_uptime:
                    max_uptime = stats.uptime_percentage
                    most_stable = stats
                
                if stats.total_appearances > max_appearances:
                    max_appearances = stats.total_appearances
                    most_active = stats
        
        # Last scan
        last_scan = None
        scan_history = self.storage.get("scan_history", [])
        if scan_history:
            last_scan_data = scan_history[-1]
            last_scan = datetime.fromisoformat(last_scan_data["timestamp"])
        
        return NetworkStats(
            total_devices_seen=len(devices),
            currently_online=currently_online,
            currently_offline=currently_offline,
            average_devices_online=float(avg_online),
            new_devices_last_24h=new_24h,
            ip_changes_last_24h=ip_changes_24h,
            most_stable_device=most_stable,
            most_active_device=most_active,
            last_scan=last_scan,
        )
    
    # === HISTORIQUE DEVICE ===
    
    def get_device_history(self, mac: str) -> Optional[DeviceHistory]:
        """Historique complet d'un device"""
        self.reload()
        
        device_data = self.storage["devices"].get(mac)
        if not device_data:
            return None
        
        # IP History
        ip_history = []
        # TODO: Implémenter tracking IP history
        
        # Events
        events = []
        for event_data in self.storage.get("events", []):
            if event_data["device_mac"] == mac:
                events.append(NetworkEvent(
                    event_id=event_data["event_id"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    event_type=NetworkEventType(event_data["event_type"]),
                    device_mac=event_data["device_mac"],
                    device_name=event_data.get("device_name"),
                    details=event_data.get("details", {}),
                ))
        
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Online periods (estimation simple)
        online_periods = []
        # TODO: Implémenter tracking périodes
        
        # Statistics
        statistics = self.get_device_statistics(mac)
        
        return DeviceHistory(
            mac=mac,
            device_name=device_data.get("current_hostname"),
            first_seen=datetime.fromisoformat(device_data["first_seen"]),
            last_seen=datetime.fromisoformat(device_data["last_seen"]),
            total_appearances=device_data.get("total_appearances", 1),
            ip_history=ip_history,
            events=events,
            online_periods=online_periods,
            statistics=statistics,
        )
