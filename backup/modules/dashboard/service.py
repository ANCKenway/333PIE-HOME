"""
🔥 Service Dashboard Ultra - Agrégation avec Scanner Blindé
"""
from typing import Dict, Any, List
import asyncio
import psutil
import time
import platform
from datetime import datetime, timedelta
from pathlib import Path

from shared.utils import setup_logging
from core.config import get_settings
from modules.network.advanced_scanner import ultra_scanner

class UltraDashboardService:
    """Service d'agrégation ultra pour le dashboard avec scanner blindé"""
    
    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)
        self.settings = get_settings()
        self._cache = {}
        self._cache_ttl = 30  # Cache 30 secondes
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """🔥 Récupère toutes les données ultra pour le dashboard"""
        try:
            self.logger.info("🏠 Récupération données dashboard ultra")
            
            # Cache pour éviter les appels répétés
            cache_key = "dashboard_data"
            if cache_key in self._cache:
                cached_time, cached_data = self._cache[cache_key]
                if time.time() - cached_time < self._cache_ttl:
                    return cached_data
            
            # Récupération des données en parallèle
            tasks = [
                self._get_system_status_ultra(),
                self._get_network_overview(),
                self._get_device_summary(),
                self._get_performance_metrics(),
                self._get_security_status()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Traitement des résultats avec fallback
            system_status = results[0] if not isinstance(results[0], Exception) else self._get_fallback_system()
            network_overview = results[1] if not isinstance(results[1], Exception) else self._get_fallback_network()
            device_summary = results[2] if not isinstance(results[2], Exception) else self._get_fallback_devices()
            performance = results[3] if not isinstance(results[3], Exception) else self._get_fallback_performance()
            security = results[4] if not isinstance(results[4], Exception) else self._get_fallback_security()
            
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "system": system_status,
                "network": network_overview,
                "devices": device_summary,
                "performance": performance,
                "security": security,
                "version": "3.0.0",
                "scanner_version": "ultra_blindé"
            }
            
            # Cache des données
            self._cache[cache_key] = (time.time(), dashboard_data)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération dashboard: {e}", exc_info=True)
            return self._get_emergency_fallback()
    
    async def _get_system_status_ultra(self) -> Dict[str, Any]:
        """Statut système ultra détaillé"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Mémoire
            memory = psutil.virtual_memory()
            
            # Disque
            disk = psutil.disk_usage('/')
            
            return {
                "hostname": platform.node(),
                "platform": f"{platform.system()} {platform.release()}",
                "architecture": platform.architecture()[0],
                "uptime": {
                    "total_seconds": int(uptime.total_seconds()),
                    "days": uptime.days,
                    "hours": uptime.seconds // 3600,
                    "formatted": str(uptime).split('.')[0]
                },
                "cpu": {
                    "usage_percent": round(cpu_percent, 1),
                    "cores": cpu_count,
                    "frequency": round(cpu_freq.current, 0) if cpu_freq else 0,
                    "status": "🟢" if cpu_percent < 80 else "🟡" if cpu_percent < 95 else "🔴"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 1),
                    "used_gb": round(memory.used / (1024**3), 1),
                    "usage_percent": round(memory.percent, 1),
                    "available_gb": round(memory.available / (1024**3), 1),
                    "status": "🟢" if memory.percent < 80 else "🟡" if memory.percent < 95 else "🔴"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 1),
                    "used_gb": round(disk.used / (1024**3), 1),
                    "free_gb": round(disk.free / (1024**3), 1),
                    "usage_percent": round((disk.used / disk.total) * 100, 1),
                    "status": "🟢" if (disk.used / disk.total) < 0.8 else "🟡" if (disk.used / disk.total) < 0.95 else "🔴"
                },
                "temperature": self._get_temperature(),
                "status": "online"
            }
        except Exception as e:
            self.logger.error(f"Erreur statut système: {e}")
            return self._get_fallback_system()
    
    async def _get_network_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble réseau ultra avec scanner blindé"""
        try:
            # Utilisation du scanner ultra blindé (version allégée pour le dashboard)
            network_result = await ultra_scanner.scan_live_ultra()
            
            if network_result["success"]:
                stats = network_result["stats"]
                devices = network_result["devices"]
                
                # Top vendeurs
                top_vendors = sorted(
                    stats.get("vendors", {}).items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                
                # Top types d'appareils
                device_types = stats.get("device_types", {})
                
                # Derniers appareils vus
                recent_devices = sorted(
                    devices, 
                    key=lambda x: x.get("last_seen", 0), 
                    reverse=True
                )[:5]
                
                return {
                    "scan_status": "success",
                    "total_devices": stats.get("total_devices", 0),
                    "online_devices": stats.get("online_devices", 0),
                    "identification_rate": round(stats.get("avg_confidence", 0), 1),
                    "device_types": device_types,
                    "top_vendors": dict(top_vendors),
                    "recent_devices": [
                        {
                            "ip": device["ip"],
                            "hostname": device.get("hostname", "")[:20],
                            "vendor": device.get("vendor", "Unknown")[:15],
                            "device_type": device.get("device_type", "unknown"),
                            "confidence": round(device.get("confidence_score", 0), 0)
                        }
                        for device in recent_devices
                    ],
                    "scanner_techniques": stats.get("techniques_used", []),
                    "last_scan": datetime.fromtimestamp(network_result.get("scan_time", 0)).strftime("%H:%M:%S")
                }
            else:
                return self._get_fallback_network()
                
        except Exception as e:
            self.logger.error(f"Erreur vue réseau: {e}")
            return self._get_fallback_network()
    
    async def _get_device_summary(self) -> Dict[str, Any]:
        """Résumé des appareils avec classification intelligente"""
        try:
            # Réutilise les données réseau pour éviter double scan
            cache_key = "dashboard_data"
            if cache_key in self._cache:
                cached_time, cached_data = self._cache[cache_key]
                if time.time() - cached_time < self._cache_ttl:
                    network_data = cached_data.get("network", {})
                    device_types = network_data.get("device_types", {})
                    
                    # Classification par catégories
                    mobile_devices = (
                        device_types.get("smartphone", 0) + 
                        device_types.get("tablet", 0)
                    )
                    computers = (
                        device_types.get("laptop", 0) + 
                        device_types.get("desktop", 0) + 
                        device_types.get("server", 0)
                    )
                    network_equipment = (
                        device_types.get("router", 0) + 
                        device_types.get("access_point", 0)
                    )
                    iot_devices = (
                        device_types.get("smart_tv", 0) + 
                        device_types.get("camera", 0) + 
                        device_types.get("iot_device", 0) + 
                        device_types.get("printer", 0)
                    )
                    
                    return {
                        "categories": {
                            "mobile": mobile_devices,
                            "computers": computers,
                            "network": network_equipment,
                            "iot": iot_devices,
                            "other": device_types.get("unknown", 0)
                        },
                        "detailed_types": device_types,
                        "total": sum(device_types.values()),
                        "most_common": max(device_types.items(), key=lambda x: x[1])[0] if device_types else "unknown"
                    }
            
            return self._get_fallback_devices()
            
        except Exception as e:
            self.logger.error(f"Erreur résumé appareils: {e}")
            return self._get_fallback_devices()
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Métriques de performance système"""
        try:
            # Statistiques réseau
            net_io = psutil.net_io_counters()
            
            return {
                "network_io": {
                    "bytes_sent": round(net_io.bytes_sent / (1024**2), 1),  # MB
                    "bytes_recv": round(net_io.bytes_recv / (1024**2), 1),  # MB
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                },
                "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "processes": len(psutil.pids())
            }
            
        except Exception as e:
            self.logger.error(f"Erreur métriques performance: {e}")
            return self._get_fallback_performance()
    
    async def _get_security_status(self) -> Dict[str, Any]:
        """Statut sécurité et monitoring"""
        try:
            return {
                "scanner_status": "🔥 Ultra Blindé Actif",
                "last_full_scan": "En cours...",
                "firewall_status": "unknown",
                "open_ports_detected": 0,
                "security_level": "🟢 Monitoring Actif",
                "alerts": []
            }
            
        except Exception as e:
            self.logger.error(f"Erreur statut sécurité: {e}")
            return self._get_fallback_security()
    
    def _get_temperature(self) -> Dict[str, Any]:
        """Température système (Raspberry Pi)"""
        try:
            # Pour Raspberry Pi
            temp_path = Path("/sys/class/thermal/thermal_zone0/temp")
            if temp_path.exists():
                with open(temp_path, 'r') as f:
                    temp_raw = int(f.read().strip())
                    temp_c = temp_raw / 1000
                    return {
                        "celsius": round(temp_c, 1),
                        "fahrenheit": round((temp_c * 9/5) + 32, 1),
                        "status": "🟢" if temp_c < 60 else "🟡" if temp_c < 80 else "🔴"
                    }
            return {"celsius": 0, "fahrenheit": 0, "status": "❓"}
        except:
            return {"celsius": 0, "fahrenheit": 0, "status": "❓"}
    
    # MÉTHODES FALLBACK
    
    def _get_fallback_system(self) -> Dict[str, Any]:
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "status": "unknown",
            "cpu": {"usage_percent": 0, "status": "❓"},
            "memory": {"usage_percent": 0, "status": "❓"},
            "disk": {"usage_percent": 0, "status": "❓"}
        }
    
    def _get_fallback_network(self) -> Dict[str, Any]:
        return {
            "scan_status": "error",
            "total_devices": 0,
            "online_devices": 0,
            "device_types": {},
            "recent_devices": []
        }
    
    def _get_fallback_devices(self) -> Dict[str, Any]:
        return {
            "categories": {"mobile": 0, "computers": 0, "network": 0, "iot": 0, "other": 0},
            "total": 0
        }
    
    def _get_fallback_performance(self) -> Dict[str, Any]:
        return {
            "network_io": {"bytes_sent": 0, "bytes_recv": 0},
            "processes": 0
        }
    
    def _get_fallback_security(self) -> Dict[str, Any]:
        return {
            "scanner_status": "❓ Status Unknown",
            "security_level": "❓ Unknown"
        }
    
    def _get_emergency_fallback(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "system": self._get_fallback_system(),
            "network": self._get_fallback_network(),
            "devices": self._get_fallback_devices(),
            "performance": self._get_fallback_performance(),
            "security": self._get_fallback_security(),
            "error": "Dashboard service unavailable"
        }