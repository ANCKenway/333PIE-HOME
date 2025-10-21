"""
🏠 333HOME - Network Monitoring Service

Service de monitoring réseau en background avec asyncio.
Scan périodique automatique + détection changements temps réel.

Features:
- Scan automatique configurable (default: 5min)
- Détection changements (IP, hostname, status, nouveau device)
- Integration avec AlertManager (à venir)
- Métriques temps réel

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 3
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.features.network.service_unified import get_network_service
from src.core.models.unified_device import UnifiedDevice


logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration du monitoring"""
    scan_interval_seconds: int = 300  # 5 minutes par défaut
    enabled: bool = True
    detect_changes: bool = True
    log_changes: bool = True


@dataclass
class MonitoringStats:
    """Statistiques du monitoring"""
    total_scans: int = 0
    last_scan: Optional[datetime] = None
    total_changes_detected: int = 0
    new_devices_detected: int = 0
    devices_offline_detected: int = 0
    ip_changes_detected: int = 0
    hostname_changes_detected: int = 0
    uptime_seconds: int = 0
    started_at: Optional[datetime] = None


class NetworkMonitoringService:
    """
    Service de monitoring réseau en background
    
    Gère:
    - Scan périodique automatique
    - Détection changements
    - Métriques
    - État du service
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.stats = MonitoringStats()
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.service = get_network_service()
        
        # Cache pour détection changements
        self.previous_devices: Dict[str, UnifiedDevice] = {}
    
    async def start(self):
        """Démarre le monitoring en background"""
        if self.is_running:
            logger.warning("Monitoring already running")
            return
        
        self.is_running = True
        self.stats.started_at = datetime.now()
        logger.info("🚀 Network monitoring started")
        logger.info(f"   Scan interval: {self.config.scan_interval_seconds}s")
        
        self.task = asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Arrête le monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Network monitoring stopped")
    
    async def _monitoring_loop(self):
        """Boucle principale du monitoring"""
        while self.is_running:
            try:
                await self._do_scan()
                await asyncio.sleep(self.config.scan_interval_seconds)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                # Continue malgré l'erreur
                await asyncio.sleep(self.config.scan_interval_seconds)
    
    async def _do_scan(self):
        """Exécute un scan et détecte les changements"""
        logger.info("📡 Monitoring: Starting scan...")
        start_time = datetime.now()
        
        try:
            # Scanner le réseau
            devices = await self.service.scan_network()
            
            # Détecter changements
            if self.config.detect_changes:
                changes = self._detect_changes(devices)
                if changes:
                    self._handle_changes(changes)
            
            # Update stats
            self.stats.total_scans += 1
            self.stats.last_scan = datetime.now()
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Monitoring: Scan complete ({len(devices)} devices in {duration:.2f}s)")
        
        except Exception as e:
            logger.error(f"Scan error: {e}")
    
    def _detect_changes(self, current_devices: List[UnifiedDevice]) -> List[Dict[str, Any]]:
        """Détecte les changements depuis le dernier scan"""
        changes = []
        current_macs = {d.mac for d in current_devices}
        previous_macs = set(self.previous_devices.keys())
        
        # Nouveaux devices
        new_macs = current_macs - previous_macs
        for mac in new_macs:
            device = next(d for d in current_devices if d.mac == mac)
            changes.append({
                'type': 'NEW_DEVICE',
                'mac': mac,
                'ip': device.current_ip,
                'hostname': device.hostname,
                'timestamp': datetime.now()
            })
            self.stats.new_devices_detected += 1
        
        # Devices disparus
        missing_macs = previous_macs - current_macs
        for mac in missing_macs:
            device = self.previous_devices[mac]
            changes.append({
                'type': 'DEVICE_OFFLINE',
                'mac': mac,
                'ip': device.current_ip,
                'hostname': device.hostname,
                'timestamp': datetime.now()
            })
            self.stats.devices_offline_detected += 1
        
        # Changements sur devices existants
        common_macs = current_macs & previous_macs
        for mac in common_macs:
            current = next(d for d in current_devices if d.mac == mac)
            previous = self.previous_devices[mac]
            
            # Changement IP
            if current.current_ip != previous.current_ip:
                changes.append({
                    'type': 'IP_CHANGED',
                    'mac': mac,
                    'old_ip': previous.current_ip,
                    'new_ip': current.current_ip,
                    'timestamp': datetime.now()
                })
                self.stats.ip_changes_detected += 1
            
            # Changement hostname
            if current.hostname != previous.hostname:
                changes.append({
                    'type': 'HOSTNAME_CHANGED',
                    'mac': mac,
                    'old_hostname': previous.hostname,
                    'new_hostname': current.hostname,
                    'timestamp': datetime.now()
                })
                self.stats.hostname_changes_detected += 1
            
            # Changement status
            if current.is_online != previous.is_online:
                change_type = 'DEVICE_ONLINE' if current.is_online else 'DEVICE_OFFLINE'
                changes.append({
                    'type': change_type,
                    'mac': mac,
                    'ip': current.current_ip,
                    'timestamp': datetime.now()
                })
                if not current.is_online:
                    self.stats.devices_offline_detected += 1
        
        # Mettre à jour le cache
        self.previous_devices = {d.mac: d for d in current_devices}
        
        return changes
    
    def _handle_changes(self, changes: List[Dict[str, Any]]):
        """Traite les changements détectés"""
        if not changes:
            return
        
        self.stats.total_changes_detected += len(changes)
        
        if self.config.log_changes:
            logger.info(f"📊 {len(changes)} changes detected:")
            for change in changes:
                change_type = change['type']
                mac = change['mac'][:17]
                
                if change_type == 'NEW_DEVICE':
                    logger.info(f"   🆕 NEW: {mac} - {change.get('ip')} ({change.get('hostname', 'Unknown')})")
                
                elif change_type == 'DEVICE_OFFLINE':
                    logger.info(f"   📴 OFFLINE: {mac} - {change.get('ip')}")
                
                elif change_type == 'DEVICE_ONLINE':
                    logger.info(f"   ✅ ONLINE: {mac} - {change.get('ip')}")
                
                elif change_type == 'IP_CHANGED':
                    logger.info(f"   🔄 IP CHANGE: {mac} - {change['old_ip']} → {change['new_ip']}")
                
                elif change_type == 'HOSTNAME_CHANGED':
                    logger.info(f"   🏷️  HOSTNAME CHANGE: {mac} - {change['old_hostname']} → {change['new_hostname']}")
        
        # TODO: Intégration AlertManager
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du monitoring"""
        uptime = 0
        if self.stats.started_at:
            uptime = int((datetime.now() - self.stats.started_at).total_seconds())
        
        return {
            'is_running': self.is_running,
            'config': {
                'scan_interval_seconds': self.config.scan_interval_seconds,
                'enabled': self.config.enabled,
                'detect_changes': self.config.detect_changes
            },
            'stats': {
                'total_scans': self.stats.total_scans,
                'last_scan': self.stats.last_scan.isoformat() if self.stats.last_scan else None,
                'total_changes_detected': self.stats.total_changes_detected,
                'new_devices_detected': self.stats.new_devices_detected,
                'devices_offline_detected': self.stats.devices_offline_detected,
                'ip_changes_detected': self.stats.ip_changes_detected,
                'hostname_changes_detected': self.stats.hostname_changes_detected,
                'uptime_seconds': uptime,
                'started_at': self.stats.started_at.isoformat() if self.stats.started_at else None
            }
        }


# === SINGLETON ===

_monitoring_instance: Optional[NetworkMonitoringService] = None


def get_monitoring_service() -> NetworkMonitoringService:
    """Retourne l'instance singleton du service de monitoring"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = NetworkMonitoringService()
    return _monitoring_instance


# === CLI Test ===

async def main():
    """Test CLI"""
    import signal
    
    print("\n🏠 333HOME - Network Monitoring Test\n")
    print("Starting monitoring... (Ctrl+C to stop)\n")
    
    # Config: scan toutes les 30s pour le test
    config = MonitoringConfig(scan_interval_seconds=30)
    monitoring = NetworkMonitoringService(config)
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n\nStopping monitoring...")
        asyncio.create_task(monitoring.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start monitoring
    await monitoring.start()
    
    # Wait
    while monitoring.is_running:
        await asyncio.sleep(1)
    
    print("\n📊 Final stats:")
    stats = monitoring.get_stats()
    print(f"   Total scans: {stats['stats']['total_scans']}")
    print(f"   Changes detected: {stats['stats']['total_changes_detected']}")
    print(f"   Uptime: {stats['stats']['uptime_seconds']}s")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    asyncio.run(main())
