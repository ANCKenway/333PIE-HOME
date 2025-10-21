"""
🌐 333HOME - Network Latency Router
Endpoints pour mesure latence/qualité réseau
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query

from ..monitoring.latency_monitor import get_latency_monitor  # ✅ Déplacé dans monitoring/


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/latency", tags=["network-latency"])


@router.get("/{ip}")
async def get_device_latency(ip: str) -> dict:
    """
    Statistiques de latence pour un device
    
    Args:
        ip: Adresse IP
        
    Returns:
        LatencyStats
    """
    try:
        monitor = get_latency_monitor()
        stats = monitor.calculate_stats(ip)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Pas de données de latence pour {ip}"
            )
        
        return {
            "ip": stats.ip,
            "hostname": stats.hostname,
            "measurements_count": stats.measurements_count,
            "avg_latency_ms": stats.avg_latency_ms,
            "min_latency_ms": stats.min_latency_ms,
            "max_latency_ms": stats.max_latency_ms,
            "jitter_ms": stats.jitter_ms,
            "packet_loss_percent": stats.packet_loss_percent,
            "quality_score": stats.quality_score,
            "quality_label": stats.quality_label,
            "quality_icon": monitor.get_quality_icon(stats.quality_score),
            "last_measurement": stats.last_measurement.isoformat() if stats.last_measurement else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting latency: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération latence: {str(e)}"
        )


@router.post("/measure")
async def measure_latency(
    background_tasks: BackgroundTasks,
    ips: List[str] = Query(..., description="Liste d'IPs à mesurer"),
) -> dict:
    """
    Mesure la latence de plusieurs devices
    
    🔧 ON-DEMAND uniquement
    
    Args:
        ips: Liste d'adresses IP
        background_tasks: Tasks FastAPI
        
    Returns:
        Dict avec résultats
    """
    try:
        monitor = get_latency_monitor()
        
        logger.info(f"⚡ Measuring latency for {len(ips)} devices...")
        
        # Mesurer en background
        results = await monitor.monitor_hosts(ips, count_per_check=4)
        
        # Formater les résultats
        formatted_results = []
        for ip, stats in results.items():
            formatted_results.append({
                "ip": ip,
                "avg_latency_ms": stats.avg_latency_ms,
                "quality_score": stats.quality_score,
                "quality_label": stats.quality_label,
                "quality_icon": monitor.get_quality_icon(stats.quality_score),
                "packet_loss_percent": stats.packet_loss_percent,
            })
        
        return {
            "total_measured": len(results),
            "results": formatted_results,
        }
    
    except Exception as e:
        logger.error(f"❌ Error measuring latency: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur mesure latence: {str(e)}"
        )
