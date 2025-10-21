"""
🌐 333HOME - Bandwidth Monitor

Monitoring professionnel de la bande passante réseau :
- Suivi upload/download par device
- Top talkers identification
- Statistiques d'usage
- Détection anomalies
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class BandwidthSample:
    """Échantillon de bande passante à un instant T"""
    
    timestamp: float
    bytes_sent: int
    bytes_received: int
    
    @property
    def total_bytes(self) -> int:
        """Total bytes transferrés"""
        return self.bytes_sent + self.bytes_received


@dataclass
class BandwidthStats:
    """Statistiques de bande passante pour un device"""
    
    ip: str
    mac: str
    hostname: Optional[str] = None
    
    # Données actuelles (dernière minute)
    current_upload_bps: float = 0.0  # bits per second
    current_download_bps: float = 0.0
    current_total_bps: float = 0.0
    
    # Totaux cumulés
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    total_bytes: int = 0
    
    # Moyennes
    avg_upload_bps: float = 0.0
    avg_download_bps: float = 0.0
    avg_total_bps: float = 0.0
    
    # Pics
    peak_upload_bps: float = 0.0
    peak_download_bps: float = 0.0
    peak_timestamp: Optional[float] = None
    
    # Métadonnées
    first_seen: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    sample_count: int = 0
    
    @property
    def total_mb(self) -> float:
        """Total en MB"""
        return self.total_bytes / (1024 * 1024)
    
    @property
    def current_mbps(self) -> float:
        """Débit actuel en Mbps"""
        return self.current_total_bps / (1024 * 1024)
    
    @property
    def avg_mbps(self) -> float:
        """Débit moyen en Mbps"""
        return self.avg_total_bps / (1024 * 1024)
    
    @property
    def peak_mbps(self) -> float:
        """Pic en Mbps"""
        return max(self.peak_upload_bps, self.peak_download_bps) / (1024 * 1024)
    
    @property
    def uptime_seconds(self) -> float:
        """Durée de monitoring en secondes"""
        return self.last_update - self.first_seen


class BandwidthMonitor:
    """
    Moniteur de bande passante réseau
    
    Note: Utilise /proc/net/dev pour Linux.
    Pour monitoring précis par IP, nécessite iptables ou nDPI.
    Cette implémentation basique estime le traffic.
    """
    
    def __init__(self, sampling_interval: float = 5.0):
        """
        Initialise le moniteur
        
        Args:
            sampling_interval: Intervalle entre échantillons (secondes)
        """
        self.sampling_interval = sampling_interval
        self._devices: Dict[str, BandwidthStats] = {}
        self._samples: Dict[str, List[BandwidthSample]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        logger.info(f"BandwidthMonitor initialized (interval={sampling_interval}s)")
    
    def start(self):
        """Démarre le monitoring en arrière-plan"""
        if self._running:
            logger.warning("BandwidthMonitor already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("BandwidthMonitor started")
    
    def stop(self):
        """Arrête le monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
        logger.info("BandwidthMonitor stopped")
    
    async def _monitoring_loop(self):
        """Boucle de monitoring continue"""
        try:
            while self._running:
                await self._collect_samples()
                await asyncio.sleep(self.sampling_interval)
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
    
    async def _collect_samples(self):
        """Collecte les échantillons pour tous les devices"""
        # Note: Implémentation basique
        # Pour production, utiliser iptables -nvx ou nDPI
        pass
    
    def register_device(
        self,
        ip: str,
        mac: str,
        hostname: Optional[str] = None
    ) -> BandwidthStats:
        """
        Enregistre un device pour monitoring
        
        Args:
            ip: Adresse IP du device
            mac: Adresse MAC du device
            hostname: Nom d'hôte optionnel
        
        Returns:
            BandwidthStats du device
        """
        if mac not in self._devices:
            self._devices[mac] = BandwidthStats(
                ip=ip,
                mac=mac,
                hostname=hostname
            )
            self._samples[mac] = []
            logger.info(f"Device registered for bandwidth monitoring: {ip} ({mac})")
        
        return self._devices[mac]
    
    def add_sample(
        self,
        mac: str,
        bytes_sent: int,
        bytes_received: int
    ) -> None:
        """
        Ajoute un échantillon de bande passante
        
        Args:
            mac: Adresse MAC du device
            bytes_sent: Bytes envoyés depuis dernier sample
            bytes_received: Bytes reçus depuis dernier sample
        """
        if mac not in self._devices:
            logger.warning(f"Device not registered: {mac}")
            return
        
        sample = BandwidthSample(
            timestamp=time.time(),
            bytes_sent=bytes_sent,
            bytes_received=bytes_received
        )
        
        self._samples[mac].append(sample)
        self._update_stats(mac, sample)
        
        # Garder seulement 1h d'historique
        max_age = time.time() - 3600
        self._samples[mac] = [
            s for s in self._samples[mac]
            if s.timestamp > max_age
        ]
    
    def _update_stats(self, mac: str, sample: BandwidthSample) -> None:
        """Met à jour les statistiques d'un device"""
        stats = self._devices[mac]
        samples = self._samples[mac]
        
        # Update totaux
        stats.total_bytes_sent += sample.bytes_sent
        stats.total_bytes_received += sample.bytes_received
        stats.total_bytes = stats.total_bytes_sent + stats.total_bytes_received
        
        # Calcul débit actuel (bps)
        if len(samples) >= 2:
            prev_sample = samples[-2]
            time_diff = sample.timestamp - prev_sample.timestamp
            
            if time_diff > 0:
                stats.current_upload_bps = (sample.bytes_sent * 8) / time_diff
                stats.current_download_bps = (sample.bytes_received * 8) / time_diff
                stats.current_total_bps = stats.current_upload_bps + stats.current_download_bps
        
        # Calcul moyennes
        total_time = stats.uptime_seconds
        if total_time > 0:
            stats.avg_upload_bps = (stats.total_bytes_sent * 8) / total_time
            stats.avg_download_bps = (stats.total_bytes_received * 8) / total_time
            stats.avg_total_bps = stats.avg_upload_bps + stats.avg_download_bps
        
        # Update pics
        if stats.current_upload_bps > stats.peak_upload_bps:
            stats.peak_upload_bps = stats.current_upload_bps
            stats.peak_timestamp = sample.timestamp
        
        if stats.current_download_bps > stats.peak_download_bps:
            stats.peak_download_bps = stats.current_download_bps
            stats.peak_timestamp = sample.timestamp
        
        stats.last_update = sample.timestamp
        stats.sample_count = len(samples)
    
    def get_stats(self, mac: str) -> Optional[BandwidthStats]:
        """Récupère les stats d'un device"""
        return self._devices.get(mac)
    
    def get_all_stats(self) -> List[BandwidthStats]:
        """Récupère les stats de tous les devices"""
        return list(self._devices.values())
    
    def get_top_talkers(
        self,
        limit: int = 10,
        sort_by: str = "total"
    ) -> List[BandwidthStats]:
        """
        Récupère les top talkers (devices avec plus de traffic)
        
        Args:
            limit: Nombre max de devices
            sort_by: Critère de tri (total, upload, download, current)
        
        Returns:
            Liste des top devices
        """
        devices = list(self._devices.values())
        
        if sort_by == "upload":
            devices.sort(key=lambda d: d.total_bytes_sent, reverse=True)
        elif sort_by == "download":
            devices.sort(key=lambda d: d.total_bytes_received, reverse=True)
        elif sort_by == "current":
            devices.sort(key=lambda d: d.current_total_bps, reverse=True)
        else:  # total
            devices.sort(key=lambda d: d.total_bytes, reverse=True)
        
        return devices[:limit]
    
    def get_total_bandwidth(self) -> Dict[str, float]:
        """
        Calcule la bande passante totale du réseau
        
        Returns:
            Dict avec upload_mbps, download_mbps, total_mbps
        """
        total_upload = sum(d.current_upload_bps for d in self._devices.values())
        total_download = sum(d.current_download_bps for d in self._devices.values())
        
        return {
            "upload_bps": total_upload,
            "download_bps": total_download,
            "total_bps": total_upload + total_download,
            "upload_mbps": total_upload / (1024 * 1024),
            "download_mbps": total_download / (1024 * 1024),
            "total_mbps": (total_upload + total_download) / (1024 * 1024)
        }
    
    def reset_stats(self, mac: Optional[str] = None) -> None:
        """
        Réinitialise les statistiques
        
        Args:
            mac: MAC du device (None = tous)
        """
        if mac:
            if mac in self._devices:
                del self._devices[mac]
                del self._samples[mac]
                logger.info(f"Stats reset for device: {mac}")
        else:
            self._devices.clear()
            self._samples.clear()
            logger.info("All stats reset")


# Singleton global
_bandwidth_monitor: Optional[BandwidthMonitor] = None


def get_bandwidth_monitor() -> BandwidthMonitor:
    """Récupère l'instance singleton du BandwidthMonitor"""
    global _bandwidth_monitor
    if _bandwidth_monitor is None:
        _bandwidth_monitor = BandwidthMonitor()
    return _bandwidth_monitor
