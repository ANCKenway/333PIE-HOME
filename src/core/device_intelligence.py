"""
🧠 333HOME - Device Intelligence Engine

Moteur d'intelligence pour tracking et analyse des devices réseau.
Fusionne données multi-sources, détecte changements, calcule scores de confiance.

Références :
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 1
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

from src.core.logging_config import get_logger
from src.features.network.detector import ExtendedOUIDatabase

logger = get_logger(__name__)


# === ENUMS ===

class ChangeType(Enum):
    """Types de changements détectables"""
    IP_CHANGED = "ip_changed"
    HOSTNAME_CHANGED = "hostname_changed"
    STATUS_CHANGED = "status_changed"
    VENDOR_DETECTED = "vendor_detected"
    NEW_DEVICE = "new_device"
    DEVICE_DISAPPEARED = "device_disappeared"
    MAC_CONFLICT = "mac_conflict"
    IP_CONFLICT = "ip_conflict"


class ConflictType(Enum):
    """Types de conflits réseau"""
    IP_DUPLICATE = "ip_duplicate"          # Même IP sur 2+ MACs
    MAC_DUPLICATE = "mac_duplicate"        # Même MAC sur 2+ IPs (impossible normalement)
    MAC_SPOOFING = "mac_spoofing"          # MAC vendor != device type détecté


class DataQuality(Enum):
    """Qualité des données device"""
    HIGH = "high"        # Données de 3+ sources, récentes
    MEDIUM = "medium"    # Données de 2 sources ou anciennes
    LOW = "low"          # Données d'1 seule source, très anciennes


# === DATA CLASSES ===

@dataclass
class DeviceData:
    """
    Données brutes d'un device depuis une source
    """
    mac: str                        # Adresse MAC (clé primaire)
    source: str                     # Source des données (nmap, arp, freebox, etc.)
    timestamp: datetime             # Quand les données ont été collectées
    
    # Identité
    ip: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    
    # Statut
    is_online: bool = False
    response_time_ms: Optional[float] = None
    
    # Capacités
    open_ports: List[int] = None
    services: List[str] = None
    os_detected: Optional[str] = None
    os_confidence: float = 0.0
    
    # Métadonnées source
    scan_type: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []
        if self.services is None:
            self.services = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DeviceChange:
    """
    Changement détecté sur un device
    """
    change_type: ChangeType
    device_mac: str
    timestamp: datetime
    old_value: Any
    new_value: Any
    source: str                     # Source qui a détecté le changement
    confidence: float = 1.0         # Confiance dans le changement (0-1)
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class NetworkConflict:
    """
    Conflit réseau détecté
    """
    conflict_type: ConflictType
    severity: str                   # critical | warning | info
    detected_at: datetime
    description: str
    affected_devices: List[str]     # MACs concernées
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class UptimeStats:
    """
    Statistiques de disponibilité d'un device
    """
    total_time_seconds: int         # Temps total observé
    online_time_seconds: int        # Temps en ligne
    offline_time_seconds: int       # Temps hors ligne
    uptime_percentage: float        # % de disponibilité
    total_detections: int           # Nombre de scans où détecté
    total_scans: int                # Nombre total de scans
    detection_rate: float           # % de détection
    average_latency_ms: float       # Latence moyenne quand online
    first_seen: datetime            # Première détection
    last_seen: datetime             # Dernière détection
    longest_online_period: int      # Plus longue période en ligne (secondes)
    longest_offline_period: int     # Plus longue période hors ligne (secondes)


# === MAIN CLASS ===

class DeviceIntelligenceEngine:
    """
    Moteur d'intelligence pour analyse et fusion des données devices
    
    Responsabilités:
    - Fusionner données de multiples sources
    - Détecter changements significatifs
    - Calculer scores de confiance
    - Détecter conflits réseau
    - Calculer statistiques de disponibilité
    """
    
    def __init__(self):
        self.logger = logger
        self.oui_db = ExtendedOUIDatabase()  # 🔧 Base OUI locale pour enrichissement vendor
        self.confidence_weights = {
            'freebox': 1.0,     # Source de vérité (routeur)
            'nmap': 0.9,        # Très fiable
            'arp': 0.8,         # Fiable
            'mdns': 0.7,        # Assez fiable
            'netbios': 0.7,     # Assez fiable
            'tailscale': 0.9,   # Fiable (VPN)
            'snmp': 0.6,        # Dépend du device
            'manual': 1.0,      # Données manuelles = confiance max
        }
    
    def merge_device_data(
        self,
        sources: List[DeviceData],
        existing_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fusionne données de multiples sources pour un device
        
        Logique:
        - MAC address = clé primaire (unique, stable)
        - Priorité aux sources plus fiables (freebox > nmap > arp)
        - Garde l'historique des valeurs
        - Enrichit avec metadata
        
        Args:
            sources: Liste des données brutes par source
            existing_data: Données existantes du device (optionnel)
            
        Returns:
            Device unifié avec toutes les données fusionnées
        """
        if not sources:
            return existing_data or {}
        
        # Trier par poids de confiance (source la plus fiable en premier)
        sources_sorted = sorted(
            sources,
            key=lambda s: self.confidence_weights.get(s.source, 0.5),
            reverse=True
        )
        
        # Base: première source (la plus fiable)
        base = sources_sorted[0]
        mac = base.mac.upper()
        
        # Initialiser le device unifié
        unified = {
            'mac': mac,
            'sources': [s.source for s in sources],
            'last_updated': datetime.now().isoformat(),
            'data_sources_count': len(sources),
        }
        
        # Fusionner les champs avec priorité
        unified['ip'] = self._merge_field(sources_sorted, 'ip')
        unified['hostname'] = self._merge_field(sources_sorted, 'hostname')
        unified['vendor'] = self._merge_field(sources_sorted, 'vendor')
        unified['device_type'] = self._merge_field(sources_sorted, 'device_type')
        unified['os_detected'] = self._merge_field(sources_sorted, 'os_detected')
        
        # 🔧 ENRICHISSEMENT: Inférer OS si manquant
        if not unified['os_detected'] or unified['os_detected'] == 'Unknown':
            inferred_os = self._infer_os_from_context(unified)
            if inferred_os:
                unified['os_detected'] = inferred_os
                unified['os_inference_method'] = 'heuristic'
                self.logger.debug(f"🖥️  Inferred OS for {mac[:17]}: {inferred_os}")
        
        # 🔧 ENRICHISSEMENT: Si pas de vendor, lookup via MAC OUI
        if not unified['vendor'] or unified['vendor'] == 'Unknown':
            try:
                # 1. Essayer OUI database locale (rapide, pas de réseau)
                oui_info = self.oui_db.lookup(mac)
                if oui_info and oui_info.get('vendor'):
                    unified['vendor'] = oui_info['vendor']
                    unified['detection_method'] = 'local_oui'
                    if oui_info.get('device_type'):
                        unified['device_type'] = oui_info['device_type']
                    self.logger.debug(f"📍 Enriched vendor for {mac[:17]}: {unified['vendor']} (local OUI)")
            except Exception as e:
                self.logger.warning(f"Failed to enrich vendor for {mac}: {e}")
        
        # Status: online si AU MOINS une source dit online
        unified['is_online'] = any(s.is_online for s in sources)
        
        # Latence: moyenne des sources qui répondent
        latencies = [s.response_time_ms for s in sources if s.response_time_ms]
        unified['average_latency_ms'] = statistics.mean(latencies) if latencies else None
        
        # Ports ouverts: union de tous les ports détectés
        all_ports = set()
        for s in sources:
            if s.open_ports:
                all_ports.update(s.open_ports)
        unified['open_ports'] = sorted(list(all_ports))
        
        # Services: union de tous les services
        all_services = set()
        for s in sources:
            if s.services:
                all_services.update(s.services)
        unified['services'] = sorted(list(all_services))
        
        # Confiance OS: max des confidences
        os_confidences = [s.os_confidence for s in sources if s.os_confidence]
        unified['os_confidence'] = max(os_confidences) if os_confidences else 0.0
        
        # Calculer score de confiance global
        unified['confidence_score'] = self.calculate_confidence(unified, sources)
        unified['data_quality'] = self._determine_data_quality(unified, sources).value
        
        # Garder metadata de toutes les sources
        unified['sources_metadata'] = {
            s.source: {
                'timestamp': s.timestamp.isoformat(),
                'scan_type': s.scan_type,
                'metadata': s.metadata
            }
            for s in sources
        }
        
        # Si données existantes, fusionner historique
        if existing_data:
            unified = self._merge_with_history(unified, existing_data)
        
        return unified
    
    def _merge_field(self, sources: List[DeviceData], field: str) -> Any:
        """Fusionne un champ spécifique en priorisant les sources fiables"""
        for source in sources:
            value = getattr(source, field, None)
            if value and value not in ['Unknown', 'N/A', '', None]:
                return value
        return None
    
    def _infer_os_from_context(self, unified: Dict[str, Any]) -> Optional[str]:
        """
        Inférer l'OS depuis vendor, hostname, device_type
        
        Heuristiques:
        - Vendor Apple/iPhone → iOS/macOS
        - Vendor Microsoft/ASUS/MSI + hostname Windows → Windows
        - Vendor Samsung/Android → Android
        - Vendor Raspberry Pi → Linux
        - Hostname patterns (MacBook, DESKTOP-, etc.)
        """
        vendor = (unified.get('vendor') or '').lower()
        hostname = (unified.get('hostname') or '').lower()
        device_type = (unified.get('device_type') or '').lower()
        
        # Apple
        if 'apple' in vendor or 'iphone' in vendor or 'ipad' in vendor:
            if 'iphone' in device_type or 'ipad' in device_type:
                return 'iOS'
            if 'macbook' in hostname or 'imac' in hostname or 'mac' in hostname:
                return 'macOS'
            return 'iOS/macOS'
        
        # Android
        if 'android' in vendor or 'samsung' in vendor or 'xiaomi' in vendor or 'huawei' in vendor:
            return 'Android'
        
        # Windows (via hostname patterns)
        if 'desktop-' in hostname or 'win-' in hostname or hostname.startswith('pc-'):
            return 'Windows'
        
        # Windows (via vendor PC brands)
        windows_vendors = ['asus', 'msi', 'dell', 'hp', 'lenovo', 'microsoft']
        if any(v in vendor for v in windows_vendors):
            return 'Windows'
        
        # Linux embedded
        if 'raspberry' in vendor or 'espressif' in vendor or 'esp32' in vendor:
            return 'Linux Embedded'
        
        # Network devices
        if 'router' in device_type or 'freebox' in vendor or 'livebox' in vendor:
            return 'Linux/RouterOS'
        
        # Smart devices
        if 'tv' in device_type or 'smart' in device_type:
            return 'Android TV/Linux'
        
        # Default heuristic: Si pas d'info, supposer Linux/Unix
        return None  # Mieux vaut ne pas deviner
    
    def _merge_with_history(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fusionne avec l'historique existant
        
        - Garde first_seen
        - Met à jour last_seen
        - Incrémente compteurs
        """
        # Garder les timestamps d'origine
        current['first_seen'] = previous.get('first_seen', datetime.now().isoformat())
        current['last_seen'] = datetime.now().isoformat()
        
        # Incrémenter compteurs
        current['total_detections'] = previous.get('total_detections', 0) + 1
        
        # Garder historique IP si changement
        if current.get('ip') != previous.get('ip'):
            if 'ip_history' not in current:
                current['ip_history'] = previous.get('ip_history', [])
            current['ip_history'].append({
                'old_ip': previous.get('ip'),
                'new_ip': current.get('ip'),
                'changed_at': datetime.now().isoformat(),
                'detected_by': current.get('sources', ['unknown'])[0]
            })
        
        # Garder historique hostname si changement
        if current.get('hostname') != previous.get('hostname'):
            if 'hostname_history' not in current:
                current['hostname_history'] = previous.get('hostname_history', [])
            current['hostname_history'].append({
                'old_hostname': previous.get('hostname'),
                'new_hostname': current.get('hostname'),
                'changed_at': datetime.now().isoformat()
            })
        
        return current
    
    def detect_changes(
        self,
        previous: Dict[str, Any],
        current: Dict[str, Any]
    ) -> List[DeviceChange]:
        """
        Détecte les changements significatifs entre 2 états d'un device
        
        Args:
            previous: État précédent
            current: État actuel
            
        Returns:
            Liste des changements détectés
        """
        changes = []
        mac = current.get('mac')
        timestamp = datetime.now()
        source = current.get('sources', ['unknown'])[0]
        
        # Changement IP
        if previous.get('ip') != current.get('ip'):
            changes.append(DeviceChange(
                change_type=ChangeType.IP_CHANGED,
                device_mac=mac,
                timestamp=timestamp,
                old_value=previous.get('ip'),
                new_value=current.get('ip'),
                source=source,
                confidence=0.95
            ))
        
        # Changement hostname
        if previous.get('hostname') != current.get('hostname'):
            changes.append(DeviceChange(
                change_type=ChangeType.HOSTNAME_CHANGED,
                device_mac=mac,
                timestamp=timestamp,
                old_value=previous.get('hostname'),
                new_value=current.get('hostname'),
                source=source,
                confidence=0.90
            ))
        
        # Changement status (online/offline)
        if previous.get('is_online') != current.get('is_online'):
            change_type = (
                ChangeType.DEVICE_DISAPPEARED
                if not current.get('is_online')
                else ChangeType.NEW_DEVICE  # Réapparu
            )
            changes.append(DeviceChange(
                change_type=change_type,
                device_mac=mac,
                timestamp=timestamp,
                old_value=previous.get('is_online'),
                new_value=current.get('is_online'),
                source=source,
                confidence=1.0
            ))
        
        # Vendor détecté (si pas présent avant)
        if not previous.get('vendor') and current.get('vendor'):
            changes.append(DeviceChange(
                change_type=ChangeType.VENDOR_DETECTED,
                device_mac=mac,
                timestamp=timestamp,
                old_value=None,
                new_value=current.get('vendor'),
                source=source,
                confidence=0.85
            ))
        
        return changes
    
    def calculate_confidence(
        self,
        device: Dict[str, Any],
        sources: List[DeviceData]
    ) -> float:
        """
        Calcule un score de confiance pour les données d'un device
        
        Facteurs:
        - Nombre de sources (plus = mieux)
        - Fiabilité des sources (freebox > nmap > arp)
        - Fraîcheur des données (récent = mieux)
        - Cohérence entre sources
        
        Returns:
            Score entre 0.0 et 1.0
        """
        if not sources:
            return 0.0
        
        # 1. Score basé sur le nombre de sources (max 0.3)
        sources_score = min(len(sources) / 5, 1.0) * 0.3
        
        # 2. Score basé sur la fiabilité des sources (max 0.4)
        reliability_scores = [
            self.confidence_weights.get(s.source, 0.5)
            for s in sources
        ]
        reliability_score = statistics.mean(reliability_scores) * 0.4
        
        # 3. Score basé sur la fraîcheur (max 0.2)
        now = datetime.now()
        ages = [(now - s.timestamp).total_seconds() / 3600 for s in sources]  # heures
        avg_age_hours = statistics.mean(ages)
        freshness_score = max(0, 1 - (avg_age_hours / 24)) * 0.2  # Décroît sur 24h
        
        # 4. Score basé sur la cohérence (max 0.1)
        # Si IP cohérente entre sources = +0.1
        ips = [s.ip for s in sources if s.ip]
        consistency_score = 0.1 if len(set(ips)) <= 1 else 0.05
        
        total_score = sources_score + reliability_score + freshness_score + consistency_score
        
        return min(total_score, 1.0)
    
    def _determine_data_quality(
        self,
        device: Dict[str, Any],
        sources: List[DeviceData]
    ) -> DataQuality:
        """Détermine la qualité des données"""
        confidence = device.get('confidence_score', 0)
        
        if confidence >= 0.8:
            return DataQuality.HIGH
        elif confidence >= 0.5:
            return DataQuality.MEDIUM
        else:
            return DataQuality.LOW
    
    def detect_conflicts(
        self,
        devices: List[Dict[str, Any]]
    ) -> List[NetworkConflict]:
        """
        Détecte les conflits réseau
        
        Types de conflits:
        - IP duplicate: même IP sur plusieurs MACs
        - MAC spoofing: MAC vendor != device type
        
        Args:
            devices: Liste des devices unifiés
            
        Returns:
            Liste des conflits détectés
        """
        conflicts = []
        timestamp = datetime.now()
        
        # Grouper par IP pour détecter doublons
        ip_map: Dict[str, List[str]] = {}
        for device in devices:
            ip = device.get('ip')
            mac = device.get('mac')
            if ip and mac:
                if ip not in ip_map:
                    ip_map[ip] = []
                ip_map[ip].append(mac)
        
        # Détecter IP duplicates
        for ip, macs in ip_map.items():
            if len(macs) > 1:
                conflicts.append(NetworkConflict(
                    conflict_type=ConflictType.IP_DUPLICATE,
                    severity='critical',
                    detected_at=timestamp,
                    description=f"IP {ip} utilisée par {len(macs)} devices",
                    affected_devices=macs,
                    details={
                        'ip': ip,
                        'mac_addresses': macs,
                        'conflict_count': len(macs)
                    }
                ))
        
        # Détecter MAC spoofing potentiel
        for device in devices:
            vendor = (device.get('vendor') or '').lower()
            device_type = (device.get('device_type') or '').lower()
            mac = device.get('mac')
            
            # Exemple: vendor dit "Apple" mais device_type dit "Windows"
            suspicious_combinations = [
                ('apple', 'windows'),
                ('microsoft', 'mac'),
                ('cisco', 'windows'),
            ]
            
            for vendor_keyword, type_keyword in suspicious_combinations:
                if vendor_keyword in vendor and type_keyword in device_type:
                    conflicts.append(NetworkConflict(
                        conflict_type=ConflictType.MAC_SPOOFING,
                        severity='warning',
                        detected_at=timestamp,
                        description=f"Possible MAC spoofing: vendor={vendor} vs type={device_type}",
                        affected_devices=[mac],
                        details={
                            'mac': mac,
                            'vendor': vendor,
                            'device_type': device_type,
                            'suspicion_level': 'medium'
                        }
                    ))
        
        return conflicts
    
    def calculate_uptime(
        self,
        device_history: List[Dict[str, Any]]
    ) -> UptimeStats:
        """
        Calcule les statistiques de disponibilité d'un device
        
        Args:
            device_history: Historique des détections (scans)
            
        Returns:
            Statistiques de uptime
        """
        if not device_history:
            return UptimeStats(
                total_time_seconds=0,
                online_time_seconds=0,
                offline_time_seconds=0,
                uptime_percentage=0.0,
                total_detections=0,
                total_scans=0,
                detection_rate=0.0,
                average_latency_ms=0.0,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                longest_online_period=0,
                longest_offline_period=0
            )
        
        # Trier par timestamp
        sorted_history = sorted(
            device_history,
            key=lambda h: datetime.fromisoformat(h.get('timestamp', datetime.now().isoformat()))
        )
        
        first_seen = datetime.fromisoformat(sorted_history[0].get('timestamp'))
        last_seen = datetime.fromisoformat(sorted_history[-1].get('timestamp'))
        total_time = (last_seen - first_seen).total_seconds()
        
        # Calculer temps online/offline
        online_count = sum(1 for h in device_history if h.get('is_online'))
        total_scans = len(device_history)
        detection_rate = online_count / total_scans if total_scans > 0 else 0
        
        # Estimation temps online (approximation)
        online_time = total_time * detection_rate
        offline_time = total_time - online_time
        uptime_percentage = (online_time / total_time * 100) if total_time > 0 else 0
        
        # Latence moyenne (quand online)
        latencies = [
            h.get('latency_ms', 0)
            for h in device_history
            if h.get('is_online') and h.get('latency_ms')
        ]
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        
        # Calculer périodes (simplifié)
        online_periods = []
        offline_periods = []
        current_period_start = None
        current_is_online = None
        
        for entry in sorted_history:
            is_online = entry.get('is_online')
            timestamp = datetime.fromisoformat(entry.get('timestamp'))
            
            if current_is_online is None:
                # Première entrée
                current_is_online = is_online
                current_period_start = timestamp
            elif current_is_online != is_online:
                # Changement de statut
                duration = (timestamp - current_period_start).total_seconds()
                if current_is_online:
                    online_periods.append(duration)
                else:
                    offline_periods.append(duration)
                
                current_is_online = is_online
                current_period_start = timestamp
        
        # Ajouter dernière période
        if current_period_start:
            duration = (last_seen - current_period_start).total_seconds()
            if current_is_online:
                online_periods.append(duration)
            else:
                offline_periods.append(duration)
        
        longest_online = max(online_periods) if online_periods else 0
        longest_offline = max(offline_periods) if offline_periods else 0
        
        return UptimeStats(
            total_time_seconds=int(total_time),
            online_time_seconds=int(online_time),
            offline_time_seconds=int(offline_time),
            uptime_percentage=round(uptime_percentage, 2),
            total_detections=online_count,
            total_scans=total_scans,
            detection_rate=round(detection_rate, 3),
            average_latency_ms=round(avg_latency, 2),
            first_seen=first_seen,
            last_seen=last_seen,
            longest_online_period=int(longest_online),
            longest_offline_period=int(longest_offline)
        )
