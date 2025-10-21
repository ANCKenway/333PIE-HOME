"""
⚡ 333HOME - Latency Monitor
Monitoring de latence et qualité réseau

Fonctionnalités:
- Mesure latence/ping en continu
- Calcul jitter (variation latence)
- Détection packet loss
- Score qualité réseau
- Historique latence par device
"""

import asyncio
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LatencyMeasurement:
    """Mesure de latence"""
    timestamp: datetime
    latency_ms: float
    success: bool


@dataclass
class LatencyStats:
    """Statistiques de latence"""
    ip: str
    hostname: Optional[str] = None
    measurements_count: int = 0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_percent: float = 0.0
    quality_score: int = 100  # 0-100
    quality_label: str = "Excellent"
    last_measurement: Optional[datetime] = None


class LatencyMonitor:
    """Moniteur de latence réseau"""
    
    def __init__(self, history_size: int = 100):
        """
        Initialise le moniteur
        
        Args:
            history_size: Nombre de mesures à conserver en historique
        """
        self.history_size = history_size
        # Dict {ip: deque[LatencyMeasurement]}
        self.history: Dict[str, deque] = {}
    
    async def measure_latency(
        self,
        ip: str,
        count: int = 4,
        timeout: float = 2.0,
    ) -> List[LatencyMeasurement]:
        """
        Mesure la latence vers un host
        
        Args:
            ip: Adresse IP
            count: Nombre de pings
            timeout: Timeout en secondes
            
        Returns:
            Liste de mesures
        """
        measurements = []
        
        for _ in range(count):
            try:
                start = time.time()
                
                # Ping via subprocess
                process = await asyncio.create_subprocess_exec(
                    'ping',
                    '-c', '1',
                    '-W', str(int(timeout)),
                    ip,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                
                await process.wait()
                end = time.time()
                
                if process.returncode == 0:
                    latency_ms = (end - start) * 1000
                    measurements.append(LatencyMeasurement(
                        timestamp=datetime.now(),
                        latency_ms=latency_ms,
                        success=True,
                    ))
                else:
                    measurements.append(LatencyMeasurement(
                        timestamp=datetime.now(),
                        latency_ms=0.0,
                        success=False,
                    ))
            
            except Exception as e:
                logger.debug(f"Ping failed for {ip}: {e}")
                measurements.append(LatencyMeasurement(
                    timestamp=datetime.now(),
                    latency_ms=0.0,
                    success=False,
                ))
        
        # Sauvegarder dans l'historique
        if ip not in self.history:
            self.history[ip] = deque(maxlen=self.history_size)
        
        self.history[ip].extend(measurements)
        
        return measurements
    
    def calculate_stats(
        self,
        ip: str,
        hostname: Optional[str] = None,
    ) -> Optional[LatencyStats]:
        """
        Calcule les statistiques de latence
        
        Args:
            ip: Adresse IP
            hostname: Hostname (optionnel)
            
        Returns:
            LatencyStats ou None si pas de données
        """
        if ip not in self.history or not self.history[ip]:
            return None
        
        measurements = list(self.history[ip])
        successful = [m for m in measurements if m.success]
        
        if not successful:
            return LatencyStats(
                ip=ip,
                hostname=hostname,
                measurements_count=len(measurements),
                packet_loss_percent=100.0,
                quality_score=0,
                quality_label="Offline",
            )
        
        # Latences
        latencies = [m.latency_ms for m in successful]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Jitter (variation moyenne)
        if len(latencies) > 1:
            jitter = sum(
                abs(latencies[i] - latencies[i-1])
                for i in range(1, len(latencies))
            ) / (len(latencies) - 1)
        else:
            jitter = 0.0
        
        # Packet loss
        packet_loss = ((len(measurements) - len(successful)) / len(measurements)) * 100
        
        # Score qualité (0-100)
        # Facteurs:
        # - Latence moyenne (50%)
        # - Jitter (30%)
        # - Packet loss (20%)
        
        latency_score = max(0, 100 - (avg_latency / 2))  # 0ms=100, 200ms=0
        jitter_score = max(0, 100 - (jitter * 2))  # 0ms=100, 50ms=0
        loss_score = max(0, 100 - (packet_loss * 2))  # 0%=100, 50%=0
        
        quality_score = int(
            latency_score * 0.5 +
            jitter_score * 0.3 +
            loss_score * 0.2
        )
        
        # Label qualité
        if quality_score >= 90:
            quality_label = "Excellent"
        elif quality_score >= 75:
            quality_label = "Good"
        elif quality_score >= 50:
            quality_label = "Fair"
        elif quality_score >= 25:
            quality_label = "Poor"
        else:
            quality_label = "Bad"
        
        return LatencyStats(
            ip=ip,
            hostname=hostname,
            measurements_count=len(measurements),
            avg_latency_ms=round(avg_latency, 2),
            min_latency_ms=round(min_latency, 2),
            max_latency_ms=round(max_latency, 2),
            jitter_ms=round(jitter, 2),
            packet_loss_percent=round(packet_loss, 2),
            quality_score=quality_score,
            quality_label=quality_label,
            last_measurement=measurements[-1].timestamp,
        )
    
    async def monitor_hosts(
        self,
        ips: List[str],
        interval: int = 60,
        count_per_check: int = 4,
    ) -> Dict[str, LatencyStats]:
        """
        Monitore plusieurs hosts en continu
        
        Args:
            ips: Liste d'IPs à monitorer
            interval: Intervalle en secondes
            count_per_check: Pings par check
            
        Returns:
            Dict {ip: LatencyStats}
        """
        logger.info(f"⚡ Starting latency monitoring for {len(ips)} hosts")
        
        # Mesurer tous les hosts
        tasks = [
            self.measure_latency(ip, count=count_per_check)
            for ip in ips
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculer les stats
        stats = {}
        for ip in ips:
            stat = self.calculate_stats(ip)
            if stat:
                stats[ip] = stat
        
        return stats
    
    def get_quality_icon(self, quality_score: int) -> str:
        """Retourne l'icône selon le score qualité"""
        if quality_score >= 90:
            return "🟢"  # Excellent
        elif quality_score >= 75:
            return "🟡"  # Good
        elif quality_score >= 50:
            return "🟠"  # Fair
        elif quality_score >= 25:
            return "🔴"  # Poor
        else:
            return "⚫"  # Bad/Offline
    
    def get_top_performers(
        self,
        limit: int = 5,
    ) -> List[LatencyStats]:
        """Retourne les meilleurs performers (latence la plus basse)"""
        all_stats = []
        
        for ip in self.history.keys():
            stat = self.calculate_stats(ip)
            if stat and stat.quality_score > 0:
                all_stats.append(stat)
        
        all_stats.sort(key=lambda s: s.avg_latency_ms)
        return all_stats[:limit]
    
    def get_worst_performers(
        self,
        limit: int = 5,
    ) -> List[LatencyStats]:
        """Retourne les pires performers"""
        all_stats = []
        
        for ip in self.history.keys():
            stat = self.calculate_stats(ip)
            if stat:
                all_stats.append(stat)
        
        all_stats.sort(key=lambda s: (s.packet_loss_percent, -s.avg_latency_ms), reverse=True)
        return all_stats[:limit]
    
    def clear_history(self, ip: Optional[str] = None):
        """Vide l'historique"""
        if ip:
            if ip in self.history:
                self.history[ip].clear()
        else:
            self.history.clear()


# === SINGLETON ===
_latency_monitor: Optional[LatencyMonitor] = None


def get_latency_monitor() -> LatencyMonitor:
    """Récupère le moniteur de latence singleton"""
    global _latency_monitor
    if _latency_monitor is None:
        _latency_monitor = LatencyMonitor()
    return _latency_monitor
